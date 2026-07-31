# 延伸知識：一般 class 跟 dataclass 差在哪，`with` 陳述式底層在做什麼

## day10 的 `frozen dataclass` vs 這天的一般 class：不是「哪個比較進階」，是「職責不同」

day10 的 `PriceRecord` 是 `@dataclass(frozen=True)`：它的角色單純是「裝資料」，欄位建立後不能改，Python 自動幫你生成 `__init__`、`__eq__`（比較兩個實例內容是否相等）、`__repr__`（印出來的樣子）。它沒有、也不該有會改變自己狀態的方法——`final_project/CONCEPTS.md` 提過的「跨模組傳遞的資料預設唯讀」，`frozen=True` 就是把這個原則變成語言層級會強制檢查的規則。

這天的 `PriceTracker` 完全相反：它的角色是「維護一組會隨時間變化的狀態」（不斷有新價格被 `add` 進來），而且對外提供的是「做一件事」的方法（`add`、`average`），不是單純的欄位存取。**判斷該用哪一種的簡單方法：如果這個東西的本質是「一份此刻拍下來的資料快照」，用 dataclass；如果本質是「一個會被持續操作、內部狀態會變的物件」，用一般 class。** AI 生成程式碼時常常把兩者混在一起——例如把一個明明會被反覆修改的物件寫成可變的 dataclass（沒加 `frozen=True`，靠大家自律不要亂改欄位），或者反過來把一個純資料結構寫成一般 class 卻塞了一堆不相關的方法。看到這種寫法，可以想想「這東西的本質到底是資料還是行為」。

## `self` 是什麼：方法怎麼知道要操作哪個實例

`def add(self, store: str, price: float) -> None` 裡的 `self` 代表「呼叫這個方法的那個實例本身」。`tracker.add("S01", 1.0)` 這句話，Python 實際上做的是 `PriceTracker.add(tracker, "S01", 1.0)`——`self` 就是 `tracker` 自己，被自動當成第一個參數傳進去。這也是為什麼 `__init__` 裡寫 `self.prices = {}` 之後，`add` 方法裡才能用 `self.prices[store].append(price)` 存取到同一份資料：**`self.xxx` 存取的是「這個特定實例」身上的屬性，不是這個 class 所有實例共用的東西**（除非你故意寫成 class 層級的屬性，那是另一個常見地雷，這裡不展開）。

## Context manager 協定：`with` 陳述式到底在呼叫什麼

`with Timer("parse") as t: ...` 這句話，Python 依序做的事情是：

1. 呼叫 `Timer("parse")` 建立實例，再呼叫它的 `__enter__()`，回傳值綁到 `as t` 後面的 `t`。
2. 執行 `with` 區塊裡的程式碼。
3. 不管區塊裡有沒有拋例外，離開時都呼叫 `__exit__(exc_type, exc_val, exc_tb)`——如果沒有例外，這三個參數都是 `None`；如果有例外，這三個參數會帶著例外的類型、內容跟 traceback。

**`__exit__` 的回傳值決定例外的命運**：回傳 `False`（或不寫 `return`，預設就是 `None`，等同 `False`）代表「我看過這個例外了，但請照常往外傳播」；回傳 `True` 代表「這個例外被我吞掉了，外面的程式碼完全不會知道剛剛發生過例外」。**這是一個真實存在的地雷**：如果你在 `__exit__` 裡隨手寫了 `return True`（或者寫了一段邏輯，某個分支不小心回傳了 truthy 值），你的 context manager 會悄悄吞掉所有經過它的例外——呼叫端的程式碼看起來正常執行完畢，實際上內部發生的錯誤完全被吃掉，這比讓例外正常拋出去更難除錯，因為連「有錯誤發生過」這件事都消失了。這天規格要求「`__exit__` 不得吞掉例外」，就是在逼你注意到這個回傳值有實際後果，不是隨便寫都一樣。

## `contextlib.contextmanager`：用 `yield` 寫 context manager 的另一條路

```python
from contextlib import contextmanager

@contextmanager
def timer(label: str):
    start = time.monotonic()
    try:
        yield
    finally:
        elapsed = time.monotonic() - start
        record(label, elapsed)
```

`yield` 之前的程式碼相當於 `__enter__`；`yield` 之後（包在 `finally` 裡）相當於 `__exit__`。**用 `finally` 而不是把記錄動作直接寫在 `yield` 後面，是關鍵**：`yield` 這一行如果 `with` 區塊拋了例外，例外會在這裡「冒出來」，如果沒有 `try/finally` 包住，`yield` 後面記錄耗時的程式碼根本不會執行到——這正好對應 class 版 `__exit__` 一定會被呼叫的保證，兩者要做到同一件事，寫法上的責任分配不同：class 版把「正常結束」跟「有例外」兩種情況揉在同一個 `__exit__` 裡用參數判斷，`generator` 版直接用 Python 本來就有的 `try/finally` 語法去表達「不管有沒有例外都要做的收尾動作」。**這也是為什麼這天要求兩種寫法都做一次**：讀別人程式碼時，這兩種 context manager 寫法在真實專案裡都很常見（`@contextmanager` 因為程式碼通常更短，AI 生成範例時更常用這個版本），能一眼看出兩者在做同一件事、只是語法外觀不同，才不會被表面差異卡住。

## AI 生成的 class 常見問題：職責塞太多、方法互相偷改對方沒預期會被改的狀態

請 AI 幫忙生成一個 class 時，很容易得到一個「什麼都做」的 class——例如同一個 `PriceTracker` 除了追蹤價格，還被塞進讀 CSV、寫 JSON、印報表這些不相關的職責（跟 day13 談的模組職責分離，其實是同一個原則，只是這次發生在單一 class 內部）。另一個常見問題是方法之間互相依賴內部細節：例如 `average()` 假設 `self.prices[store]` 一定是個 list，但另一個方法某個分支不小心把它寫成了單一數字——這種錯誤通常要到呼叫某個特定方法組合時才會現形，測試如果只各自測試單一方法、沒測「先呼叫 A 再呼叫 B」的組合，很容易漏掉。看到一個 class 的方法數量突然變多，或者方法之間開始互相假設對方會怎麼修改共用狀態，值得停下來想一下這個 class 是不是該拆成兩個。
