# 延伸知識：CLI 介面實務上怎麼設計——用 `gate.py` 當活教材

這天的主題是 `argparse`，但更大的主題是「一個命令列工具的介面應該怎麼設計」。你不用去外面找範例——**`../gate.py` 本身就是一個活生生的案例**，而且你已經親手改過它了。

## `--help` 是怎麼生成的，為什麼值得認真寫

跑 `python ../gate.py --help` 或 `python ../gate.py finish --help` 時看到的說明文字，不是你手打的一大段文字，是 `argparse` 根據你在 `add_argument()` 裡寫的 `help=` 參數自動組出來的。這代表：**你多花一分鐘寫清楚 `help=` 的內容，之後每個使用這個工具的人（包括你自己三個月後）都不用重新讀程式碼就能知道這個參數是幹什麼的。** 看 `gate.py` 現在的 `p_finish.add_argument("--declare", ...)`，`help=` 裡寫的是「非互動地提供誠實聲明……不給則照舊互動詢問」——這句話同時講了「這個參數做什麼」跟「不給的時候會怎樣」，這是好的 help 文字該有的密度：讓人不用去猜預設行為。

反面案例是 AI 生成 CLI 常見的問題：`help="設定選項"` 這種空洞到跟沒寫一樣的說明，或者乾脆不寫 `help=`，讓 `--help` 輸出一片空白。

## 子指令（subcommand）模式：`start` / `status` / `finish` 為什麼不是三個獨立的 flag

`gate.py` 用 `sub.add_parser("start", ...)`、`sub.add_parser("finish", ...)` 建立的是**子指令**，每個子指令有自己獨立的一組參數（`start` 有 `--minutes`、`--force`；`finish` 有自己的 `--force`、`--declare`、`--review`）。這跟 `git commit`、`git push`、`docker run` 是同一套模式：**當一個工具要做的事情本質上是幾種不同的「動作」，而不是同一個動作的幾種變化，用子指令比用一堆互斥的 flag 清楚。** 如果硬要把 `start`/`status`/`finish` 塞成同一層的三個 flag（例如 `--start`、`--status`、`--finish`），使用者還要自己搞清楚這三個 flag 是互斥的、不能同時給，`argparse` 也沒辦法自動幫你檢查「這三個只能選一個」——子指令從結構上就排除了這種模糊空間。

## 為什麼兩個 `--force`（`start` 的跟 `finish` 的）是分開定義，卻共用同一個名字

`p_start.add_argument("--force", ...)` 跟 `p_finish.add_argument("--force", ...)` 是兩個獨立的參數定義，只是恰好同名、恰好都是 `action="store_true"`（出現就是 `True`，不出現就是 `False`，不需要接值）。這是刻意的設計：**同一個字面意思（強制執行、跳過某個檢查）用同一個名字，即使底層邏輯不同**，使用者不需要為每個子指令重新學一個新名字。這跟 `git commit --amend`、`git push --force` 那種「同一個 flag 名字在不同子指令下有各自意義，但語感一致」是同一個道理。

## `choices=["y", "n"]` 這種寫法在幫你做什麼

`--declare` 定義成 `choices=["y", "n"]`，代表如果有人打 `--declare maybe`，`argparse` 會在你的程式碼**執行前**直接報錯並印出合法選項，exit code 是 2（argparse 慣例：參數錯誤 = 2，這跟 day04 學的「用 exit code 區分錯誤種類」是同一套精神，只是這次是 `argparse` 内建幫你做掉）。**這代表你完全不需要在 `cmd_finish` 裡自己寫 `if declare not in ("y", "n"): raise ...`——把驗證邏輯搬到宣告參數的地方，離錯誤最近的地方擋下來，這正是 day03 學到的「盡早驗證」精神的 CLI 版本。**

## `add_argument_group`：參數一多，`--help` 也需要分段

這天只有 5 個參數，一次列出來還看得清楚。如果一個工具有 20 個參數，`--help` 印出來會是一長串看不出分類的清單。`argparse` 提供 `add_argument_group()` 讓你在 `--help` 輸出裡把參數分段：

```python
parser = argparse.ArgumentParser()
io_group = parser.add_argument_group("輸入輸出")
io_group.add_argument("--input", required=True)
io_group.add_argument("--output", required=True)

calc_group = parser.add_argument_group("計算選項")
calc_group.add_argument("--baseline", required=True)
calc_group.add_argument("--min-coverage", type=float, default=0.5)
```

**這只影響 `--help` 顯示的排版，不影響參數怎麼被解析**——`args.input`、`args.baseline` 存取方式完全不變。這天參數不多，不需要用到；但看到 AI 生成的、參數超過十個的 CLI 卻沒有分組，`--help` 輸出會是一堆難以一眼掃過的清單，這時候值得建議它加上分組。

## `build_parser` / `run` / `main(argv=None)` 分離，回到最實際的理由：可測試性

