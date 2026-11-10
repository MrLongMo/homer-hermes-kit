"""Homer 搬家程式嘅後台：搵 Hermes、安裝、裝 Homer 設定、Grok 登入、搬 Grok Bot。

全部經官方 `hermes` 指令做嘢，唔直接改 Hermes 內部檔案（除咗加一條記憶）。
冇 GUI，可以單獨測試：測試時用 HOMER_HERMES_BIN 指去假 hermes，HERMES_HOME 指去暫存資料夾。
"""
from __future__ import annotations

import os
import re
import shutil
import subprocess
import sys
import time
import urllib.request
import webbrowser
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, Iterable

PROFILE = "homer"
MIN_VERSION = (0, 22, 6)
SETUP_URLS = {
    "darwin": "https://hermes-assets.nousresearch.com/Hermes-Setup.dmg",
    "win32": "https://hermes-assets.nousresearch.com/Hermes-Setup.exe",
}
IS_WIN = sys.platform == "win32"
Log = Callable[[str], None]


def _noop(_: str) -> None:
    pass


# ---------- 位置 ----------

def hermes_root() -> Path:
    """Hermes 資料夾：HERMES_HOME → Windows %LOCALAPPDATA%\\hermes → ~/.hermes（同官方一樣）。"""
    env = os.environ.get("HERMES_HOME", "").strip()
    if env:
        return Path(os.path.expandvars(os.path.expanduser(env)))
    if IS_WIN:
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / "hermes"
    return Path.home() / ".hermes"


def profile_dir(name: str = PROFILE) -> Path:
    return hermes_root() / "profiles" / name


def downloads_dir() -> Path:
    return Path.home() / "Downloads"


def handoff_home() -> Path:
    return Path.home() / "Documents" / "Grok Bot 搬家"


def candidate_bins() -> list[Path]:
    home = Path.home()
    c: list[Path] = []
    if IS_WIN:
        la = Path(os.environ.get("LOCALAPPDATA") or home / "AppData" / "Local")
        c += [la / "hermes" / "bin" / "hermes.exe", la / "Microsoft" / "WindowsApps" / "hermes.exe"]
    else:
        c += [home / ".local" / "bin" / "hermes", home / ".hermes" / "bin" / "hermes",
              home / ".hermes" / "hermes-agent" / "venv" / "bin" / "hermes",
              Path("/opt/homebrew/bin/hermes"), Path("/usr/local/bin/hermes")]
        app = Path("/Applications/Hermes.app/Contents")
        if app.is_dir():
            c += sorted(p for p in app.rglob("hermes") if p.is_file() and os.access(p, os.X_OK))
    return c


def find_hermes() -> Path | None:
    forced = os.environ.get("HOMER_HERMES_BIN")
    if forced:
        return Path(forced)
    which = shutil.which("hermes")
    if which:
        return Path(which)
    for p in candidate_bins():
        if p.is_file():
            return p
    return None


def parse_version(text: str) -> tuple[int, int, int] | None:
    m = re.search(r"(\d+)\.(\d+)\.(\d+)", text or "")
    return tuple(int(x) for x in m.groups()) if m else None  # type: ignore[return-value]


# ---------- 行指令 ----------

@dataclass
class Result:
    code: int
    out: str

    @property
    def ok(self) -> bool:
        return self.code == 0


def _cmd(bin_: Path, args: Iterable[str]) -> list[str]:
    b = str(bin_)
    # 測試用假 hermes 係 .py：用而家個 Python 行
    if b.endswith(".py"):
        return [sys.executable, b, *args]
    return [b, *args]


