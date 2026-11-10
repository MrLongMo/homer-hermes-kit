"""行法：cd app && python3 -m pytest -q tests  （或者 python3 -m unittest discover tests）"""
import json
import os
import sys
import tempfile
import time
import unittest
import zipfile
from pathlib import Path

APP = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(APP))
FAKE = APP / "tests" / "fake_hermes.py"
ARCHIVE = APP / "homer_mover" / "data" / "homer.tar.gz"


class MoverTest(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.env_backup = dict(os.environ)
        os.environ["HERMES_HOME"] = str(self.tmp / "hermes")
        os.environ["HOMER_HERMES_BIN"] = str(FAKE)
        os.environ["HOME"] = str(self.tmp / "home")
        os.environ["USERPROFILE"] = str(self.tmp / "home")  # Windows 用呢個做 home
        os.environ.pop("FAKE_VERSION", None)
        (self.tmp / "home" / "Downloads").mkdir(parents=True)
        from homer_mover import core, handoff
        self.core, self.handoff = core, handoff
        self.bin = core.find_hermes()

    def tearDown(self):
        os.environ.clear()
        os.environ.update(self.env_backup)

    def calls(self):
        return json.loads((self.tmp / "hermes" / "_fake.json").read_text())["calls"]

    def test_kit_has_no_hardcoded_model(self):
        import tarfile
        with tarfile.open(ARCHIVE) as t:
            cfg = t.extractfile("homer/config.yaml").read().decode()
        self.assertNotIn("xai-oauth", cfg)
        self.assertIn("zh-hant", cfg)

    def test_version_check(self):
        self.assertTrue(self.core.check_hermes()["ok"])
        os.environ["FAKE_VERSION"] = "0.17.3"
        h = self.core.check_hermes()
        self.assertTrue(h["found"])
        self.assertFalse(h["ok"])
        self.assertEqual(h["version"], "0.17.3")

    def test_profile_install_then_skip(self):
        self.assertFalse(self.core.profile_installed())
        self.assertTrue(self.core.install_profile(self.bin, ARCHIVE).ok)
        self.assertTrue(self.core.profile_installed())
        self.assertTrue(self.core.install_profile(self.bin, ARCHIVE).ok)
        imports = [c for c in self.calls() if c[:2] == ["profile", "import"]]
        self.assertEqual(len(imports), 1, "second run must not re-import")
        self.assertIn(["profile", "use", "homer"], self.calls())

    def test_grok_login_reads_code(self):
        self.assertFalse(self.core.grok_logged_in(self.bin))
        seen = {}
        import webbrowser
        webbrowser.open = lambda url: seen.setdefault("opened", url)
        r = self.core.grok_login(self.bin, lambda url, code: seen.update(url=url, code=code))
        self.assertTrue(r.ok)
        self.assertEqual(seen["code"], "ABCD-1234")
        self.assertTrue(seen["url"].startswith("https://accounts.x.ai/"))
        self.assertTrue(self.core.grok_logged_in(self.bin))
        self.assertTrue(self.core.use_grok(self.bin).ok)
        cfg = json.loads((self.tmp / "hermes" / "_fake.json").read_text())["config"]
        self.assertEqual(cfg["model.provider"], "xai-oauth")
        self.assertEqual(cfg["image_gen.provider"], "xai")

    def test_importer_and_prompt(self):
        self.assertTrue(self.core.ensure_importer(self.bin).ok)
        self.assertTrue(self.core.ensure_importer(self.bin).ok)
        installs = [c for c in self.calls() if "install" in c and "agent-importers" in c]
        self.assertEqual(len(installs), 1)
        p = self.core.export_prompt(self.bin)
        self.assertIn("Please export", p)
        msg = self.handoff.combined_message(p)
        self.assertIn("grok-bot-handoff.zip", msg)
        self.assertIn("Please export", msg)
        # 冇 -y：攞訊息嗰下唔可以搬任何嘢
        self.assertFalse(any("-y" in c for c in self.calls()))

    def test_downloads_watch_ignores_old_and_partial(self):
        dl = self.tmp / "home" / "Downloads"
        old = dl / "grok-bot-export.json"
        old.write_text("{}")
        os.utime(old, (time.time() - 3600, time.time() - 3600))
        since = time.time()
        self.assertEqual(self.core.find_new_downloads(since), {})
        (dl / "grok-bot-handoff.zip.crdownload").write_text("x")
        self.assertEqual(self.core.find_new_downloads(since), {})
        (dl / "grok-bot-export (1).json").write_text('{"name": "Trip Planner"}')
        (dl / "grok-bot-handoff.zip").write_text("x")
        f = self.core.find_new_downloads(since)
        self.assertEqual(f["export"].name, "grok-bot-export (1).json")
        self.assertEqual(f["handoff"].name, "grok-bot-handoff.zip")
        self.assertEqual(self.core.bot_name_from_export(f["export"]), "Trip Planner")

    def test_preview_and_import(self):
        exp = self.tmp / "home" / "Downloads" / "grok-bot-export.json"
        exp.write_text("{}")
        r = self.core.preview_import(self.bin, exp)
        self.assertTrue(r.ok)
        lines = self.core.summarize(r.out)
        self.assertTrue(any("3 skills" in l for l in lines))
        self.assertTrue(self.core.do_import(self.bin, exp).ok)

    def _zip(self, entries):
        z = self.tmp / "home" / "Downloads" / "grok-bot-handoff.zip"
        with zipfile.ZipFile(z, "w") as zf:
            for name, data in entries.items():
                zf.writestr(name, data)
        return z

    def test_zip_good_extract_and_memory(self):
        md = "# 交接\n## 未完成嘅工作\n- 京都行程訂酒店：等你批\n- 整理收據\n## 你定期做緊嘅嘢\n- 每朝 8 點\n"
        z = self._zip({"HANDOFF.md": md, "reports/a.md": "x", ".env": "SECRET=1", "notes/cookies.txt": "c"})
        info = self.handoff.check_zip(z)
        self.assertTrue(info["ok"], info)
        self.assertEqual(sorted(info["skipped"]), [".env", "notes/cookies.txt"])
        dest = self.handoff.extract(z, "行程/助手", info)
        self.assertEqual(dest.name, "行程助手")
        self.assertTrue((dest / "reports" / "a.md").exists())
        self.assertFalse((dest / ".env").exists())
        items = self.handoff.open_items(md)
        self.assertEqual(items, ["京都行程訂酒店：等你批", "整理收據"])
        self.assertTrue(self.handoff.add_memory("行程助手", dest, items))
        self.assertTrue(self.handoff.add_memory("行程助手", dest, items))  # 唔重複
        mem = (self.tmp / "hermes" / "profiles" / "homer" / "memories" / "MEMORY.md").read_text()
        self.assertEqual(mem.count("從 Grok Bot「行程助手」"), 1)
        self.assertIn("京都行程訂酒店", mem)

    def test_zip_rejects_traversal_and_missing_handoff(self):
        z = self._zip({"../evil.sh": "x", "a.txt": "y"})
        info = self.handoff.check_zip(z)
        self.assertFalse(info["ok"])
        self.assertTrue(any("危險路徑" in p for p in info["problems"]))
        self.assertTrue(any("HANDOFF.md" in p for p in info["problems"]))

    def test_memory_appends_with_delimiter(self):
        mem = self.tmp / "hermes" / "profiles" / "homer" / "memories" / "MEMORY.md"
        mem.parent.mkdir(parents=True)
        mem.write_text("User likes short answers\n")
        self.handoff.add_memory("A", self.tmp, [])
        self.assertIn("User likes short answers\n§\n從 Grok Bot「A」", mem.read_text())


    def test_chatgpt_login_sets_provider_only(self):
        import webbrowser
        webbrowser.open = lambda url: None
        r = self.core.login(self.bin, "chatgpt", lambda u, c: None)
        self.assertTrue(r.ok)
        self.assertIn(["auth", "add", "openai-codex", "--type", "oauth"], self.calls())
        self.assertEqual(self.core.first_logged_in(self.bin), "grok")  # 假 hermes 只有一個登入狀態
        self.assertTrue(self.core.use_provider(self.bin, "chatgpt").ok)
        cfg = json.loads((self.tmp / "hermes" / "_fake.json").read_text())["config"]
        self.assertEqual(cfg, {"model.provider": "openai-codex", "model.default": "", "model.base_url": "", "image_gen.provider": ""})

    def test_suggest_provider(self):
        apps = self.tmp / "Applications"
        apps.mkdir()
        self.assertEqual(self.core.suggest_provider(apps), "nous")
        (apps / "Grok Bot.app").mkdir()
        self.assertEqual(self.core.suggest_provider(apps), "grok")
        (self.tmp / "home" / ".codex").mkdir()
        self.assertEqual(self.core.suggest_provider(apps), "chatgpt")

    def test_english_build(self):
        os.environ["HOMER_LANG"] = "en"
        from homer_mover import i18n
        self.assertEqual(i18n.t("s4_go"), "Start")
        self.assertNotRegex(" ".join(i18n.all_strings().values()), r"[\u4e00-\u9fff]")
        msg = self.handoff.combined_message("OFFICIAL")
        self.assertIn("handoff package", msg)
        self.assertNotRegex(msg, r"[\u4e00-\u9fff]")
        self.handoff.add_memory("Trip", self.tmp, ["book hotel"])
        mem = (self.tmp / "hermes" / "profiles" / "homer" / "memories" / "MEMORY.md").read_text()
        self.assertIn("Moved from Grok Bot “Trip”", mem)
        os.environ["HOMER_LANG"] = "zh"
        self.assertEqual(i18n.t("s4_go"), "開始搬")

    def test_every_string_has_both_languages(self):
        from homer_mover.i18n import S
        for k, (zh, en) in S.items():
            if zh is None:
                continue
            self.assertTrue(zh and en, k)
            self.assertEqual(zh.count("{"), en.count("{"), k)

    def test_old_profile_gets_new_skills_but_keeps_config_and_memory(self):
        self.assertTrue(self.core.install_profile(self.bin, ARCHIVE).ok)
        d = self.tmp / "hermes" / "profiles" / "homer"
        (d / "distribution.yaml").write_text("name: homer\nversion: 0.1.0\n")
        (d / "config.yaml").write_text("model:\n  provider: openai-codex\n")
        (d / "memories").mkdir(exist_ok=True)
        (d / "memories" / "MEMORY.md").write_text("keep me")
        import shutil
        shutil.rmtree(d / "skills" / "homer-doctor")
        self.assertTrue(self.core.install_profile(self.bin, ARCHIVE).ok)
        self.assertTrue((d / "skills" / "homer-doctor" / "SKILL.md").exists())
        self.assertIn("openai-codex", (d / "config.yaml").read_text())
        self.assertEqual((d / "memories" / "MEMORY.md").read_text(), "keep me")
        self.assertFalse(self.core.update_profile_files(ARCHIVE), "same version: no second update")

    def test_minimax_login_command(self):
        import webbrowser
        webbrowser.open = lambda url: None
        self.assertTrue(self.core.login(self.bin, "minimax", lambda u, c: None).ok)
        self.assertIn(["auth", "add", "minimax-oauth"], self.calls())

    def test_api_key_saved_privately_and_never_logged(self):
        key = "sk-test-1234567890abcdefXYZ"
        logged = []
        r = self.core.save_api_key(self.bin, "deepseek", "  " + key + "\n", logged.append)
        self.assertTrue(r.ok, r.out)
        env = self.tmp / "hermes" / "profiles" / "homer" / ".env"
        self.assertIn("DEEPSEEK_API_KEY=" + key, env.read_text())
        self.assertEqual(oct(env.stat().st_mode & 0o777), "0o600")
        self.assertFalse(any(key in l for l in logged), "key must not appear in the log")
        self.assertFalse(any(key in " ".join(c) for c in self.calls()), "key must not be passed on a command line")
        cfg = json.loads((self.tmp / "hermes" / "_fake.json").read_text())["config"]
        self.assertEqual(cfg["model.provider"], "deepseek")
        self.assertEqual(self.core.saved_api_key(), "deepseek")
        # 再寫一次唔會重複
        self.core.save_api_key(self.bin, "deepseek", key)
        self.assertEqual(env.read_text().count("DEEPSEEK_API_KEY="), 1)

    def test_bad_api_key_rejected(self):
        for bad in ["", "short", "has space in it 1234567890", "line\nbreak1234567890abc"]:
            self.assertEqual(self.core.save_api_key(self.bin, "gemini", bad).out, "bad key", bad)
        self.assertEqual(self.core.save_api_key(self.bin, "nope", "sk-1234567890abcdefgh").out, "unknown provider")
        self.assertIsNone(self.core.saved_api_key())


if __name__ == "__main__":
    unittest.main()