規格要求至少實作 `build_parser()`、`run(args)`、`main(argv: list[str] | None = None) -> int`，理由就是這天的口頭驗收要問的：**如果 `main()` 直接讀 `sys.argv`，你的測試就必須真的去操控全域的 `sys.argv`（用 `monkeypatch.setattr(sys, "argv", [...])`），測試之間互相影響的風險變高，而且沒辦法在同一個測試檔案裡輕鬆跑「用參數 A 跑一次、用參數 B 跑一次」。**如果 `main(argv=None)` 接受一個參數列表，不給就預設用 `sys.argv[1:]`，測試可以直接 `main(["--input", "x.csv", "--baseline", "S01"])`，跟呼叫一般函式沒有兩樣。

`gate.py` 目前的 `main()` 其實還是直接讀 `sys.argv`（沒有走 `argv=None` 這個模式），這是因為它是一支給人在終端機互動用的小工具，不是需要被大量單元測試覆蓋的核心邏輯——**這也是一個值得注意的設計判斷：不是每支程式都需要同一套嚴謹度，要看它的角色是什麼。** `day08` 要求你的 `solution.py` 走 `argv=None` 模式，是因為它未來可能被當作一個模組被其他程式或測試呼叫，跟 `gate.py` 的定位不同。

## AI 生成 CLI 工具時，實務上常見的兩個選擇與地雷

1. **常常直接建議用 `click` 或 `typer`**，因為裝飾器語法比 `argparse` 精簡好寫。這兩個都很好，是業界真實常用的第三方 CLI 框架——但這個訓練專案的 `SPEC.md` 明確禁止依賴第三方套件，所以如果你直接把 AI 生成的 `click` 版本貼上來，會直接違反規格。**判斷「AI 建議的工具是不是在這個專案的限制條件下能用」，是你自己要做的把關，AI 不會主動幫你檢查你的專案限制。**

2. **常常把所有邏輯塞進 `main()`，跳過 `build_parser`/`run` 的分離**，尤其是當你的提示詞只說「幫我寫一個讀 CSV 算平均的 CLI」而沒特別要求可測試性。這種版本乍看能跑，但你會發現規格要求的「至少兩個直接呼叫 `main([...])` 的測試」很難寫，因為所有邏輯都跟 `argparse` 綁在一起——這正是為什麼這天要求你自己動手拆過一次這個結構，往後看到 AI 生成的、沒拆過的 CLI 程式碼，你才能一眼看出「這個結構會讓測試很痛苦」。

## `click`／`typer` 實務上真的會用在什麼時候

這個訓練專案的 `SPEC.md` 禁止第三方套件，所以全程只用 `argparse`。但這不代表 `argparse` 在真實世界裡永遠是對的選擇——知道 `click`／`typer` 實際解決了什麼、什麼情境下值得多裝一個依賴，跟知道怎麼用 `argparse` 一樣重要：

- **`click`**：用裝飾器（decorator）宣告指令，例如 `@click.command()`、`@click.option("--baseline")`。比起 `argparse` 省下的主要是：子指令用 `@click.group()` 巢狀組合比 `sub.add_parser()` 精簡、內建 `click.testing.CliRunner` 讓測試 CLI 輸出更方便、內建互動式提示（`click.prompt`）、確認訊息（`click.confirm`）、進度條（`click.progressbar`）這些 `argparse` 完全沒有的 UX（User Experience，使用者體驗）功能、以及自動產生 shell 自動完成（autocomplete）腳本。
- **`typer`**：建在 `click` 上面，讓你直接從一般 Python 函式的型別標註產生 CLI 介面——你已經在寫 `def run(input_path: Path, baseline: str, min_coverage: float = 0.5) -> int` 這種型別標註了（`SPEC.md` 本來就要求），`typer` 讓這份型別標註本身就變成 CLI 參數定義，不需要像 `argparse`／`click` 那樣另外呼叫 `add_argument()`／`@click.option()` 重複宣告一次同樣的資訊。這對「函式簽名跟 CLI 參數幾乎一一對應」的工具特別省力,也是為什麼常跟 FastAPI（同一位作者、同一套「用型別標註生成介面」哲學的網路框架）搭配出現。
- **什麼時候該選哪個**：
  - 環境限制第三方依賴（企業內部管控、離線環境）、或工具本身只是個小型單一用途腳本（就像這個訓練專案裡的每一天）——`argparse` 是對的選擇：零依賴、標準庫本來就有、不需要額外說明「為什麼要多裝這個套件」。
  - CLI 本身是一個要長期維護、發行給別人用、有很多子指令的「產品」，而且你在意使用者體驗（顏色、進度條、互動提示、自動完成）——`click`／`typer` 省下的重複勞動跟提升的體驗，通常值得那一個依賴。
  - 團隊已經在用 FastAPI 或已經習慣「型別標註即介面」這種寫法——`typer` 通常比 `click` 更省力，因為你不用為同一份參數資訊多寫一次宣告。
  - 這天特別要你手刻 `build_parser`/`run`/`main(argv)` 這套可測試結構，也是因為 `click`（用 `CliRunner`）跟 `typer` 都已經內建幫你把這件事解決掉了——**先手刻過一次，你才知道那些框架的測試工具實際上幫你省掉了什麼，不是只會用,而不知道背後在解決什麼問題**。
