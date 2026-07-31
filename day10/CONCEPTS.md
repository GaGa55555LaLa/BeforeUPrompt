# 延伸知識：`dataclass` 解決的問題是什麼，什麼時候不需要它

## 從巢狀 dict 換成 dataclass，實際換到了什麼

在這天之前，資料大概都是用 `dict` 或元組傳來傳去，例如 `{"store": "S01", "item": "rice", "price": 1.0, "priced": True}`。這樣寫的問題是：**沒有任何東西保證這個 dict 一定長這樣**——打錯欄位名稱（`"stroe"`）不會有任何提示,直到執行到某處才因為 `KeyError` 爆掉；IDE 也沒辦法自動完成欄位名稱，因為對它來說 `dict` 就是任意 key 的容器。

```python
@dataclass(frozen=True)
class PriceRecord:
    store: str
    item: str
    price: float
    priced: bool
```

換成 `dataclass`，`result.store` 打錯字會直接被 IDE、`mypy` 抓到（`AttributeError` 或型別檢查失敗），而且建構時如果少給一個欄位，`PriceRecord(store="S01", item="rice")` 會直接在建立的那一行報錯——**錢包破洞出現在你把手伸進去的地方,不是在後面某個用到它的地方才發現裡面少了東西。**

## `frozen=True` 的實務意義：不是效能優化，是防止意外修改

`frozen=True` 讓這個物件建立後不能再改欄位值（`result.price = 999` 會直接拋 `FrozenInstanceError`）。這在「這份資料代表已經發生過的一筆記錄」的情境下特別合理——**一筆已經記錄的價格，理論上不應該在程式跑到一半被任何函式偷偷改掉**。如果你發現程式某處「需要」修改一個 frozen 物件的欄位，那通常代表你要的其實是「用舊資料建一個新物件」（`dataclasses.replace(result, price=new_price)`），而不是真的要改變過去發生的事實——這個限制本身就是在提醒你資料流向該怎麼設計。

## `dataclass` vs. `dict` vs. `pydantic`：AI 會怎麼選，你要怎麼判斷

- **`dict`**：最快、最省事，但完全沒有結構保證，欄位名稱、型別都要靠你自己記住或到處寫檢查。適合真的很臨時、資料形狀本來就會變動的場景。
- **`dataclass`**（標準庫，這天用的）：宣告欄位跟型別，Python 自動幫你生成 `__init__`、`__eq__`、`__repr__`，但**不會在執行期強制檢查型別**——`PriceRecord(store=123, ...)` 不會報錯，因為 Python 的型別標註本質上只是給人跟工具看的提示，不是執行期的守衛。
- **`pydantic`**（第三方套件）：宣告方式跟 `dataclass` 很像，但**會在執行期真的驗證型別跟限制條件**，資料不合規會直接拋出清楚的驗證錯誤。這也是為什麼很多 AI 生成的「資料驗證」程式碼會直覺選 `pydantic`——它把 day03 手寫的那堆 `if` 檢查變成宣告式的：

```python
from pydantic import BaseModel, Field, field_validator

class PriceRecord(BaseModel):
    store: str
    item: str
    price: float = Field(gt=0)          # 宣告即驗證：price 必須 > 0，不用自己寫 if
    priced: bool

    @field_validator("store")
    @classmethod
    def store_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("store 不得為空白")
        return v
```

`PriceRecord(store="S01", item="rice", price=-1.0, priced=True)` 這行會在**建構的當下**直接拋出 `pydantic.ValidationError`，訊息會清楚指出是哪個欄位、違反了哪條規則——`Field(gt=0)` 這種寫法把「大於 0」這條驗證規則直接寫進欄位宣告，`field_validator` 則是「這個欄位需要自訂邏輯時」的逃生口（跟這天你自己手寫的驗證函式做的是同一件事，只是宣告式寫法把規則跟欄位定義放在同一個地方，不用另外去某個函式裡找）。

