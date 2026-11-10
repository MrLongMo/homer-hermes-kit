"""交接包（grok-bot-handoff.zip）：先檢查、再解壓、再加一條記憶。"""
from __future__ import annotations

import re
import zipfile
from pathlib import Path, PurePosixPath

from . import core

MAX_TOTAL = 300 * 1024 * 1024
MAX_FILES = 5000
SECRET_NAME = re.compile(
    r"(^|/)(\.env(\..*)?|id_rsa[^/]*|id_ed25519[^/]*|[^/]*\.pem|[^/]*\.key|[^/]*\.p12|[^/]*\.pfx|"
    r"[^/]*cookie[^/]*|[^/]*token[^/]*|[^/]*credential[^/]*|[^/]*password[^/]*|[^/]*secret[^/]*|"
    r"auth\.json|\.netrc|\.npmrc|\.pypirc)$",
    re.I,
)
MEMORY_DELIM = "\n§\n"
MEMORY_LIMIT = 2200

HANDOFF_ZH = """做完上面之後，請再幫我準備一個交接包。同樣不要修改、刪除或寄出任何東西，也不要開始任何新工作。

1. 寫一份 HANDOFF.md，用我平常跟你聊天的語言，內容包括：
   - 你的角色（一句話）
   - 我們討論過的主要事項：每項寫日期（如果知道）和決定了什麼
   - 還沒完成的工作：每項寫進度、下一步、正在等我核准的事
   - 你定期在做的事，以及會用到哪些檔案
   - 你知道的我的偏好和習慣
   - 檔案清單：每個檔案用一句話說明用途
   不要寫任何密碼、API key、token、銀行或信用卡號碼。

2. 把 HANDOFF.md 和你幫我做過或工作會用到的檔案（報告、表格、草稿、腳本、筆記）壓縮成一個 grok-bot-handoff.zip。
   - 不要包含：密碼、API key、token、cookie、.env、瀏覽器登入資料、任何登入憑證。
   - 單一檔案超過 20MB 就不要放，改在 HANDOFF.md 列出。
   - 整個 zip 盡量小於 100MB。

3. 把 grok-bot-export.json 和 grok-bot-handoff.zip 兩個檔案都傳給我下載。"""


HANDOFF_EN = """When you've done that, please also prepare a handoff package. Again: don't change, delete or send anything, and don't start any new work.

1. Write HANDOFF.md in the language we usually chat in, with:
   - your role (one line)
   - the main things we've discussed: for each, the date if you know it and what we decided
   - open work: for each, how far it got, the next step, and anything waiting for my approval
   - what you do on a schedule, and which files it uses
   - my preferences and habits that you know
   - a file list: one line per file saying what it is for
   Don't include passwords, API keys, tokens, or bank or card numbers.

2. Zip HANDOFF.md together with the files you made for me or use in your work (reports, sheets, drafts, scripts, notes) into grok-bot-handoff.zip.
   - Leave out passwords, API keys, tokens, cookies, .env files, browser logins and any credentials.
   - Leave out any single file over 20 MB and list it in HANDOFF.md.
   - Keep the whole zip under about 100 MB.

3. Send me both grok-bot-export.json and grok-bot-handoff.zip to download."""


def combined_message(official: str) -> str:
    from .i18n import lang
    return official.strip() + "\n\n---\n\n" + (HANDOFF_EN if lang() == "en" else HANDOFF_ZH)


def check_zip(path: Path) -> dict:
    """唔解壓，淨係睇：有冇危險路徑、似登入資料嘅檔、有冇 HANDOFF.md、大細。"""
    problems: list[str] = []
    skipped: list[str] = []
    names: list[str] = []
    total = 0
    try:
        zf = zipfile.ZipFile(path)
    except (zipfile.BadZipFile, OSError) as e:
        return {"ok": False, "problems": [f"唔係有效嘅 zip：{e}"], "skipped": [], "files": 0, "has_handoff": False}
    with zf:
        infos = zf.infolist()
        if len(infos) > MAX_FILES:
            problems.append(f"檔案太多（{len(infos)} 個）")
        for i in infos:
            n = i.filename.replace("\\", "/")
            pp = PurePosixPath(n)
            if n.startswith("/") or re.match(r"^[A-Za-z]:", n) or ".." in pp.parts:
                problems.append(f"危險路徑：{n}")
                continue
            if (i.external_attr >> 16) & 0o170000 == 0o120000:
                problems.append(f"捷徑檔（symlink）：{n}")
                continue
            if i.is_dir():
                continue
            if SECRET_NAME.search(n):
                skipped.append(n)
                continue
            total += i.file_size
            names.append(n)
        if total > MAX_TOTAL:
            problems.append(f"解壓後太大（{total // (1024 * 1024)}MB）")
    has = any(PurePosixPath(n).name.lower() == "handoff.md" for n in names)
    if not has:
        problems.append("入面冇 HANDOFF.md")
    return {"ok": not problems, "problems": problems, "skipped": skipped, "files": len(names),
            "has_handoff": has, "names": names}


