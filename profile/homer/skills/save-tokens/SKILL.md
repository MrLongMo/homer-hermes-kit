---
name: save-tokens
description: "幫用家慳 token／慳額度：檢查設定、解釋邊度食得多、建議改法（改之前一定問）。Help the user cut token use and cost."
version: 1.0.0
author: Homer 出品
license: MIT
metadata:
  hermes:
    tags: [cost, tokens, 慳錢, quota]
---

# 慳 token

> 語言：所有同用家講嘅說話，用對方嘅語言。台灣用家（書面中文）用台灣慣用語，例如「按」「檔案」「軟體」；下面引號入面嘅句子只係意思參考。

用家嫌貴、爆額度、問點慳，就用呢個技能。每個建議都要講「點解慳」同「代價係咩」，改設定之前一定先問。

## 先睇數據，唔好估
- 行 `hermes -p homer insights --days 7`（冇呢個指令就跳過），用白話講：邊個模型、邊類工作食得最多。
- Desktop 用家：叫佢喺對話上面撳右鍵開「Cache hit rate」。命中率越高越平。

## 五招（由最易做起）
1. **長對話開新 chat**：舊對話越長，每句都要重新讀晒成段。換話題就 Ctrl/Cmd+N 開新 chat。
2. **唔好喺對話中途轉模型**：轉模型會令 prompt cache 失效，下一句要用全價重讀成段對話。
3. **早啲壓縮**：而家設定喺用到 40% context 就自動壓縮（Homer 預設）。對話好長仍然貴，可以再調低：
   `hermes -p homer config set compression.threshold 0.35`（代價：好耐之前講過嘅細節可能記唔清）。
4. **側邊工作用平模型**：壓縮、改標題呢啲雜務唔使用最強模型。Homer 預設已經將佢哋嘅思考程度調低。
5. **主力換平模型**（用家同意先做）：日常傾偈用 DeepSeek 一類平模型，整圖繼續用 Grok。
   - 佢要有 OpenRouter key（openrouter.ai 自己開，自己充值）。
   - Desktop：Settings → Model → Main model 揀 OpenRouter 同模型，撳 Apply。
   - 代價：難題表現可能差過 Grok；整圖照舊用 Grok Imagine，唔受影響。

## 唔好做
- 唔好擅自改佢 config。
- 唔好推介來歷不明、平到唔合理嘅「中轉站」API。對話會經人哋伺服器，戶口亦可能隨時被封。
