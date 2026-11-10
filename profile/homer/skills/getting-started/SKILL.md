---
name: getting-started
description: "開工精靈：問 3 條問題，幫用家開好每日要做嘅排程同合用嘅技能，唔使自己研究點設定。Getting-started wizard: three questions, then set up the user's daily routines and the right skills for them."
version: 1.0.0
author: Homer 出品
license: MIT
metadata:
  hermes:
    tags: [onboarding, setup, routines, 開工]
---

# 開工精靈

> 語言：所有同用家講嘅說話，用對方嘅語言。台灣用家（書面中文）用台灣慣用語，例如「按」「檔案」「軟體」；下面引號入面嘅句子只係意思參考。

目的：用家唔使自己研究 Hermes 點設定。你問 3 條問題，然後**幫佢開好**，佢只需要答「好」。

## 幾時用
- 第一次傾偈，而記憶入面冇「開工精靈已完成」。
- 搬完 Grok Bot 之後。
- 用家講「幫我設定」「開工精靈」「我唔知用你做咩」「set me up」。

## 規矩
- 每次只問一條問題，俾例子，答案越短越好。
- 開任何排程、裝任何技能之前，先列清楚會開咩，等用家答「好」。
- 最多開 3 樣嘢。開太多會亂，亦食 token。之後可以再加。

## 3 條問題

1. 「你平時做咩工作，或者最想我幫你處理生活邊方面？」（例：開網店、讀書、做 freelance 設計、搵樓）
2. 「每日或者每個禮拜，最想我**自己主動**做邊樣？」俾 3 個同佢答案相關嘅例子，例如：
   - 每朝整理今日要做嘅嘢
   - 每朝搵你行業嘅新聞重點
   - 每個禮拜五出週報
   - 留意競爭對手或者某件貨嘅價錢
   - 整理 email，淨係話你知要覆嘅
3. 「結果想喺邊度收？」——喺 Hermes 入面睇（預設，唔使設定），定係已經駁咗 Telegram／WhatsApp 之類（有先揀）。

## 開嘢

1. **搵技能**：用 skills 工具搵有冇啱用嘅現成技能（例如 email 整理、週報、價錢監察、競爭對手新聞），有就用，冇就淨係用排程加清楚嘅指示。唔好自己寫新技能，除非用家要求。
2. **列計劃**（最多 3 樣），每樣一行：做咩、幾時、用咩技能。例：
   「① 每朝 8:30 整理今日待辦（星期一至五）② 每個禮拜五 6 點出週報」
   問：「開唔開？」
3. **用家答好**：用 cronjob 工具逐樣開，例如：
   ```
   cronjob(action="create", skill="<技能名>", prompt="<清楚嘅中文指示>",
           schedule="every 1d at 08:30", name="每朝待辦")
   ```
   需要做嘢先要用家登入或者授權嘅（例如 email），先講清楚要佢做咩，唔好代佢輸入密碼。
4. **試行一次**：每樣開完，用 cronjob 工具即刻行一次（或者 `hermes -p homer cron run <id>`），將結果俾用家睇：「啱唔啱？要改就話我知。」
5. **Homer 醫生**：最後問：「要唔要我每個禮拜日幫你做一次身體檢查？有問題先話你知。」答好就跟 `homer-doctor` 技能「開每週檢查」。
6. **記低**：用 memory 工具加一條：`開工精靈已完成（日期）：開咗 ①… ②…；用家做：…`

## 收尾一句
「搞掂。部電腦要開住排程先會行。想加嘢、改時間，直接同我講就得。」

## English users
Same flow in English: three questions, at most three routines, list the plan and wait for a yes, run each once so they can see it, offer the weekly Homer Doctor check, then save one memory note.
