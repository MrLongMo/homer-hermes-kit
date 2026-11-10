# Homer 搬家程式（Grok Bot → Hermes）

一個視窗：裝 Hermes → 裝 Homer 設定 → Grok 登入 → 搬 Grok Bot（設定＋工作檔案＋交接）→ 打開 Hermes。
全部經官方 `hermes` 指令做；Hermes 未裝就下載官方 Hermes-Setup 安裝程式。

- 後台：`homer_mover/core.py`（Hermes 指令）、`homer_mover/handoff.py`（交接 zip 檢查／解壓／記憶）
- 介面：`homer_mover/ui/index.html`，`homer_mover/app.py` 係介面叫嘅 Python 功能
- 測試：`../.venv/bin/python -m unittest discover -s tests`（用 `tests/fake_hermes.py` 扮 hermes，唔會掂真 Hermes）
- 砌 Mac：`./build_mac.sh` → `dist/Homer-Mover-mac.zip`
- 砌 Windows：要 Windows 機或者 GitHub Actions（`.github/workflows/build-app.yml`，推 `app-v*` tag）

測試時唔想掂本機 Hermes：`HERMES_HOME=<暫存資料夾> HOMER_HERMES_BIN=<假 hermes>`。
⚠️ 本機 ~/.hermes 係舊 Jarvis（v0.17）：真機測試請用另一個 macOS 用戶帳號，唔好喺 Boss 帳號撳「更新 Hermes」。
