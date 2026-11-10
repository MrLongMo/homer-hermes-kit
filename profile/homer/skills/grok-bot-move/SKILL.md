---
name: grok-bot-move
description: "帶用家由 Grok Bot 搬去 Hermes：角色、技能、記憶、例行工作，加埋工作檔案、對話重點同未完成嘅工作，全程唔使佢自己打指令。Guide a user moving from Grok Bot to Hermes (setup, files, open work) without them touching a terminal."
version: 1.1.0
author: Homer 出品
license: MIT
metadata:
  hermes:
    tags: [Grok Bot, migration, import, 搬家]
---

# 由 Grok Bot 搬過嚟

> 語言：所有同用家講嘅說話，用對方嘅語言。台灣用家（書面中文）用台灣慣用語，例如「按」「檔案」「軟體」；下面引號入面嘅句子只係意思參考。

用家唔識 terminal。所有指令由你（agent）用 terminal 工具代佢行，佢只需要喺 Grok Bot 度貼兩段字、下載兩個檔案。

搬分兩部分：
- **設定**：角色、技能、記憶、例行工作。用官方 `agent-importers` 外掛（Nous Research 維護）。
- **工作**：工作檔案、對話重點、未完成嘅工作。官方工具唔搬呢啲，所以叫 Bot 自己寫一份交接、連檔案打包。

Grok Bot 嗰邊唔會改任何嘢。

## 開始前講清楚（一句講晒）
「我會幫你裝官方搬家工具，再叫你喺 Grok Bot 貼兩段字、下載兩個檔案。Grok Bot 嗰邊唔會改任何嘢，搬之前我會畀你睇清單先。」等佢答好先繼續。

有幾個 Bot 就**一次搬一個**，搬完一個先開始下一個。

## 步驟

1. **確認 hermes 指令搵唔搵到**
   - 行 `hermes --version`。搵唔到就試 `~/.hermes/bin/hermes --version`（Windows：`%LOCALAPPDATA%\hermes\bin\hermes.exe`）。
   - 都搵唔到：叫佢喺 Hermes Desktop 嘅 Settings 確認已裝好 Hermes runtime，停喺度。
   - 版本要支援 `hermes migrate grok-bot`（2026-11-02 之後嘅版本）。太舊就叫佢喺 Desktop 撳更新。

2. **裝搬家工具**（每個 profile 一次）
   - 先講：「我而家裝官方搬家工具 agent-importers。」
   - 行 `hermes -p homer plugins install agent-importers`。已經裝咗就跳過。

3. **攞兩段要貼嘅字**
   - 行 `hermes -p homer import-agent grok-bot`。未有匯出檔時，佢會印一段訊息，亦會存喺 Hermes home 嘅 `grok-bot-import/export-prompt.txt`。呢段係**第一段**。
   - **第二段**係下面「交接訊息」，用佢傾偈嘅語言揀中文或者英文版本。
   - 兩段各放喺一個 code block 畀用家，講：
     「打開 Grok Bot，揀你想搬嘅 Bot。
     ① 貼第一段，佢會整 `grok-bot-export.json`，下載。
     ② 再貼第二段，佢會整 `grok-bot-handoff.zip`，都下載。
     兩個檔案放喺『下載項目』資料夾就得。」
   - 提佢：兩段都要 Bot 回覆，會用少少 Grok Bot 額度。額度用晒嘅話，要等重置先做到。
   - 等佢講「好咗」。

4. **預覽設定**
   - 行 `hermes -p homer import-agent grok-bot --dry-run`（檔案喺 ~/Downloads 會自動搵到；唔喺嗰度就加 `--source <路徑>`）。
   - 用白話總結清單，最多 5 點：有幾多個技能、記憶、例行工作，同埋邊啲要自己重建（Slack／GitHub／email 觸發嘅例行工作會變成筆記，唔會自動行）。
   - 問：「無問題就開始搬？」

5. **正式搬設定**
   - 行 `hermes -p homer import-agent grok-bot -y`。
   - 講搬咗咩（數量）。例行工作嘅事放喺第 7 步先講。

