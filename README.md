# Python 獨立實作訓練

這份作業包的目標是恢復「從空白檔案開始，把需求轉成可執行、可測試程式」的能力，而不是要求完全不使用 AI。

**進度不是重點，看懂才是。** 每天標的 dayXX 只是難度遞增的順序，不是日曆上的天數，花三天搞懂 day03 也比為了趕進度含糊帶過好。真正的驗收標準是：你能不能看懂、解釋、並在需求改變時修改一份程式（包括 AI 幫你生成的程式），而不是「跑得動就過」。每個 `dayXX/` 底下除了規格 `README.md`，還有一份 `CONCEPTS.md`，那是延伸知識，講這個主題實務上（包括 AI Agent）通常怎麼設計、常見的地雷長什麼樣子。什麼時候看隨你：先看建立心智模型，或解完再看驗證自己的判斷，兩種都合理。

day01 開始就假設你已經會寫 `if`/`for`/`while`、認識 `list`/`dict`/`tuple`、會定義函式。這份訓練練的是「把需求變成程式」的能力，不是從零教語法。如果這些語法對你來說還有點生疏，先看 [`PRIMER.md`](PRIMER.md)（不計分、不進 `gate.py` 流程，純參考）。

## 開始前要讀的文件

除了每天的 `README.md`／`CONCEPTS.md`，下面幾份是**每天都會用到、不是只給 AI 看的**規則文件，開始 day01 前建議先過一遍：

| 文件 | 內容 | 什麼時候用 |
|---|---|---|
| [`SPEC.md`](SPEC.md) | 全域規格：函式拆分、型別標註、測試要求、每日提交結構、Git 要求 | 每天寫 `solution.py`／`test_solution.py` 時都要符合，不是只有第一天看一次 |
| [`AI_POLICY.md`](AI_POLICY.md) | AI 使用三階段（獨立實作／提示模式／審查模式）與「視為未完成」的情況 | 每天執行 `gate.py start` 前後都適用，`ai_usage.md` 要填的內容就是照這份規則寫 |
| [`RUBRIC.md`](RUBRIC.md) | 評分規則，六個項目怎麼配分 | 想知道 `reviewer` 子代理會怎麼打分數時查 |
| [`CHECKLIST.md`](CHECKLIST.md) | 每日／每階段的自我檢查清單 | 每天寫完、`gate.py finish` 前，拿來核對有沒有漏做什麼 |
| [`PRIMER.md`](PRIMER.md) | Python 基礎語法快速參考（不計分） | 上面提到的語法還生疏時查 |

## 環境

- Python 3.11 以上
- Git
- VS Code
- pytest（Python 常用的自動化測試框架）

```bash
python -m venv .venv
python -m pip install -r requirements-dev.txt
```

Windows PowerShell 啟用虛擬環境：

```powershell
.venv\Scripts\Activate.ps1
```

Linux / macOS：

```bash
source .venv/bin/activate
```

## 每日流程

1. 閱讀當天 `README.md`。
2. 在該日目錄下執行 `python ../gate.py start`，開始 20 分鐘獨立實作計時；期間禁止讓 AI 產生核心程式（完整三階段規則見 `AI_POLICY.md`）。
3. 先完成最小可執行版本。
4. 補上錯誤處理與測試（結構、測試覆蓋要求見 `SPEC.md`）。
5. 執行 `pytest -v`。
6. 填寫 `notes.md` 與 `ai_usage.md`（`ai_usage.md` 該寫什麼，對照 `AI_POLICY.md` 的三階段）。
7. 用 `CHECKLIST.md` 核對一次有沒有漏做的項目。
8. 執行 `python ../gate.py finish`，產生 `.gate_report.md` evidence 報告；再請 Claude Code 用 `reviewer` 子代理（見 `.claude/agents/reviewer.md`）對照 `RUBRIC.md` 評分，例如：「用 reviewer 幫我評 day05」。
9. 至少進行一次 Git commit。

單天核心實作約 50～70 分鐘，但這是下限不是上限，`CONCEPTS.md` 想看多久、要不要多做一輪重構練習，都是你自己抓。

## 完成標準

依這個順序做完全部 dayXX（不限定用幾天），應能：

- 從空白檔案完成 100～200 行的小型 Python 工具。
- 使用函式拆分需求。
- 處理檔案、CSV、JSON、TOML 與 CLI（Command-Line Interface，命令列介面）。
- 使用 pytest 測試正常與異常輸入。
- 閱讀、驗證及修改 AI 產生的程式。
- 解釋資料流、錯誤處理與設計選擇。

## 延伸（選修）：day15～19

不計入兩週核心天數，涵蓋前 14 天沒觸及、但實務上同樣常見的主題，難度由淺到深排列，流程與 `gate.py`／`reviewer` 用法跟前面完全相同：

- `day15/`：手動操作 `sys.path`，什麼情境下這是合理選擇（vendoring、plugin 系統、離線環境），怎麼寫成跟目前工作目錄無關、可重複呼叫不出現重複項目。
- `day16/`：`ruff`／`mypy` 這類靜態檢查工具在抓什麼、`conftest.py` 如何在不 import 的情況下讓多個測試共用 fixture、`@pytest.mark.parametrize` 何時該用、何時不該硬套。
- `day17/`：一般 class（有方法、有狀態，跟 day10 只裝資料的 `frozen dataclass` 不同）與 context manager（`with` 陳述式背後的 `__enter__`/`__exit__` 協定，以及 `contextlib.contextmanager`）。
- `day18/`：抽象基底類別（`ABC`／`@abstractmethod`）與「一個介面，多種實作」，真實專案裡最常見的物件導向設計模式，跟 day17 的差別是這天引入繼承。
- `day19/`：`asyncio` 基礎，`async`/`await`、`asyncio.gather` 的 fail-fast 模式、`time.sleep()` 誤用在 async 函式裡會悄悄吃掉並行效果的地雷。

## 貢獻

歡迎回報錯誤、改進說明、提議新主題，但請先看過 [`CONTRIBUTING.md`](CONTRIBUTING.md)，這個專案對「哪些貢獻歡迎」有一些跟一般軟體專案不同的限制（例如不收填好的練習解答）。參與討論與貢獻請遵守 [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md)。本專案以 [MIT License](LICENSE) 授權。