這個訓練專案限制不能用第三方套件，所以這天特意讓你用 `dataclass` + 手寫驗證函式模擬 `pydantic` 幫你做的事——**理解「`dataclass` 本身不驗證」這個限制，你才會知道為什麼規格要求你在建立 `PriceRecord` 之前，要先跑過一輪驗證邏輯，不能指望型別標註幫你擋住壞資料。** 讀 AI 生成、用了 `pydantic` 的程式碼時，看到 `Field(...)` 裡的限制條件，可以直接對應到「這條規則如果我自己手寫驗證函式，會寫成哪一個 `if`」——兩者在做的事情完全一樣，只是語法外觀不同。

## `dataclass` 也可以繼承、也可以有計算出來的欄位

這天的 `PriceRecord` 是單一、扁平的 dataclass，沒有繼承任何東西。真實世界的 dataclass 常常會疊上更多機制：

```python
from dataclasses import dataclass, field

@dataclass(frozen=True)
class Record:
    store: str
    item: str

@dataclass(frozen=True)
class PriceRecord(Record):        # 繼承另一個 dataclass，新增自己的欄位
    price: float
    priced: bool
    tags: list[str] = field(default_factory=list)   # 預設值是「呼叫這個函式產生新物件」

    def __post_init__(self) -> None:
        if self.price < 0:
            raise ValueError(f"price 不得為負數：{self.price}")

    @property
    def display_name(self) -> str:            # 看起來像欄位，實際上是每次呼叫都重新計算的方法
        return f"{self.store}/{self.item}"
```

- **繼承**：`PriceRecord(Record)` 直接拿到 `Record` 的 `store`、`item` 兩個欄位，只需要宣告新增的部分——跟 day18 會講的 class 繼承是同一套機制，dataclass 只是自動幫你生成 `__init__` 而已，繼承規則沒有變。
- **`field(default_factory=list)`**：day13/`CONCEPTS.md` 提過 `def f(x=[])` 是地雷，因為預設值只在函式定義時建立一次。`dataclass` 的欄位預設值也有同樣的風險，所以標準庫直接提供 `default_factory`——不是給一個值，是給一個「沒有人傳值時，呼叫這個函式產生一個新的」，`list` 本身就是這樣的函式（呼叫 `list()` 得到一個新的空 list）。
- **`__post_init__`**：`dataclass` 自動生成的 `__init__` 跑完以後，會自動呼叫這個方法（如果你定義了它）——這是在「建構完成後」加一段驗證或計算的標準位置,不用自己手動改寫 `__init__`。
- **`@property`**：讓一個方法可以用「屬性存取」的語法呼叫（`record.display_name`，不是 `record.display_name()`），但背後其實是每次存取都重新執行一次計算——適合「這個值可以從其他欄位算出來，不需要真的存成一個欄位」的情境（存成獨立欄位反而要擔心跟來源欄位不同步的問題）。

這天不要求你用到這些機制（`PriceRecord` 保持扁平、沒有繼承就夠了），但這些是你之後讀到任何比這天複雜一點的 dataclass 時，幾乎一定會遇到的組合。

## 「不得全用巢狀 dictionary 取代資料模型」在防什麼

如果你在該用 `PriceRecord` 的地方，還是持續傳遞 `{"store": ..., "item": ...}` 這種 dict，你等於是繞過了剛剛建立好的資料模型，那 `dataclass` 帶來的所有好處（型別提示、欄位保證、`frozen` 限制）在那條路徑上就完全失效了——**定義一個資料模型的價值在於你真的貫徹使用它,不是定義完就丟在旁邊,程式主體仍然用鬆散的 dict 傳資料。** 看 AI 生成的程式碼時，這是個具體的檢查點：它宣告了一個漂亮的 `dataclass`，但實際的函式呼叫鏈裡，是不是又默默改用 dict 或散裝的位置參數傳資料？

## `match`/`case`：`if`/`elif` 鏈的另一種寫法

