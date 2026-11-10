# Homer 搬家程式｜Grok Bot → Hermes

**懶人包（圖文教學）**：https://mrlongmo.github.io/homer-hermes-kit/grok-bot-to-hermes/

一個視窗幫你：安裝 Hermes → 裝好中文設定 → 用你現有的帳號選 AI → 把 Grok Bot 連工作檔案一起搬過來。不用打指令。

**下載（Mac，Apple 晶片）**：[Homer-Mover-mac-zh.zip](https://github.com/MrLongMo/homer-hermes-kit/releases/latest/download/Homer-Mover-mac-zh.zip)　·　English: [Homer-Mover-mac-en.zip](https://github.com/MrLongMo/homer-hermes-kit/releases/latest/download/Homer-Mover-mac-en.zip)

## 怎麼用

1. 下載後點兩下 zip 解壓縮。**第一次開啟：在「Homer 搬家」上按右鍵 →「打開」→ 再按「打開」。**
2. 按「安裝 Hermes」，跟著官方安裝程式點。最後看到「HERMES IS READY」**先不要按 Launch Hermes**，關掉它回到程式。
3. 選你有的 AI 帳號（Grok、ChatGPT、OpenRouter；都沒有就選 Nous Portal 免費方案），瀏覽器登入後按「同意」。
4. 要搬 Grok Bot：按「開始搬」→「複製」→ 貼到 Grok Bot → 下載它做的兩個檔案 → 按「搬」。不搬可以跳過。
5. 按「打開 Hermes」，**在對話框打「你好」**，開工精靈會問你 3 個問題，幫你設好每天要做的事。

## 常見問題

- **Mac 說「無法打開」或「無法驗證開發者」**：在程式上按右鍵 →「打開」→ 再按「打開」。程式還沒買 Apple 開發者簽章，不是病毒；原始碼都在這裡。
- **Intel Mac、Windows 能用嗎**：官方 Hermes Desktop 只支援 Apple 晶片（M1 以後）。Windows 版製作中。
- **沒有 Grok 訂閱**：第三步選 ChatGPT（Plus／Pro）、OpenRouter，或 Nous Portal 免費方案；「更多選項」可以貼 DeepSeek、Gemini、OpenAI、Claude 等 API 金鑰。
- **登入 Grok 出現 HTTP 403**：xAI 對部分方案的限制。改在「更多選項」貼 xAI API 金鑰。
- **打開 Hermes 後不知道做什麼**：在對話框打「你好」。或者跟小助手說「幫我設定」「檢查一下」「幫我省 token」。
- **排程沒有跑**：Hermes 在你的電腦上執行，關機或睡眠時不會跑。搬過來的排程預設暫停，要跟小助手說「開啟 XX 排程」。
- **卡住了**：展開程式底部的「詳細紀錄」，截圖到 [Issues](https://github.com/MrLongMo/homer-hermes-kit/issues) 問我們。

## FAQ

- **“Can’t be opened” / “unidentified developer” on Mac**: right-click the app → Open → Open. The app isn’t signed with an Apple developer certificate yet; all source is here.
- **Intel Mac / Windows**: official Hermes Desktop needs Apple silicon. Windows version coming.
- **No Grok subscription**: pick ChatGPT, OpenRouter or the free Nous Portal plan; “More options” accepts DeepSeek, Gemini, OpenAI, Claude and other API keys.
- **After Hermes opens**: type “hi” in the chat box; the getting-started wizard takes it from there.
- **Stuck**: expand “Details” at the bottom of the app, screenshot it and open an [issue](https://github.com/MrLongMo/homer-hermes-kit/issues).

## 裡面有什麼

- `app/`：搬家程式（Python＋pywebview）。全部透過官方 `hermes` 指令執行，資料和 API 金鑰只存在你的電腦。
- `profile/homer/`：Homer 設定（小助手、省 token、開工精靈、Homer 醫生、Grok Bot 搬家、做圖技能）。
- 測試：`python -m unittest discover -s app/tests`（用假的 hermes，不會動到真的 Hermes）。

與 Nous Research、xAI 無關。Hermes 是 Nous Research 的產品，Grok 是 xAI 的產品。MIT 授權。
