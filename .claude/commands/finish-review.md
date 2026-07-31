---
description: 對某一天(或 final_project)跑 gate.py finish，成功後直接用 reviewer 子代理評分，一步到位。
argument-hint: <dayXX|final_project> <y|n> [--force]
---

使用者輸入：$ARGUMENTS

請依下列步驟執行，不要跳過或合併：

1. 解析輸入，取得：
   - `目錄`：第一個 token，例如 `day05` 或 `final_project`。
   - `declare`：第二個 token，必須是 `y` 或 `n`——這是使用者對「前 20 分鐘是否完全沒有讓 AI 產生或提供程式碼」的誠實回答，直接照使用者給的值傳下去，不要自己判斷或代答。
   - `--force`：若輸入中包含 `--force`，之後傳給 gate.py。
   - 若缺少 `目錄` 或 `declare`，停止並詢問使用者補齊，不要用預設值猜測誠實聲明。

2. 用 Bash 在 `<目錄>` 底下執行：
   ```
   python ../gate.py finish --declare <declare> [--force]
   ```

3. 檢查 exit code：
   - 非 0（例如時間未到又沒加 `--force`）：把 gate.py 印出的訊息原樣告訴使用者，並停止，不要呼叫 reviewer。
   - 0：繼續下一步。

4. 呼叫 `reviewer` 子代理，對 `<目錄>` 評分（依 `.claude/agents/reviewer.md` 的規則，讀 RUBRIC.md / SPEC.md / AI_POLICY.md 與該目錄內容，不要只憑 .gate_report.md 的節錄）。

5. 把 reviewer 的評分結果原樣回報給使用者。