def safe_folder_name(name: str) -> str:
    s = re.sub(r'[\\/:*?"<>|\x00-\x1f]', "", name).strip(" .")
    return s[:60] or "我的 Bot"


def extract(path: Path, bot: str, report: dict) -> Path:
    dest = core.handoff_home() / safe_folder_name(bot)
    dest.mkdir(parents=True, exist_ok=True)
    root = dest.resolve()
    with zipfile.ZipFile(path) as zf:
        for n in report["names"]:
            target = (dest / n).resolve()
            if root not in target.parents and target != root:
                continue
            if target.exists():
                continue  # 唔覆蓋
            target.parent.mkdir(parents=True, exist_ok=True)
            with zf.open(n) as src, open(target, "wb") as out:
                while chunk := src.read(1 << 16):
                    out.write(chunk)
    return dest


def find_handoff_md(folder: Path) -> Path | None:
    for p in sorted(folder.rglob("*")):
        if p.is_file() and p.name.lower() == "handoff.md":
            return p
    return None


def open_items(md: str, limit: int = 3) -> list[str]:
    """由 HANDOFF.md 抽「未完成」嗰段頭幾項。"""
    lines = md.splitlines()
    out: list[str] = []
    grab = False
    for line in lines:
        t = line.strip()
        if re.search(r"(未完成|open work|open tasks|pending|進行中)", t, re.I) and len(t) < 60:
            grab = True
            continue
        if grab:
            if t.startswith("#") or (re.search(r"(定期|schedule|偏好|preference|檔案清單|file list)", t, re.I) and len(t) < 60):
                break
            m = re.match(r"^([-*•]|\d+[.)])\s+(.*)", t)
            if m:
                out.append(m.group(2)[:80])
                if len(out) >= limit:
                    break
    return out


def add_memory(bot: str, folder: Path, items: list[str]) -> bool:
    mem = core.profile_dir() / "memories" / "MEMORY.md"
    mem.parent.mkdir(parents=True, exist_ok=True)
    from .i18n import lang
    en = lang() == "en"
    entry = (f"Moved from Grok Bot “{bot}”. Handoff and files are in {folder}; read HANDOFF.md before related work."
             if en else f"從 Grok Bot「{bot}」搬過來。交接和檔案在 {folder}，處理相關事情前先讀 HANDOFF.md。")
    if items:
        entry += (" Open: " + "; ".join(items)) if en else (" 還沒完成：" + "；".join(items))
    old = mem.read_text(encoding="utf-8") if mem.exists() else ""
    if entry in old:
        return True
    new = (old.rstrip("\n") + MEMORY_DELIM + entry) if old.strip() else entry
    if len(new) > MEMORY_LIMIT:
        entry = (f"Moved from Grok Bot “{bot}”; handoff in {folder}/HANDOFF.md." if en
                 else f"從 Grok Bot「{bot}」搬過來。交接和檔案在 {folder}，先讀 HANDOFF.md。")
        new = (old.rstrip("\n") + MEMORY_DELIM + entry) if old.strip() else entry
        if len(new) > MEMORY_LIMIT:
            return False
    mem.write_text(new + "\n", encoding="utf-8")
    return True


def archive_zip(path: Path, bot: str) -> Path:
    target = path.with_name(f"grok-bot-handoff-{safe_folder_name(bot)}.zip")
    i = 2
    while target.exists():
        target = path.with_name(f"grok-bot-handoff-{safe_folder_name(bot)}-{i}.zip")
        i += 1
    path.rename(target)
    return target
