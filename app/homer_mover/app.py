"""Homer 搬家程式：一個視窗由頭帶到尾。介面係 ui/index.html，呢度係俾介面叫嘅 Python 功能。"""
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import threading
import time
from pathlib import Path

from . import core, handoff
from .i18n import t, all_strings, lang

HERE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
UI = HERE / "homer_mover" / "ui" / "index.html"
ARCHIVE = HERE / "homer_mover" / "data" / "homer.tar.gz"


class Api:
    def __init__(self) -> None:
        self.window = None
        self.bin: Path | None = None
        self.since = 0.0
        self.files: dict[str, Path] = {}
        self._watching = False

    # ---- 推訊息去介面 ----
    def _emit(self, kind: str, **data) -> None:
        if self.window:
            self.window.evaluate_js(f"window.onEvent({json.dumps({'kind': kind, **data}, ensure_ascii=False)})")

    def _log(self, line: str) -> None:
        self._emit("log", line=line)

    def _bg(self, fn, *a) -> None:
        def wrap():
            try:
                fn(*a)
            except Exception as e:  # 任何錯都顯示俾用家睇，唔好靜靜雞死
                self._emit("error", message=str(e))
        threading.Thread(target=wrap, daemon=True).start()

    # ---- 狀態 ----
    def status(self) -> dict:
        h = core.check_hermes(self._log)
        self.bin = Path(h["path"]) if h.get("found") else None
        prof = core.profile_installed()
        provider = core.first_logged_in(self.bin, self._log) if (self.bin and h.get("ok")) else None
        if provider and prof:
            core.use_provider(self.bin, provider, self._log)  # 之前已經登入過：照樣設做預設
        elif prof and core.saved_api_key():
            provider = "key:" + core.saved_api_key()
        login = bool(provider)
        return {"hermes": h, "profile": prof, "login": login, "provider": provider,
                "suggest": core.suggest_provider(), "platform": sys.platform}

    # ---- 第 1 步 ----
    def install_hermes(self) -> None:
        self._bg(self._install_hermes)

    def _install_hermes(self) -> None:
        self._emit("progress", step=1, text=t("p_download"), pct=0)
        dest = core.download_setup(Path(tempfile.mkdtemp(prefix="homer-")),
                                   lambda f: self._emit("progress", step=1, text=t("p_download"), pct=round(f * 100)))
        core.open_file(dest)
        self._emit("progress", step=1, text=t("p_opened"), pct=100)
        for _ in range(720):  # 最多等 60 分鐘
            time.sleep(5)
            h = core.check_hermes()
            if h.get("found") and h.get("ok"):
                self.bin = Path(h["path"])
                self._emit("done", step=1, info=h)
                return
        self._emit("error", message=t("e_wait"))

    def update_hermes(self) -> None:
        def go():
            self._emit("progress", step=1, text=t("p_updating"), pct=None)
            r = core.update_hermes(self.bin, self._log)
            h = core.check_hermes(self._log)
            if h.get("ok"):
                self._emit("done", step=1, info=h)
            else:
                self._emit("error", message=t("e_update") + "\n" + r.out[-800:])
        self._bg(go)

    # ---- 第 2 步 ----
    def install_profile(self) -> None:
        def go():
            self._emit("progress", step=2, text=t("p_profile"), pct=None)
            r = core.install_profile(self.bin, ARCHIVE, self._log)
            if r.ok:
                self._emit("done", step=2)
            else:
                self._emit("error", message=t("e_profile") + "\n" + r.out[-800:])
        self._bg(go)

    # ---- 第 3 步 ----
    def ai_login(self, key: str) -> None:
        def go():
            self._emit("progress", step=3, text=t("p_login"), pct=None)
            r = core.login(self.bin, key, lambda url, code: self._emit("code", url=url, code=code), self._log)
            if r.ok and core.logged_in(self.bin, key, self._log):
                u = core.use_provider(self.bin, key, self._log)
                if not u.ok:
                    self._emit("error", message=t("e_login_set") + "\n" + u.out[-600:])
                    return
                self._emit("done", step=3, provider=key)
            else:
                self._emit("error", message=t("e_login") + "\n" + r.out[-600:])
        self._bg(go)

    def save_key(self, which: str, key: str) -> None:
        def go():
            self._emit("progress", step=3, text=t("p_login"), pct=None)
            r = core.save_api_key(self.bin, which, key, self._log)
            if r.ok:
                self._emit("done", step=3, provider="key:" + which)
            elif r.out == "bad key":
                self._emit("error", message=t("e_badkey"))
            else:
                self._emit("error", message=t("e_login_set") + "\n" + r.out[-600:])
        self._bg(go)

    def grok_login(self) -> None:  # 舊介面
        self.ai_login("grok")

    def strings(self) -> dict:
        return {"lang": lang(), **all_strings()}

    def open_url(self, url: str) -> None:
        import webbrowser
        webbrowser.open(url)

    # ---- 第 4 步 ----
    def prepare_move(self) -> None:
        def go():
            self._emit("progress", step=4, text=t("p_prepare"), pct=None)
            r = core.ensure_importer(self.bin, self._log)
            if not r.ok:
                self._emit("error", message=t("e_importer") + "\n" + r.out[-800:])
                return
            msg = handoff.combined_message(core.export_prompt(self.bin, self._log))
            self.since = time.time()
            self.files = {}
            self._emit("message", text=msg)
            self._watch()
        self._bg(go)

    def _watch(self) -> None:
        if self._watching:
            return
        self._watching = True
        try:
            got_export_at = 0.0
            for _ in range(1800):  # 最多 60 分鐘
                time.sleep(2)
                found = core.find_new_downloads(self.since)
                if found.keys() - self.files.keys():
                    self.files.update(found)
                    self._emit("files", files={k: v.name for k, v in self.files.items()})
                if "export" in self.files and not got_export_at:
                    got_export_at = time.time()
                # 有 export 之後，等 zip 最多 90 秒；有齊就即刻
                if got_export_at and ("handoff" in self.files or time.time() - got_export_at > 90):
                    self._preview()
                    return
        finally:
            self._watching = False

    def choose_file(self) -> None:
        import webview
        paths = self.window.create_file_dialog(webview.OPEN_DIALOG, allow_multiple=True,
                                               directory=str(core.downloads_dir())) or []
        for p in map(Path, paths):
            n = p.name.lower()
            if n.endswith(".zip"):
                self.files["handoff"] = p
            elif n.endswith((".json", ".txt", ".md")):
                self.files["export"] = p
        self._emit("files", files={k: v.name for k, v in self.files.items()})
        if "export" in self.files:
            self._bg(self._preview)

    def _preview(self) -> None:
        self._emit("progress", step=4, text=t("p_preview"), pct=None)
        r = core.preview_import(self.bin, self.files["export"], self._log)
        if not r.ok:
            self._emit("error", message=t("e_export") + "\n" + r.out[-800:])
            return
        zipinfo = handoff.check_zip(self.files["handoff"]) if "handoff" in self.files else None
        self._emit("preview", lines=core.summarize(r.out) or r.out.splitlines()[-8:],
                   bot=core.bot_name_from_export(self.files["export"]), zip=zipinfo and {
                       k: zipinfo[k] for k in ("ok", "problems", "skipped", "files")})

    def do_move(self, bot: str) -> None:
        def go():
            bot_name = handoff.safe_folder_name(bot)
            self._emit("progress", step=4, text=t("p_import"), pct=None)
            r = core.do_import(self.bin, self.files["export"], self._log)
            if not r.ok:
                self._emit("error", message=t("e_import") + "\n" + r.out[-800:])
                return
            result = {"bot": bot_name, "imported": core.summarize(r.out), "folder": None, "items": [], "memory": False}
            z = self.files.get("handoff")
            if z:
                info = handoff.check_zip(z)
                if info["ok"]:
                    self._emit("progress", step=4, text=t("p_files"), pct=None)
                    folder = handoff.extract(z, bot_name, info)
                    md = handoff.find_handoff_md(folder)
                    items = handoff.open_items(md.read_text(encoding="utf-8", errors="replace")) if md else []
                    result.update(folder=str(folder), items=items, files=info["files"], skipped=info["skipped"],
                                  memory=handoff.add_memory(bot_name, folder, items))
                    handoff.archive_zip(z, bot_name)
                else:
                    result["zip_problems"] = info["problems"]
            exp = self.files["export"]
            exp.rename(exp.with_name(f"grok-bot-export-{bot_name}-搬咗{exp.suffix}"))
            self.files = {}
            self._emit("moved", result=result)
        self._bg(go)

    def copy(self, text: str) -> bool:
        try:
            if sys.platform == "darwin":
                subprocess.run(["pbcopy"], input=text.encode("utf-8"), check=True,
                               env=dict(os.environ, LANG="en_US.UTF-8"))
            elif sys.platform == "win32":
                # 經 UTF-8 暫存檔，免得中文喺 PowerShell 變亂碼
                f = Path(tempfile.gettempdir()) / "homer-clip.txt"
                f.write_text(text, encoding="utf-8")
                subprocess.run(["powershell", "-NoProfile", "-Command",
                                f"Get-Content -Raw -Encoding UTF8 '{f}' | Set-Clipboard"], check=True,
                               creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
                f.unlink(missing_ok=True)
            else:
                return False
            return True
        except Exception:
            return False

    def open_grok_bot(self) -> None:
        if sys.platform == "darwin":
            subprocess.Popen(["open", "-a", "Grok Bot"])
        elif sys.platform == "win32":
            la = Path(os.environ.get("LOCALAPPDATA", ""))
            for p in [la / "Programs" / "Grok Bot" / "Grok Bot.exe", la / "Programs" / "grok-bot" / "Grok Bot.exe"]:
                if p.is_file():
                    os.startfile(str(p))  # type: ignore[attr-defined]
                    return

    def open_folder(self, path: str) -> None:
        core.open_file(Path(path))

    def finish(self) -> None:
        core.open_hermes_app(self.bin)


def main() -> None:
    import webview
    api = Api()
    api.window = webview.create_window(t("window_title"), str(UI), js_api=api,
                                       width=760, height=860, min_size=(420, 600), background_color="#0f1218")
    webview.start()


if __name__ == "__main__":
    main()
