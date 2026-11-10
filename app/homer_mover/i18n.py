"""中英文字。砌程式時揀語言：data/lang.txt 寫 zh 或 en（冇就睇 HOMER_LANG，再冇就 zh）。"""
from __future__ import annotations

import os
import sys
from pathlib import Path

_HERE = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))


def lang() -> str:
    f = _HERE / "homer_mover" / "data" / "lang.txt"
    v = os.environ.get("HOMER_LANG") or (f.read_text().strip() if f.is_file() else "zh")
    return "en" if v.lower().startswith("en") else "zh"


S: dict[str, tuple[str, str]] = {
    # ---- 視窗 ----
    "window_title": ("Homer 出品｜Grok Bot 搬到 Hermes", "Homer's Grok Bot → Hermes Mover"),
    "brand": ("HOMER 出品", "MADE BY HOMER"),
    "h1_a": ("Grok Bot 搬到 ", "Move Grok Bot to "),
    "sub": ("跟著點，一個視窗搞定。Grok Bot 那邊不會被修改。",
            "Click through one window. Nothing in Grok Bot gets changed."),
    "done_state": ("完成", "Done"),
    "doing_state": ("進行中", "Now"),
    "log": ("詳細紀錄（出問題時給 Homer 看）", "Details (send these to Homer if something breaks)"),
    "foot": ("Homer 出品 · 開源 · 與 Nous Research、xAI 無關。全部透過官方 Hermes 指令執行，資料留在你的電腦。",
             "Made by Homer · open source · not affiliated with Nous Research or xAI. Everything runs through the official Hermes commands, and your data stays on your computer."),
    # ---- 1 ----
    "s1_title": ("安裝 Hermes", "Install Hermes"),
    "s1_checking": ("正在檢查你的電腦…", "Checking your computer…"),
    "s1_missing": ("你的電腦還沒有 Hermes。我會幫你下載<b>官方安裝程式</b>，打開後跟著點就好（大約 5–10 分鐘）。<br>最後看到「HERMES IS READY」時<b>先不要按 Launch Hermes</b>，關掉它回到這裡就好。",
                   "Hermes isn't on this computer yet. I'll download the <b>official installer</b>; just click through it (about 5–10 minutes).<br>When you see “HERMES IS READY”, <b>don't click Launch Hermes yet</b>. Close it and come back here."),
    "s1_install": ("安裝 Hermes", "Install Hermes"),
    "s1_recheck": ("我裝好了，再檢查一次", "I've installed it, check again"),
    "s1_old": ("你的電腦有 Hermes <b>v{v}</b>，版本太舊，搬家功能需要 v0.22.6 以上。",
               "This computer has Hermes <b>v{v}</b>. Moving bots needs v0.22.6 or later."),
    "s1_update": ("更新 Hermes", "Update Hermes"),
    "p_download": ("正在下載官方 Hermes 安裝程式…", "Downloading the official Hermes installer…"),
    "p_opened": ("已打開官方安裝程式，請跟著它點。最後看到「HERMES IS READY」時，先不要按 Launch Hermes，按左上角紅色 ✕ 關掉它，回到這裡，我會自動繼續。",
                 "The official installer is open; click through it. When you see “HERMES IS READY”, don't click Launch Hermes. Close it with the red ✕ and come back. I'll carry on by myself."),
    "e_wait": ("等了 60 分鐘還沒看到 Hermes 裝好。裝完後可以按「再檢查一次」。",
               "Hermes still isn't installed after 60 minutes. Click “check again” once it's done."),
    "p_updating": ("正在更新 Hermes（需要幾分鐘）…", "Updating Hermes (a few minutes)…"),
    "e_update": ("更新失敗：", "The update didn't work:"),
    # ---- 2 ----
    "s2_title": ("安裝 Homer 設定", "Install Homer's setup"),
    "s2_text": ("繁體中文介面、會用你的語言回覆的小助手、省 token 設定、開工精靈和 Homer 醫生。",
                "A token-saving setup, a friendly assistant, a getting-started wizard and a weekly health check."),
    "p_profile": ("正在安裝 Homer 設定…", "Installing Homer's setup…"),
    "e_profile": ("Homer 設定安裝失敗：", "Couldn't install Homer's setup:"),
    # ---- 3 ----
    "s3_title": ("選 AI（用你本來就有的帳號）", "Pick your AI (use an account you already have)"),
    "s3_text": ("點你有的那一個，會打開瀏覽器，登入後按「同意」即可。不用複製任何金鑰。",
                "Click the one you have. A browser opens; sign in and approve. No keys to copy."),
    "pv_grok": ("Grok", "Grok"),
    "pv_grok_d": ("有 SuperGrok 或 X Premium+", "SuperGrok or X Premium+"),
    "pv_chatgpt": ("ChatGPT", "ChatGPT"),
    "pv_chatgpt_d": ("有 ChatGPT Plus／Pro", "ChatGPT Plus / Pro"),
    "pv_nous": ("Nous Portal", "Nous Portal"),
    "pv_nous_d": ("都沒有？開免費帳號", "Nothing yet? Free account"),
    "pv_openrouter": ("OpenRouter", "OpenRouter"),
    "pv_openrouter_d": ("有 OpenRouter 帳號", "Have an OpenRouter account"),
    "recommended": ("推薦", "Suggested"),
    "more": ("更多選項", "More options"),
    "pv_minimax": ("MiniMax", "MiniMax"),
    "pv_minimax_d": ("免費登入，但限制較多", "Free sign-in, tight limits"),
    "key_title": ("我有 API 金鑰", "I have an API key"),
    "key_text": ("選擇服務，貼上你的金鑰。金鑰只會存在你電腦上的 Hermes，不會傳到任何地方。",
                 "Pick the provider and paste your key. It is saved only in Hermes on this computer and sent nowhere else."),
    "key_ph": ("貼上金鑰（例如 sk-…）", "Paste your key (e.g. sk-…)"),
    "key_save": ("儲存並使用", "Save and use"),
    "e_badkey": ("金鑰格式不正確：不能有空格，通常是 sk- 或 AIza 開頭的一長串文字。", "That key doesn't look right: no spaces, usually a long string starting with sk- or AIza."),
    "no_claude": ("為什麼沒有 Claude 登入？Anthropic 不允許在其他程式使用 Claude 訂閱帳號；如果有 Claude API 金鑰，請在上方選「Claude API」。為什麼沒有 Qwen？它的免費登入已在 2026 年 4 月停止。",
                  "Why no Claude sign-in? Anthropic doesn't allow Claude subscription logins in other apps; if you have a Claude API key, pick “Claude API” above. Why no Qwen? Its free sign-in ended in April 2026."),
    "s3_code": ("如果瀏覽器要求輸入登入碼，請填：", "If the browser asks for a code, enter:"),
    "s3_nocode": ("（不用填，直接按同意）", "(no code needed, just approve)"),
    "s3_reopen": ("瀏覽器沒打開？點這裡", "Browser didn't open? Click here"),
    "s3_wait": ("按完同意後，回到這裡等幾秒。", "After approving, come back and wait a few seconds."),
    "s3_nous_hint": ("Nous Portal：註冊或登入，選擇 <b>Free</b> 方案，再按授權。", "Nous Portal: sign up or sign in, choose the <b>Free</b> plan, then authorize."),
    "s3_skip": ("之後再選，先跳過", "Skip for now"),
    "p_login": ("正在打開登入頁…", "Opening the sign-in page…"),
    "e_login": ("登入未完成。可以再試一次、改選其他服務，或按「先跳過」。", "Sign-in didn't finish. Try again, pick another one, or skip."),
    "e_login_set": ("已登入，但設定預設 AI 失敗：", "Signed in, but setting the default AI failed:"),
    # ---- 4 ----
    "s4_title": ("搬 Grok Bot", "Move a Grok Bot"),
    "s4_intro": ("一次搬一個 Bot。沒有 Grok Bot 或不想搬？可以直接跳到最後一步。",
                 "One bot at a time. No Grok Bot? Skip to the last step."),
    "s4_go": ("開始搬", "Start"),
    "s4_skip": ("不搬，跳過", "Skip"),
    "s4_steps": ("① 按「複製」，② 打開 Grok Bot 選擇要搬的 Bot，③ 貼上並送出。",
                 "① Click Copy, ② open Grok Bot and pick the bot to move, ③ paste and send."),
    "copy": ("複製", "Copy"),
    "copied": ("已複製 ✓", "Copied ✓"),
    "copy_fail": ("請手動選取複製", "Select and copy it yourself"),
    "open_gb": ("打開 Grok Bot", "Open Grok Bot"),
    "s4_dl": ("<b>④ Bot 會做出兩個檔案，兩個都要下載。</b>下載完我會自動找到。",
              "<b>④ The bot makes two files. Download both.</b> I'll find them."),
    "s4_pick": ("檔案不在「下載項目」？手動選擇", "Files not in Downloads? Pick them"),
    "s4_will": ("將會搬移：", "This will move:"),
    "s4_botname": ("Bot 名稱（用來建立資料夾）：", "Bot name (for the folder):"),
    "s4_botph": ("例如：行程助手", "e.g. Trip Planner"),
    "s4_move": ("搬", "Move"),
    "s4_nozip": ("沒有收到工作檔案（grok-bot-handoff.zip），只搬設定。", "No work files (grok-bot-handoff.zip) yet, so only the setup moves."),
    "s4_zipok": ("工作檔案：<b>{n} 個</b>", "Work files: <b>{n}</b>"),
    "s4_zipskip": ("（{n} 個疑似登入資料的檔案不搬）", " ({n} that look like logins are left out)"),
    "s4_zipbad": ("工作檔案有問題，不會搬移：", "The work files have a problem and won't be moved:"),
    "s4_moved": ("「{b}」搬好了 ✓", "“{b}” moved ✓"),
    "s4_files": ("工作檔案 {n} 個 → {f}", "{n} work files → {f}"),
    "s4_open": ("還沒完成：", "Still open: "),
    "s4_memfull": ("記憶已滿，沒有加入交接提示。跟小助手說「去讀 HANDOFF.md」就好。", "Memory is full, so no handoff note was added. Tell the assistant “read HANDOFF.md”."),
    "s4_folder": ("打開檔案資料夾", "Open the folder"),
    "s4_again": ("再搬一個 Bot", "Move another bot"),
    "s4_next": ("搬完了，下一步", "Done, next"),
    "default_bot": ("我的 Bot", "My bot"),
    "p_prepare": ("正在準備官方搬家工具…", "Getting the official importer ready…"),
    "e_importer": ("無法安裝官方搬家工具：", "Couldn't install the official importer:"),
    "p_preview": ("正在確認可以搬哪些內容…", "Checking what can be moved…"),
    "e_export": ("讀不到匯出檔（可能不完整）。請在 Grok Bot 請它重新做一次。", "The export file can't be read (it may be incomplete). Ask the bot to make it again."),
    "p_import": ("正在搬移設定…", "Moving the setup…"),
    "e_import": ("設定搬移失敗：", "Moving the setup failed:"),
    "p_files": ("正在搬移工作檔案…", "Moving work files…"),
    "e_nofiles": ("工作檔案沒有搬：", "Work files not moved: "),
    # ---- 5 ----
    "s5_title": ("完成", "Finish"),
    "s5_routines": ("<b>排程搬過去後是暫停的</b>，避免和 Grok Bot 重複執行。請先在 Grok Bot 關掉，再跟小助手說「開啟 XX 排程」。",
                    "<b>Routines arrive paused</b> so nothing runs twice. Turn it off in Grok Bot first, then tell the assistant “turn on the XX routine”."),
    "s5_noai": ("<b>你還沒選 AI</b>，Hermes 需要選一個才能聊天。打開後會看到「開始設定」：選 <b>Nous Portal</b> 的免費方案，或「我有 API 金鑰」。",
                "<b>You haven't picked an AI yet.</b> Hermes needs one to chat. When it opens you'll see the setup screen: choose <b>Nous Portal</b> for the free plan, or “I have an API key”."),
    "s5_nous": ("<b>你正在使用 Nous Portal 免費方案：</b>如果聊天時提示需要訂閱，在 Hermes 的模型選單選擇標示免費的模型。",
                "<b>You're on the Nous Portal free plan.</b> If chat asks for a subscription, open the model picker and choose one ending in “:free”."),
    "s5_start": ("<b>打開 Hermes 後，在對話框打「你好」</b>，小助手會問你 3 個問題，幫你設好每天要做的事（開工精靈）。",
                 "<b>Once Hermes opens, type “hi” in the chat box.</b> The assistant asks three questions and sets up your daily tasks (the getting-started wizard)."),
    "help": ("卡住了？看教學和常見問題", "Stuck? Read the guide and FAQ"),
    "s5_go": ("打開 Hermes", "Open Hermes"),
    # ---- 交接訊息 ----
    "handoff": (None, None),  # 見 handoff.py
}


def t(key: str, **kw) -> str:
    zh, en = S[key]
    s = en if lang() == "en" else zh
    return s.format(**kw) if kw else s


def all_strings() -> dict[str, str]:
    return {k: (v[1] if lang() == "en" else v[0]) for k, v in S.items() if v[0] is not None}
