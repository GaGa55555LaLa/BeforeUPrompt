# 貢獻指南

謝謝你考慮貢獻這個專案。這是一套 Python 獨立實作訓練教材，不是一般軟體專案——多數檔案是教材內容（`README.md`／`CONCEPTS.md`），少數是輔助工具（`gate.py`、`check_submission.py`）。貢獻的方式跟一般開源專案不太一樣，請先讀完這份文件再動手。

## 這個專案歡迎的貢獻

- **修正錯誤**：規格描述不清楚、範例輸入輸出算錯、`CONCEPTS.md` 裡的技術說明有誤、`gate.py`／`check_submission.py` 的 bug。
- **改進說明**：讓某段 `CONCEPTS.md` 更清楚、補充遺漏的邊界案例、修正術語解釋。
- **提議新的一天／新主題**：如果你發現某個實務上常見的 Python 主題完全沒被涵蓋，歡迎提議。**請先開 Issue 討論，不要直接送一個完整的新一天的 PR**——難度該放在哪個位置（現有天數是刻意由淺到深排列的）、跟哪幾天銜接，這些最好先對過。
- **修正 typo、格式問題**。

## 這個專案不歡迎的貢獻

- **不要 PR 你自己寫好的 `solution.py`、填好的 `notes.md`／`ai_usage.md`**。這些檔案在 repo 裡刻意保持空白骨架（`# TODO: implement according to README.md`）——它們是每個學習者自己要完成的練習，不是等人補完的缺漏。你自己練習時當然會填寫這些檔案，但那是你自己 fork／clone 之後的本地內容，不要送回上游。如果你想貢獻「範例解答」，請先開 Issue 討論要不要用，以及放在哪裡（例如獨立的 `solutions/` 分支或 fork，不會混進主要教材結構）。
- **不要在核心 14 天（day01～14）裡引入第三方套件依賴**。`SPEC.md` 明確規定「除 pytest 外，不得依賴第三方套件」，這是刻意的限制，不是疏漏。延伸天數（day15 之後）如果需要引入新工具（像 `ruff`／`mypy`），請在 PR 說明裡解釋為什麼這是例外。
- **不要把延伸（選修）天數改成核心要求**，或反過來把核心天數搬到延伸區——`README.md`／`CHECKLIST.md` 對「兩週核心」跟「選修延伸」的邊界是刻意畫的。

## 修改既有內容前，先想清楚影響範圍

- `SPEC.md`、`AI_POLICY.md`、`RUBRIC.md` 是跨全部天數的全域規則。改動這幾份文件會影響所有天的驗收標準跟 `reviewer` 子代理的評分依據，**請先開 Issue 討論**，不要直接送 PR。
- 修改某一天的 `README.md`（規格）時，記得同步檢查：`solution.py`／`test_solution.py` 的骨架註解是否還對得上、`CONCEPTS.md` 裡引用到的範例值是否一致、有沒有其他天的 `README.md`／`CONCEPTS.md` 用 `dayXX` 字樣交叉引用到這一天（改了規格但漏改交叉引用，是這個專案最容易犯的錯）。

## 新增一天的檔案結構

如果 Issue 討論後決定要新增一天，請完整比照現有天數的結構（可以直接參考任何一個 `dayXX/` 目錄）：

```text
dayXX/
├── README.md       # 規格：目標／執行／規則／測試數量／口頭驗收／延伸知識指標
├── CONCEPTS.md      # 延伸知識：為什麼要這樣設計、AI 生成程式碼常見的地雷
├── solution.py       # 空骨架，只有 TODO，不是解答
├── test_solution.py  # 只有一個 placeholder 測試
├── notes.md          # 從 templates/notes.md 複製
└── ai_usage.md       # 從 templates/ai_usage.md 複製
```

- `solution.py`／`test_solution.py` 的骨架請直接照抄任一天現有的寫法（`"""Day XX solution."""` docstring、`def main() -> int:`、`if __name__ == "__main__":` 那一段），保持全專案一致。
- 難度必須放在正確的相對位置——如果是核心天數，接在 day14 之前插入會牽動後面所有天的編號，請在 Issue 討論階段先確認清楚要放哪裡；如果是延伸天數，難度必須比前一個延伸天數更深（`README.md` 的延伸區段開頭寫明「難度由淺到深排列」）。
- 新增的一天要同步更新：根目錄 `README.md` 的天數清單、`CHECKLIST.md` 對應階段的檢查項目。核心天數（day01～14）還要更新 `check_submission.py` 裡的 `range(1, 15)`。

## 寫作風格

這個專案的 `CONCEPTS.md` 有一套固定的寫作慣例，PR 裡新增或修改的內容請照這個風格寫，不要換一套文風：

- 全部使用繁體中文；程式碼、術語、函式庫名稱維持英文。
- 術語第一次出現時，用括號附白話解釋，例如「pure function（純函式，只依輸入計算結果）」——不要假設讀者已經知道這個領域的術語。
- 不要寫「這個功能是做什麼」的描述性文字，要寫「為什麼要這樣設計」「AI 生成的程式碼常見的地雷長什麼樣」——這是這份教材跟一般 Python 教學文件最大的差別。
- 具體、有實際程式碼片段佐證，避免空泛的原則性句子。
- 程式碼骨架本身不寫多行註解說明（教材類的解釋放在 `CONCEPTS.md`，不是程式碼註解裡）。

## 送出 PR 前

1. 在你修改到的每個 `dayXX/`（或 `final_project/`）目錄下執行 `pytest -v`，確認通過。
2. 在 repo 根目錄執行 `python check_submission.py`，確認目錄結構檢查沒問題。
3. 如果修改了 `gate.py`／`check_submission.py`，執行 `ruff check` 跟 `mypy`（見 `requirements-dev.txt`）。
4. 如果你的 PR 內容主要由 AI 生成（例如請 AI 幫忙寫一整段 `CONCEPTS.md`），請在 PR 說明裡註明，並確認你自己讀過、驗證過內容正確——這呼應 `AI_POLICY.md` 對這整個專案的核心要求：AI 是加速器，不是答案來源，對貢獻者自己也一樣適用。

## 行為準則

參與這個專案的討論與貢獻，請遵守 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)。

## 授權

貢獻進這個專案的內容，會以 [MIT License](LICENSE) 授權釋出，跟專案其他部分一致。