這天把 coverage 分成 `Priced`／`Estimated`／`Invalid` 三種，多半會寫成 `if coverage == 1.0: ... elif coverage >= threshold: ... else: ...`。Python 3.10 起多了一種語法可以表達同一件事：

```python
match coverage:
    case c if c == 1.0:
        basis = "Priced"
    case c if c >= threshold:
        basis = "Estimated"
    case _:
        basis = "Invalid"
```

`match`/`case`（structural pattern matching，結構化模式比對）在這種「依數值範圍分支」的情境下,跟 `if`/`elif` 比起來沒有本質差別，只是語法外觀不同——**它真正好用的場景，是比對資料的「形狀」**，例如判斷一個 tuple 有幾個元素、dict 裡有沒有特定 key：

```python
match parsed_row:
    case {"store": store, "item": item, "price": price}:
        ...   # 這個 dict 剛好有這三個 key
    case _:
        raise ValueError("缺少必要欄位")
```

這天不要求用 `match`/`case`（`if`/`elif` 完全夠用），但看到 AI 生成的程式碼用這個語法時，先確認它是不是真的在比對「資料形狀」——如果只是拿來取代單純的數值範圍判斷，跟 `if`/`elif` 效果一樣，選哪個純粹是風格問題。

## `frozen=True` 保護不到的地方：欄位本身是 mutable 物件時

`frozen=True` 只擋住「重新綁定欄位」（`result.price = 999`），**它擋不住「欄位裡面那個物件本身被就地修改」**。舉個會讓人踩到的例子：

```python
@dataclass(frozen=True)
class StoreSummary:
    name: str
    items: list[str]      # 欄位是個 list，這是個地雷

s = StoreSummary(name="S01", items=["rice", "milk"])
s.items.append("eggs")  # 這行完全合法，不會拋 FrozenInstanceError
```

`s.items` 本身沒有被「重新賦值」，只是被呼叫了它的 `.append()` 方法——`frozen` 檢查的是「這個名字有沒有被重新綁到另一個物件」，不是「這個名字指到的物件內容有沒有變」。**如果一個 dataclass 的欄位型別是 `list`、`dict` 這類 mutable 容器，`frozen=True` 給你的不變性保證其實是有漏洞的。** 這也是為什麼 `PriceRecord` 這天的欄位刻意都是 `str`/`float`/`bool`（全部不可變）——只要所有欄位都是不可變型別，`frozen=True` 才是真正滴水不漏的保證。如果之後你自己設計的資料模型需要裝一個 list，通常會改成裝 `tuple`（不可變序列），道理跟這裡一樣。

## 巢狀結構傳進函式：shallow copy 為什麼不夠

day01 提過用 `values[:]` 複製一份 list 來避免動到呼叫端的原始資料，那是 shallow copy（淺拷貝）：只複製最外層容器，裡面的元素仍然是同一批物件。當元素是不可變的 `float` 時這樣就夠了，因為你不可能「就地修改」一個 float。但如果是 `list[dict]`（例如一批 `{"store": ..., "price": ...}`）：

```python
import copy
backup = original[:]        # 淺拷貝：backup 是新的 list，但裡面的每個 dict 還是同一個物件
backup[0]["price"] = 999    # 這行會連帶改到 original[0]，因為兩邊的第一個元素是同一個 dict
```

要真正切斷所有層級的關聯，需要 `copy.deepcopy(original)`——遞迴複製每一層。這件事在效能上不是免費的（資料越大越深，複製越貴），所以實務上更常見的解法不是「每次都 deepcopy 求心安」，而是**設計上讓資料一路都是不可變的**（像這天用 `frozen=True` 的 dataclass、或上一段講的用 `tuple` 取代 `list`）——不可變資料不需要複製就是安全的，因為根本沒有「就地修改」這個動作可以做。這也是為什麼 functional programming（函式化程式設計）風格的程式碼偏好不可變資料結構：省掉一整類因為別名（aliasing）造成的意外修改問題。
