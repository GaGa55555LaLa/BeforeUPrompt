# 延伸知識：「一個介面，多種實作」為什麼是真實專案裡最常見的物件導向模式

## `ABC`／`@abstractmethod` 實際在做什麼

day17 的 `PriceTracker` 是一個獨立的一般 class，沒有繼承任何東西。這天的 `PriceSource` 不一樣：它是一個 `ABC`（Abstract Base Class，抽象基底類別——本身不能被直接建立實例，只能被繼承），`fetch_price` 標了 `@abstractmethod`（抽象方法——宣告「繼承我的人一定要實作這個方法」，但不寫實作內容）。這不只是命名慣例或文件說明，是 Python 執行期真的會檢查的規則：

```python
PriceSource()   # TypeError: Can't instantiate abstract class PriceSource
                 # with abstract method fetch_price
```

如果你寫一個子類別繼承 `PriceSource`，卻忘了實作 `fetch_price`，那個子類別**也會被視為抽象**，一樣不能被建立實例——這個錯誤會在你嘗試 `建立實例` 的那一行就爆出來，不會等到你真的呼叫 `fetch_price()` 才發現「啊，這個方法根本沒寫」。**這是 `ABC` 存在的核心價值：把「這個子類別有沒有完整實作這個介面」這件事，從『可能某天執行到才發現』提前變成『建立實例的那一刻就檢查』。**

## 為什麼 `total_price()` 的參數要寫成 `PriceSource`，不是具體子類別

```python
def total_price(source: PriceSource, items: list[str]) -> float:
    return sum(source.fetch_price(item) for item in items)
```

這個函式完全不知道 `source` 到底是 `StaticPriceSource` 還是 `CsvPriceSource`，也不需要知道——它只依賴「這個物件有 `fetch_price` 這個方法」這個承諾，這個承諾正是 `PriceSource` 這個抽象型別在保證的事。這帶來一個具體的好處：**之後如果要加第三種資料來源（例如從某個外部服務查價），`total_price()` 一行都不用改**，只要新的類別一樣繼承 `PriceSource`、實作 `fetch_price`，就可以直接丟進 `total_price()` 用。反面案例是函式內部寫 `if isinstance(source, StaticPriceSource): ... elif isinstance(source, CsvPriceSource): ...`——這種寫法每加一種新來源就要回來改這個函式一次，而且這個函式必須認得所有具體類別的名字,完全違背了「呼叫端不該關心資料從哪來」的初衷。**這天規格明確禁止在 `total_price()` 裡用 `isinstance` 判斷，就是要你實際感受到「依賴抽象介面」跟「依賴具體型別」在程式碼可維護性上的差別，不是背一句口號。**

## Python 其實不強制要求 `ABC` 才能做到「多種實作」——那為什麼還要用它

Python 是動態型別語言，靠 duck typing（鴨子型別：只要一個物件有你需要的方法,就可以用,不管它宣告繼承自什麼）就能達到類似效果——你可以寫兩個完全沒有共同基底類別、只是「恰好都有 `fetch_price` 方法」的類別，`total_price()` 一樣能正常運作。**但不用 `ABC` 的話，「這兩個類別必須有 `fetch_price` 這個方法」這個約定,只存在於你腦中或文件裡，Python 不會幫你檢查。** 如果某個新來源的類別把方法名稱打錯成 `fetch_prices`（多了一個 s），duck typing 版本要等到真的呼叫到那一行才會 `AttributeError`；用 `ABC` 的話，這個類別因為沒有正確覆寫抽象方法，建立實例那一刻就會報錯。`ABC` 用的是「執行期會主動檢查的規則」取代「大家自己記住的口頭約定」，跟 day10 用 `frozen dataclass` 取代裸 `dict`、day13 用 `Enum` 取代裸字串，是同一種精神的第三次出現。

## AI 生成這種「多種實作」程式碼時常見的兩個問題

1. **假抽象**：AI 有時會用一般的 class 加上一句 docstring「子類別必須實作 `fetch_price`」，而不是真的用 `ABC`／`@abstractmethod`——這種寫法沒有任何執行期保護，忘了實作的子類別要等到真正呼叫時才會出錯，錯誤發生的時間點跟前面講的完全不同。看到「這個方法子類別必須覆寫」這種**只寫在註解或 docstring 裡、沒有用語言機制強制**的約定，值得直接改成 `ABC`。
2. **呼叫端用 `isinstance` 繞過抽象介面**：即使定義了漂亮的 `ABC`，AI 生成的呼叫端程式碼有時還是會忍不住寫 `if isinstance(source, StaticPriceSource): ...`——通常是因為某個子類別多了一個介面沒有宣告的方法，AI 想在呼叫端「特別處理」這個子類別。**這其實是個訊號：如果呼叫端需要知道具體類別才能用,代表這個抽象介面設計得不夠完整**，該做的是把那個「特別的行為」也加進抽象介面（讓所有子類別都要有，即使有些子類別的實作是「什麼都不做」），而不是讓呼叫端繞過抽象介面直接認子類別。

## 延伸（不要求實作）：如果三個 `fetch_price` 的回傳型別想不一樣怎麼辦

這天所有 `PriceSource` 的 `fetch_price` 都回傳 `float`，型別單純。真實世界的抽象基底類別有時會搭配 `typing.Generic`／`TypeVar` 讓「回傳型別」本身變成可以替換的參數（例如 `PriceSource[T]`，讓不同子類別可以回傳不同但一致的型別），這樣呼叫端的型別檢查工具還能推論出「這個特定 source 回傳的到底是什麼型別」。這個機制比較進階，這天不要求用到，但看到 class 名稱後面帶著 `[T]` 這種寫法（例如 `class Repository(Generic[T]):`），現在你知道那是同一種「介面 + 多種實作」精神，只是把「回傳型別也可以變」這件事也納入了介面設計。