6. **搬工作檔案同進度**（用家未有 `grok-bot-handoff.zip` 就問佢要唔要補做；佢話唔要就跳去第 7 步）
   - **先睇入面有咩，未解壓**：
     - macOS／Linux：`unzip -l ~/Downloads/grok-bot-handoff.zip`
     - Windows（PowerShell）：`Add-Type -A System.IO.Compression.FileSystem; [IO.Compression.ZipFile]::OpenRead("$HOME\Downloads\grok-bot-handoff.zip").Entries | Select FullName, Length`
   - 有以下情況就停，同用家講，唔好解壓：
     - 路徑有 `..`、或者由 `/`、`C:\` 開頭。
     - 檔名似登入資料：`.env`、`*cookie*`、`*token*`、`*credential*`、`*.pem`、`*.key`、`id_rsa*`、`*password*`、`*secret*`。
     - 冇 `HANDOFF.md`。
     叫佢返 Grok Bot 講「唔好包任何登入資料，重新打包」。
   - **解壓去用家睇得到嘅資料夾**：`文件/Grok Bot 搬家/<Bot 名>/`
     - macOS／Linux：`mkdir -p "$HOME/Documents/Grok Bot 搬家/<Bot 名>" && unzip -n ~/Downloads/grok-bot-handoff.zip -d "$HOME/Documents/Grok Bot 搬家/<Bot 名>"`
     - Windows：`Expand-Archive "$HOME\Downloads\grok-bot-handoff.zip" "$HOME\Documents\Grok Bot 搬家\<Bot 名>"`
     - 解壓完將 zip 改名做 `grok-bot-handoff-<Bot 名>.zip`，免得搬下一個 Bot 時撞名。
   - **讀 `HANDOFF.md`**，用 memory 工具加**一條**記憶（記憶有字數上限，唔好成份抄入去）：
     `由 Grok Bot「<Bot 名>」搬過嚟。交接同檔案喺 <完整路徑>，做相關嘢之前先讀 HANDOFF.md。未完成：<最多 3 項，每項一句>`
   - 用白話講畀用家聽，最多 5 點：搬咗幾多個檔案、去咗邊、有咩未完成。
   - 最後問：「要唔要我而家接住做『<第一項未完成嘅工作>』？」

7. **收尾講三樣嘢**
   - 例行工作搬過嚟係**暫停**狀態，免得同 Grok Bot 重複行。叫佢先喺 Grok Bot 關咗嗰個例行工作，再話你知，你用 `hermes -p homer cron resume <id>` 開返。
   - 匯出檔入面似密碼／key 嘅嘢會被拒絕或者遮咗，所以各個網站同 app 要喺 Hermes 重新登入。
   - 對話係 Bot 寫嘅**重點**，唔係逐句原文。原本嘅對話仲喺 Grok Bot 度。

## 交接訊息（第二段，原文畀用家貼）

中文版：
```
請幫我準備一個交接包，我要搬去另一個 AI 助手。唔好改、唔好刪、唔好寄出任何嘢，亦唔好開始任何新工作。

1. 寫一份 HANDOFF.md，用我平時同你傾偈嘅語言，包括：
   - 你嘅角色（一句）
   - 我哋傾過嘅主要事項：每項寫日期（如果知）同決定咗咩
   - 未完成嘅工作：每項寫做到邊、下一步係咩、等緊我批咩
   - 你定期做緊嘅嘢，同佢哋用到邊啲檔案
   - 你知道我嘅偏好同習慣
   - 檔案清單：每個檔案一句講用途
   唔好寫任何密碼、API key、token、銀行或者信用卡號碼。

2. 將 HANDOFF.md，同你為我整過或者工作用到嘅檔案（報告、表格、草稿、script、筆記），壓縮成一個 grok-bot-handoff.zip。
   - 唔好包：密碼、API key、token、cookie、.env、瀏覽器登入資料、任何登入憑證。
   - 單一檔案大過 20MB 就唔包，喺 HANDOFF.md 列出嚟。
   - 成個 zip 盡量細過 100MB。

3. 將 grok-bot-handoff.zip 傳畀我下載。整唔到 zip 的話，就將 HANDOFF.md 成段貼出嚟。
```

English:
```
Please prepare a handoff package: I'm moving to another AI assistant. Don't change, delete or send anything, and don't start any new work.

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

3. Send me grok-bot-handoff.zip to download. If you can't make a zip, paste HANDOFF.md in full instead.
```

用家只係貼咗 HANDOFF.md 文字冇 zip：將佢成段存做 `文件/Grok Bot 搬家/<Bot 名>/HANDOFF.md`，照第 6 步加記憶，同佢講檔案冇搬到。

## 出事點算
- 匯出檔被拒（credential-looking keys）：叫佢喺 Grok Bot 重新匯出，同 Bot 講「唔好包任何 key 或者密碼」。
- 一個 Bot 分幾段匯出：全部放落同一個資料夾，用 `--source <資料夾>`，會自動合併。
- 佢只係貼咗文字冇檔案：將 Bot 成段回覆存成 `~/Downloads/grok-bot-export.txt`，再用 `--source` 指住佢。
- zip 太大或者 Bot 話傳唔到：叫 Bot 分開幾個 zip（`grok-bot-handoff-1.zip`、`-2.zip`…），逐個照第 6 步做。
- 用家想要逐句原文對話：話佢知社群有人整咗 `gbot migrate`（sam_lung2077，GitHub akari-sora/grok-bot-cli），可以連原文搬，但要用 terminal 同 Node.js，亦係非官方工具，會讀 Grok Bot app 嘅登入資料。**唔好主動幫佢裝**；佢堅持就先講清楚以上風險，等佢再確認。
- 任何一步失敗：原文貼錯誤訊息畀用家睇，唔好自己估住改設定。

## English users
Same steps; reply in English and use the English handoff message. Say what you'll install before installing it, show the dry-run summary before importing, check the zip's contents before extracting it, and remind them that routines arrive paused and that conversations come over as summaries, not word for word.
