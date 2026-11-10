# Homer 出品｜Hermes 搬家包

> Grok Bot 爆額度？一個檔案搬去 Hermes：繁體中文介面、會整圖、慳 token。唔使打任何指令。
>
> [English below](#english)

## 你會得到咩
- **Homer 小助手**：識講廣東話／繁體中文／英文，答嘢短而白話。
- **Grok Bot 一鍵搬家**：同小助手講「幫我由 Grok Bot 搬過嚟」，佢會帶你一步步做。角色、技能、記憶、例行工作，連工作檔案同未做完嘅嘢都搬得走。
- **整圖**：用你自己嘅 Grok 月費 + Grok Imagine，講一句就整到。
- **慳 token 預設**：早啲壓縮長對話、雜務用平啲嘅設定；嫌貴仲可以一句轉平模型。

## 3 步裝好（唔使 terminal）
1. 下載官方 **Hermes Desktop**：<https://hermes-agent.nousresearch.com/desktop>（Mac / Windows）。
   - Windows 第一次開可能彈「Windows 已保護您的電腦」：撳「其他資訊」→「仍要執行」。
2. 下載 **[homer.tar.gz](../../releases/latest)**。
   喺 Hermes Desktop 撳 **⌘K（Windows：Ctrl+K）→ Import profile…**，揀剛下載嘅檔案。
3. **Settings → Providers → Accounts → xAI Grok** 登入你嘅 Grok 帳號。完成！

想搬 Grok Bot：開新對話，打「幫我由 Grok Bot 搬過嚟」。

## 要知
- 要有 **SuperGrok 或 X Premium+**，先可以用 Grok 登入。冇嘅話，可以喺 Settings → Model 揀其他模型（例如 OpenRouter）。
- 有用家報告某啲 Grok 級別登入後會出 `HTTP 403`，係 xAI 嗰邊嘅限制。解決方法：改用 xAI API key。
- Grok Bot 例行工作搬過嚟係**暫停**狀態，免得兩邊重複行。
- 對話係 Bot 自己寫嘅重點，唔係逐句原文；原本對話仲留喺 Grok Bot。
- 搬設定用嘅係 Nous Research 官方 `agent-importers`；檔案同進度由 Bot 自己打包交接。呢個包只係幫你帶路，唔會將你任何資料傳去其他地方。
- 用終端機嘅話：`hermes profile install github.com/MrLongMo/homer-hermes-kit --alias`

## 更新 / 教學
訂閱電子報收更新同進階教學：**（連結待補）**

---

## English

**Homer's Hermes Kit — move from Grok Bot to Hermes with one file. No terminal.**

### What you get
- **Homer assistant**: answers in your language (Cantonese, Traditional Chinese or English), short and plain.
- **Guided Grok Bot migration**: say "move me from Grok Bot" and it walks you through the official importer. Role, skills, memories and routines come over, plus the bot's work files and a handoff of open work.
- **Images**: Grok Imagine on your own Grok subscription.
- **Token-lean defaults**: earlier compression of long chats and low-effort side tasks. One sentence switches daily chat to a cheaper model.

### Install in 3 steps
1. Get the official **Hermes Desktop**: <https://hermes-agent.nousresearch.com/desktop>.
2. Download **[homer.tar.gz](../../releases/latest)**. In Hermes Desktop: **⌘K / Ctrl+K → Import profile…**
3. **Settings → Providers → Accounts → xAI Grok**: sign in. Done.

To migrate, open a new chat and type "move me from Grok Bot".

### Notes
- Grok sign-in needs **SuperGrok or X Premium+**. Some tiers get `HTTP 403` from xAI; switch to an xAI API key if that happens.
- Imported routines arrive **paused**.
- Conversations come over as the bot's own summary, not word for word.
- Migration uses Nous Research's official `agent-importers` plugin. This kit sends your data nowhere.
- Terminal users: `hermes profile install github.com/MrLongMo/homer-hermes-kit --alias`

### Updates
Newsletter: **(link TBD)**

---
MIT License · Homer 出品 · Not affiliated with Nous Research or xAI.
