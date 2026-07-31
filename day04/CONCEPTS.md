# 延伸知識：logging 與 exit code 是給「下一個程式」看的，不是給你看的

## `print()` 跟 `logging` 的根本差別

`print()` 是給**當下坐在終端機前的人**看的。`logging` 是給**任何時候、任何人（或任何自動化系統）**回頭查的：它自帶時間戳記、等級（INFO/ERROR/DEBUG）、可以同時寫進檔案又輸出到畫面、可以依等級篩選、可以之後接上正式環境的監控系統。這也是為什麼規格禁止用 `print()` 寫 log——`print()` 沒有等級、沒有時間、關掉終端機就什麼都沒留下。

實務上一個工具通常會有兩條輸出管道，各自用途不同：

- **stdout（標準輸出）**：程式正常的「結果」，例如 JSON 報告內容——設計上應該可以被下一個程式用 `|` 接走（pipe，管線）處理。
- **stderr（標準錯誤輸出）**：錯誤訊息、警告、進度提示——即使 stdout 被導向檔案，stderr 仍然會顯示在終端機上讓人看到。

這就是規格要求「錯誤同時輸出到 stderr」的理由：如果你的錯誤訊息混進 stdout，下一個讀你輸出的程式（可能就是另一個腳本，也可能是 AI agent 呼叫你這個 CLI 工具）會把錯誤訊息誤認為是正常結果去解析，然後在更下游炸開。

## Exit code 的存在，是因為 shell 不會讀你的錯誤訊息

一支程式執行完後的 exit code（結束狀態碼）是它跟外部世界溝通「發生了什麼」的唯一機械化管道。`$?`（bash 裡讀取上一個指令 exit code 的變數）、CI/CD pipeline、`gate.py` 呼叫 `pytest` 時判斷成不成功——全部都是看 exit code，不是去解析你印出來的文字。這也是為什麼要把不同的失敗原因對應到不同的 code（檔案不存在 = 2、TOML 錯誤 = 3……）：呼叫端可以不看任何文字，只憑數字就知道「這次是設定檔案的問題，不是輸出的問題」，進而決定要不要重試、要不要中斷整個流程。

這組慣例其實呼應 Unix 傳統的 `sysexits.h`（`EX_USAGE=64`、`EX_NOINPUT=66` 之類），不同專案的具體數字不會完全一樣，但「用不同數字區分不同失敗原因」這個精神是共通的。

## `raise SystemExit(main())`：exit code 從「一個 int」變成「程式真正的結束狀態」的那一行

`main()` 回傳 `2` 只是一個普通的 Python `int`，本身不會讓程式的結束狀態碼變成 2——`return 2` 跟任何函式回傳任何一個數字沒有差別。真正讓這個數字變成 shell 看到的 exit code 的，是每天 `solution.py` 結尾那行 `raise SystemExit(main())`：`SystemExit` 是 Python 直譯器認得的特殊例外，最外層看到它時會直接用你給的整數結束程式，不印 traceback（跟其他例外會印一堆錯誤堆疊不一樣）。`sys.exit(code)` 做的是同一件事（它內部就是 `raise SystemExit(code)`），這套訓練的骨架選擇顯式寫 `raise SystemExit(...)`，效果相同。

如果哪天你把這行改成單純呼叫 `main()`（不包 `SystemExit`），不管 `main()` 內部回傳 `0`、`2` 還是 `5`，程式對外的結束狀態碼永遠是 `0`——這個表格裡辛苦分出來的五種 exit code，會在這一行被全部抹平成「成功」。這是這天最容易被忽略、卻決定整張 exit code 表格是不是真的有意義的一行程式碼。

## 自訂例外類別：把「錯誤種類」變成型別，不是變成訊息字串

這天的錯誤全部用內建的例外類型（`ValueError`、`FileNotFoundError`……），這在單一檔案的小工具裡沒問題。但當程式變大、錯誤來源變多之後，光用內建型別會遇到一個具體問題：**`ValueError` 太籠統**，「TOML 欄位型別錯」跟「數值超出範圍」如果都拋 `ValueError`，最外層要決定該對應哪個 exit code 時，只能去讀錯誤訊息字串裡有沒有包含特定關鍵字——這種寫法一旦訊息文字改了（例如你把中文訊息換成英文），判斷邏輯就會悄悄失效,而且不會有任何警告。

自訂例外類別解決的正是這個問題：

```python
class ConfigError(Exception):
    """設定檔驗證失敗。"""

class TomlSyntaxError(ConfigError):
    """TOML 語法本身有誤。"""

class FieldValidationError(ConfigError):
    """欄位存在但值不合法。"""
```

`class X(Exception):` 就能定義一個新的例外型別——繼承 `Exception`（或繼承某個更具體的內建例外，例如 `ValueError`）即可，通常不需要額外寫任何方法，一個 `pass` 或一句 docstring 就夠了。**重點不是類別內部有什麼，是「型別本身」變成了一個可以被 `except` 精確捕捉、可以被 `isinstance` 判斷的東西**：

```python
try:
    load_config(path)
except TomlSyntaxError:
    return 3
except FieldValidationError:
    return 4
```

呼叫端現在是靠**型別**分派 exit code，不是靠解析錯誤訊息裡有沒有某個字——訊息文字愛怎麼改都可以改,不會影響這段判斷邏輯。這也是為什麼設計自己的例外時，通常會像上面一樣建一個共同的基底類別（`ConfigError`）：想廣泛捕捉「任何設定相關的錯誤」時 `except ConfigError`，想精確處理某一種時 `except TomlSyntaxError`——兩種粒度都保留,呼叫端自己選要接住哪一層。這天不強制要求你定義自訂例外類別（規格允許直接用內建型別），但這是後面 day13～14 期末專案會用到的技巧：模組一多、失敗原因一多，自訂例外類別會比到處检查訊息字串可靠得多。

## `except Exception: pass` 為什麼是 AI 生成程式碼裡最常見、也最危險的地雷

叫 AI「幫我處理一下錯誤」，很容易得到這種寫法：

```python
try:
    do_something()
except Exception:
    pass
```

表面上「程式不會當掉」，實際上是把所有錯誤資訊都丟掉——包括你完全沒預期到、可能代表更嚴重問題的錯誤（例如硬碟寫滿、記憶體不足）。你會看到程式安靜地「跑完」，但結果是錯的，而且你完全不知道哪裡開始錯。規格要求「若最外層捕捉廣泛例外，必須記錄原因」，意思是至少要 `logging.error(..., exc_info=True)` 把發生了什麼寫下來——**捕捉例外的目的是為了優雅處理或留下線索，不是為了讓錯誤消失。**

看 AI 生成的程式碼時，`except Exception` 或裸的 `except:` 幾乎值得每次都停下來問一句：「這裡吞掉的錯誤，如果真的發生，我還能不能查出原因？」