def run(bin_: Path, args: Iterable[str], *, stdin: str | None = None, timeout: float = 900,
        log: Log = _noop) -> Result:
    cmd = _cmd(bin_, args)
    log("$ hermes " + " ".join(cmd[2 if cmd[0] == sys.executable else 1:]))
    env = dict(os.environ, NO_COLOR="1", TERM="dumb", PYTHONIOENCODING="utf-8")
    try:
        p = subprocess.run(cmd, input=stdin, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=timeout, env=env,
                           creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    except subprocess.TimeoutExpired:
        return Result(124, "（等太耐，停咗）")
    except OSError as e:
        return Result(127, str(e))
    out = (p.stdout or "") + (("\n" + p.stderr) if p.stderr else "")
    out = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", out)  # 去顏色碼
    return Result(p.returncode, out.strip())


# ---------- 第 1 步：Hermes ----------

def check_hermes(log: Log = _noop) -> dict:
    b = find_hermes()
    if not b:
        return {"found": False}
    r = run(b, ["--version"], timeout=60, log=log)
    v = parse_version(r.out)
    return {"found": True, "path": str(b), "version": ".".join(map(str, v)) if v else None,
            "ok": bool(v and v >= MIN_VERSION)}


def download_setup(dest_dir: Path, progress: Callable[[float], None] = lambda f: None) -> Path:
    url = SETUP_URLS.get("win32" if IS_WIN else sys.platform)
    if not url:
        raise RuntimeError("呢部電腦唔支援（只支援 Mac 同 Windows）")
    dest = dest_dir / url.rsplit("/", 1)[1]
    req = urllib.request.Request(url, headers={"User-Agent": "HomerMover/0.1"})
    with urllib.request.urlopen(req, timeout=60) as r, open(dest, "wb") as f:
        total = int(r.headers.get("Content-Length") or 0)
        got = 0
        while chunk := r.read(1 << 16):
            f.write(chunk)
            got += len(chunk)
            if total:
                progress(got / total)
    return dest


def open_file(path: Path) -> None:
    if IS_WIN:
        os.startfile(str(path))  # type: ignore[attr-defined]
    else:
        subprocess.Popen(["open", str(path)])


def update_hermes(bin_: Path, log: Log = _noop) -> Result:
    return run(bin_, ["update"], stdin="y\n", timeout=1800, log=log)


# ---------- 第 2 步：Homer 設定 ----------

def profile_installed() -> bool:
    d = profile_dir()
    return d.is_dir() and any((d / f).exists() for f in ("config.yaml", "SOUL.md"))


def _kit_version(text: str) -> tuple[int, ...]:
    m = re.search(r"^version:\s*([\d.]+)", text or "", re.M)
    return tuple(int(x) for x in m.group(1).split(".")) if m else (0,)


def update_profile_files(archive: Path, log: Log = _noop) -> bool:
    """已經裝過舊版：只換 SOUL.md、技能同 distribution.yaml。唔郁 config.yaml（AI 設定）、記憶、對話。"""
    import tarfile
    d = profile_dir()
    cur = (d / "distribution.yaml").read_text(encoding="utf-8") if (d / "distribution.yaml").exists() else ""
    with tarfile.open(archive) as t:
        new = t.extractfile("homer/distribution.yaml").read().decode("utf-8")
        if _kit_version(new) <= _kit_version(cur):
            return False
        for m in t.getmembers():
            rel = m.name.split("/", 1)[1] if "/" in m.name else ""
            if not m.isfile() or not (rel in ("SOUL.md", "distribution.yaml") or rel.startswith("skills/")):
                continue
            if ".." in rel.split("/"):
                continue
            dest = d / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(t.extractfile(m).read())
    log(f"更新咗 Homer 設定（技能同 SOUL）到 {'.'.join(map(str, _kit_version(new)))}")
    return True


def install_profile(bin_: Path, archive: Path, log: Log = _noop) -> Result:
    if profile_installed():
        log("已經有 homer 設定，跳過匯入。")
        update_profile_files(archive, log)
        r = Result(0, "already")
    else:
        r = run(bin_, ["profile", "import", str(archive)], timeout=300, log=log)
        if not r.ok:
            return r
    u = run(bin_, ["profile", "use", PROFILE], timeout=60, log=log)
    return u if not u.ok else r


# ---------- 第 3 步：揀 AI（用本身有嘅帳號喺瀏覽器登入，唔使抄金鑰） ----------

LOGGED_IN = re.compile(r"(logged in|signed in|authenticated|active|valid|✓)", re.I)
LOGGED_OUT = re.compile(r"(not logged|not signed|no credential|logged out|none|expired|missing)", re.I)
URL_RE = re.compile(r"https://\S+")
CODE_RE = re.compile(r"\b([A-Z0-9]{4}-[A-Z0-9]{4}|[A-Z0-9]{6,9})\b")

# 官方 `hermes auth` 支援嘅瀏覽器登入。settings＝登入成功後幫 homer 設定嘅嘢。
# 只有 Grok 寫死預設模型（官方文件寫明 grok-4.6）；其他交返 Hermes 揀佢自己嘅預設。
# 轉去其他 AI 時清走 Grok 專用設定（舊版寫死過），空值＝交返 Hermes 用預設
_CLEAR_GROK = [("model.default", ""), ("model.base_url", ""), ("image_gen.provider", "")]

PROVIDERS: dict[str, dict] = {
    "grok": {"slug": "xai-oauth", "add": ["auth", "add", "xai-oauth", "--no-browser"],
             "settings": [("model.provider", "xai-oauth"), ("model.default", "grok-4.6"),
                          ("model.base_url", "https://api.x.ai/v1"), ("image_gen.provider", "xai")]},
    "chatgpt": {"slug": "openai-codex", "add": ["auth", "add", "openai-codex", "--type", "oauth"],
                "settings": [("model.provider", "openai-codex")] + _CLEAR_GROK},
    "nous": {"slug": "nous", "add": ["auth", "add", "nous", "--type", "oauth"],
             "settings": [("model.provider", "nous")] + _CLEAR_GROK},
    "minimax": {"slug": "minimax-oauth", "add": ["auth", "add", "minimax-oauth"],
                "settings": [("model.provider", "minimax-oauth")] + _CLEAR_GROK},
    "openrouter": {"slug": "openrouter", "add": ["auth", "add", "openrouter", "--type", "oauth"],
                   "settings": [("model.provider", "openrouter")] + _CLEAR_GROK},
}
GROK_SETTINGS = PROVIDERS["grok"]["settings"]


# 「我有 API 金鑰」：官方做法係寫入 profile 自己嘅 .env（見 Hermes profiles 文件）
API_KEY_PROVIDERS: dict[str, tuple[str, str]] = {   # 介面代號: (Hermes provider, .env 名)
    "deepseek": ("deepseek", "DEEPSEEK_API_KEY"),
    "gemini": ("gemini", "GEMINI_API_KEY"),
    "openai": ("openai-api", "OPENAI_API_KEY"),
    "openrouter": ("openrouter", "OPENROUTER_API_KEY"),
    "xai": ("xai", "XAI_API_KEY"),
    "anthropic": ("anthropic", "ANTHROPIC_API_KEY"),   # Claude API 金鑰（按用量收費），唔係月費帳號
}
KEY_RE = re.compile(r"^[A-Za-z0-9._\-:]{16,300}$")


def save_api_key(bin_: Path, which: str, key: str, log: Log = _noop) -> Result:
    """將金鑰寫入 homer 嘅 .env（只限擁有者讀寫），再將傾偈設做嗰間 AI。金鑰唔會寫入紀錄。"""
    key = (key or "").strip()
    if which not in API_KEY_PROVIDERS:
        return Result(2, "unknown provider")
    if not KEY_RE.match(key):
        return Result(2, "bad key")
    slug, env_name = API_KEY_PROVIDERS[which]
    env = profile_dir() / ".env"
    env.parent.mkdir(parents=True, exist_ok=True)
    lines = env.read_text(encoding="utf-8").splitlines() if env.exists() else []
    lines = [l for l in lines if not l.startswith(env_name + "=")] + [f"{env_name}={key}"]
    env.write_text("\n".join(lines) + "\n", encoding="utf-8")
    try:
        os.chmod(env, 0o600)
    except OSError:
        pass
    log(f"已寫入 {env_name}（金鑰唔顯示）")
    for k, v in [("model.provider", slug)] + _CLEAR_GROK:
        r = run(bin_, ["-p", PROFILE, "config", "set", k, v], timeout=60, log=log)
        if not r.ok:
            return r
    return Result(0, "ok")


def saved_api_key() -> str | None:
    """homer 嘅 .env 有冇已經寫咗金鑰（有就當揀咗 AI）。"""
    env = profile_dir() / ".env"
    if not env.exists():
        return None
    text = env.read_text(encoding="utf-8")
    for which, (_, name) in API_KEY_PROVIDERS.items():
        if any(l.startswith(name + "=") and len(l) > len(name) + 1 for l in text.splitlines()):
            return which
    return None


def logged_in(bin_: Path, key: str, log: Log = _noop) -> bool:
    r = run(bin_, ["auth", "status", PROVIDERS[key]["slug"]], timeout=60, log=log)
    if not r.ok or LOGGED_OUT.search(r.out):
        return False
    return bool(LOGGED_IN.search(r.out))


def first_logged_in(bin_: Path, log: Log = _noop) -> str | None:
    for key in PROVIDERS:
        if logged_in(bin_, key, log):
            return key
    return None


def suggest_provider(apps: Path = Path("/Applications")) -> str:
    """部機有用 Codex（ChatGPT）就推 ChatGPT；有 Grok Bot app 就推 Grok；否則推免費嘅 Nous Portal。"""
    home = Path.home()
    if (home / ".codex").is_dir():
        return "chatgpt"
    if (apps / "Grok Bot.app").is_dir() or (home / "AppData" / "Local" / "Programs" / "Grok Bot").is_dir():
        return "grok"
    return "nous"


def login(bin_: Path, key: str, on_code: Callable[[str, str], None], log: Log = _noop,
          timeout: float = 900) -> Result:
    """行官方瀏覽器登入：讀出網址同登入碼交俾介面顯示，再自己開瀏覽器。"""
    args = PROVIDERS[key]["add"]
    cmd = _cmd(bin_, args)
    log("$ hermes " + " ".join(args))
    env = dict(os.environ, NO_COLOR="1", TERM="dumb", PYTHONIOENCODING="utf-8")
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                         text=True, encoding="utf-8", errors="replace", env=env,
                         creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    lines: list[str] = []
    url = code = ""
    shown = False
    start = time.time()
    assert p.stdout
    for line in p.stdout:
        line = re.sub(r"\x1b\[[0-9;?]*[A-Za-z]", "", line).rstrip()
        lines.append(line)
        log(line)
        if not url and (m := URL_RE.search(line)):
            url = m.group(0).rstrip(".,)")
        if not code and ("code" in line.lower() or "碼" in line) and (m := CODE_RE.search(line.split(":")[-1])):
            code = m.group(1)
        if url and not shown and (code or "user_code" in url or "code=" in url):
            shown = True
            on_code(url, code)
            try:
                webbrowser.open(url)
            except Exception:
                pass
        if time.time() - start > timeout:
            p.kill()
            p.stdout.close()
            return Result(124, "\n".join(lines))
    p.wait()
    p.stdout.close()
    if url and not shown:
        on_code(url, code)  # 有啲登入（例如 OpenRouter）自己開瀏覽器，冇登入碼
    return Result(p.returncode or 0, "\n".join(lines))


def use_provider(bin_: Path, key: str, log: Log = _noop) -> Result:
    """登入成功先將 homer 嘅傾偈設做嗰間 AI（冇登入就唔郁，免得 Hermes 開箱出錯）。"""
    for k, v in PROVIDERS[key]["settings"]:
        r = run(bin_, ["-p", PROFILE, "config", "set", k, v], timeout=60, log=log)
        if not r.ok:
            return r
    return Result(0, "ok")


# 舊名（測試同舊介面用）
def grok_logged_in(bin_: Path, log: Log = _noop) -> bool:
    return logged_in(bin_, "grok", log)


def grok_login(bin_: Path, on_code: Callable[[str, str], None], log: Log = _noop, timeout: float = 900) -> Result:
    return login(bin_, "grok", on_code, log, timeout)


def use_grok(bin_: Path, log: Log = _noop) -> Result:
    return use_provider(bin_, "grok", log)


# ---------- 第 4 步：搬 Grok Bot ----------

def ensure_importer(bin_: Path, log: Log = _noop) -> Result:
    lst = run(bin_, ["-p", PROFILE, "plugins", "list"], timeout=120, log=log)
    if lst.ok and "agent-importers" in lst.out:
        return Result(0, "already")
    return run(bin_, ["-p", PROFILE, "plugins", "install", "agent-importers"], stdin="y\ny\ny\n",
               timeout=600, log=log)


def export_prompt(bin_: Path, log: Log = _noop) -> str:
    """攞官方匯出訊息。未有匯出檔時，`import-agent grok-bot` 會印出嚟，亦會存去 grok-bot-import/export-prompt.txt。"""
    f = profile_dir() / "grok-bot-import" / "export-prompt.txt"
    if f.is_file():
        return f.read_text(encoding="utf-8").strip()
    # 唔加 -y：就算下載項目有舊匯出檔，佢都只會停喺預覽，唔會搬
    r = run(bin_, ["-p", PROFILE, "import-agent", "grok-bot"], stdin="n\n", timeout=300, log=log)
    if f.is_file():
        return f.read_text(encoding="utf-8").strip()
    blocks = [b.strip() for b in re.split(r"\n\s*\n", r.out) if len(b.strip()) > 200]
    if blocks:
        return max(blocks, key=len)
    raise RuntimeError("攞唔到官方匯出訊息：\n" + r.out[-1500:])


def find_new_downloads(since: float, folder: Path | None = None) -> dict:
    """搵「下載項目」入面喺 since 之後出現嘅 Grok Bot 檔案。"""
    folder = folder or downloads_dir()
    found: dict[str, Path] = {}
    if not folder.is_dir():
        return found
    for p in folder.iterdir():
        try:
            if not p.is_file() or p.stat().st_mtime < since - 2:
                continue
        except OSError:
            continue
        n = p.name.lower()
        if n.endswith((".crdownload", ".part", ".download", ".tmp")):
            continue
        if n.startswith("grok-bot-export") and n.endswith((".json", ".txt", ".md")):
            if "export" not in found or p.stat().st_mtime > found["export"].stat().st_mtime:
                found["export"] = p
        elif n.startswith("grok-bot-handoff") and n.endswith(".zip"):
            if "handoff" not in found or p.stat().st_mtime > found["handoff"].stat().st_mtime:
                found["handoff"] = p
    return found


def preview_import(bin_: Path, export: Path, log: Log = _noop) -> Result:
    return run(bin_, ["-p", PROFILE, "import-agent", "grok-bot", "--source", str(export), "--dry-run"],
               timeout=300, log=log)


def do_import(bin_: Path, export: Path, log: Log = _noop) -> Result:
    return run(bin_, ["-p", PROFILE, "import-agent", "grok-bot", "--source", str(export), "-y"],
               timeout=900, log=log)


def summarize(out: str) -> list[str]:
    """將預覽輸出縮做幾行人睇得明嘅重點（數字行優先）。"""
    keep = []
    for line in out.splitlines():
        s = line.strip(" •-*│|")
        if not s or s.startswith("$"):
            continue
        if re.search(r"\d", s) and re.search(r"(skill|memor|routine|cron|soul|role|fact|技能|記憶|例行)", s, re.I):
            keep.append(s)
    return keep[:8]


def bot_name_from_export(export: Path) -> str:
    import json
    try:
        data = json.loads(export.read_text(encoding="utf-8"))
    except Exception:
        return ""
    for obj in ([data] + (data.get("bots") or [] if isinstance(data, dict) else [])):
        if isinstance(obj, dict):
            for k in ("name", "bot_name", "botName", "title"):
                v = obj.get(k)
                if isinstance(v, str) and v.strip():
                    return v.strip()[:60]
    return ""


def open_hermes_app(bin_: Path | None) -> None:
    if not IS_WIN and Path("/Applications/Hermes.app").is_dir():
        subprocess.Popen(["open", "-a", "Hermes"])
    elif bin_:
        subprocess.Popen(_cmd(bin_, ["desktop"]), creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
