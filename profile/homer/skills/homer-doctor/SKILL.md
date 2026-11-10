---
name: homer-doctor
description: "Homer 醫生：檢查 Hermes 有冇問題（設定、排程、記憶、token 用量），用白話報告，修之前一定先問。Weekly health check for this Hermes: config, routines, memory and token use, in plain words; never fixes anything without asking."
version: 1.0.0
author: Homer 出品
license: MIT
metadata:
  hermes:
    tags: [health, doctor, maintenance, 健康檢查]
---

# Homer 醫生

> 語言：所有同用家講嘅說話，用對方嘅語言。台灣用家（書面中文）用台灣慣用語，例如「按」「檔案」「軟體」；下面引號入面嘅句子只係意思參考。

目的：用家唔使自己睇住 Hermes。你幫佢定期檢查，有問題用白話講，**修之前一定先問**。
最重要嘅規矩：**唔准自己靜靜雞修**。「Hermes 修自己整壞自己」係用家最怕嘅嘢。

## 幾時用
- 每週排程叫你（見最底「開每週檢查」）。
- 用家講「檢查吓」「做身體檢查」「點解咁慢」「點解排程冇行」「health check」。

## 檢查（全部只係睇，唔改任何嘢）

1. **設定同連線**：行 `hermes -p homer doctor`（**唔好加 `--fix`**）。記低未解決嘅問題（exit code 1 即係有）。
2. **排程**：行 `hermes -p homer cron doctor`。記低：失敗咗嘅、過咗時間冇行嘅、寄唔到結果嘅。
3. **記憶有幾滿**：讀 Hermes home 入面 `memories/MEMORY.md`（上限約 2,200 字）同 `memories/USER.md`（上限約 1,375 字），計字數。超過 80% 就記低：太滿會令佢記唔到新嘢、對話慢。
4. **token 用量**：行 `hermes -p homer insights --days 7`。記低總數同最食 token 嗰類對話。上一次檢查有記低數字就比較吓（記憶入面搵「Homer 醫生上次」）。

任何一步失敗（指令搵唔到、出錯）：唔好估，照記低「呢項檢查唔到」同錯誤第一行。

## 報告（最多 5 行，白話）

全部正常：
「✓ Homer 醫生：一切正常。今個禮拜用咗大約 X token（上個禮拜 Y）。」

有問題，每個問題一行，講**影響**同**你可以點幫**，例如：
- 「⚠️ 記憶用咗 92%，好快會記唔到新嘢。我可以將過時嘅 3 條執走，要唔要？」
- 「⚠️『每朝新聞』排程兩日冇行到，因為部電腦果陣熄咗機。開住機就會照行，唔使改。」
- 「⚠️ 設定檢查話 X 有問題。我可以用官方修復功能試修，要唔要？」

最後用 memory 工具更新**一條**記憶（覆蓋舊嗰條，唔好疊）：
`Homer 醫生上次（日期）：token 7 日 X；問題：…（冇就寫「冇」）`

## 修（只喺用家答「好」之後）
- 設定問題：`hermes -p homer doctor --fix`，再行一次 `hermes -p homer doctor` 確認。
- 記憶太滿：逐條列出你想刪或者合併嘅記憶，等用家揀，用 memory 工具改。**唔准一次過清晒。**
- 排程失敗：先講原因，再建議做法（例如 `cron run` 試行一次、改時間），用家答好先改。
- 背景服務死咗：講清楚「我會重開背景服務，進行緊嘅排程可能會斷」，等答好先做。
- 修完報告一句：修咗咩、而家點。

## 開每週檢查
用家答應先開。用 cronjob 工具：

```
cronjob(action="create", skill="homer-doctor",
        prompt="做每週健康檢查，用白話報告，唔好自己修任何嘢。",
        schedule="0 20 * * 0", name="Homer 醫生：每週健康檢查")
```

（逢星期日晚 8 點。）開完同用家講：「每個禮拜日晚 8 點會出報告，部電腦要開住先會行。」

## English users
Same checks and rules; report in English, at most 5 lines. Never run `doctor --fix`, delete memories or restart anything without a clear yes.
