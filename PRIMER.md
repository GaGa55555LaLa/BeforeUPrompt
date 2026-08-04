# Python 基礎語法快速參考

這份文件**不計分、不進 `gate.py` 計時流程、不用 `reviewer` 評分**。它不是 day00，只是一份參考資料：`day01` 開始就假設你已經會寫 `if`/`for`/`while`、認識 `list`/`dict`，這份文件是給「這些東西看起來有點生疏，或從沒系統學過」的人，開始 day01 前先掃過一遍，或卡住時回來查。**如果以下內容你看了都覺得理所當然，直接跳去 day01 即可，不用從頭讀完。**

## 執行一段 Python 程式

```bash
python solution.py        # 執行一個檔案
python                     # 進入互動模式（REPL），一行一行執行，Ctrl+D 或 exit() 離開
```

這份訓練全程用第一種方式：把程式寫進 `.py` 檔案再執行，不是在互動模式裡累積程式碼。

## 變數與基本型別

Python 不用像 `int x = 5` 那樣宣告型別，變數在賦值的當下就決定了型別（這叫 dynamic typing，動態型別）：

```python
count = 5          # int（整數）
price = 12.5        # float（浮點數，有小數點）
name = "S01"        # str（字串）
in_stock = True     # bool（布林值，只有 True/False）
note = None         # None，代表「沒有值」，不是 0 也不是空字串
```

`type(x)` 可以查一個變數目前是什麼型別。同一個變數名稱之後可以重新指到不同型別的值（`count = 5` 之後寫 `count = "五"` 完全合法，只是通常不建議這樣做，會讓程式難懂）。

## 運算子

```python
7 + 3    # 10   加
7 - 3    # 4    減
7 * 3    # 21   乘
7 / 3    # 2.333...  除，結果一定是 float
7 // 3   # 2    整數除法（floor division，只取整數部分，向下取整）
7 % 3    # 1    取餘數（modulo）
7 ** 2   # 49   次方
```

比較運算子（`==` 等於、`!=` 不等於、`<`、`>`、`<=`、`>=`）回傳 `bool`。**`==` 是比較，`=` 是賦值，這是新手最容易打錯的地方**。

布林邏輯用 `and`、`or`、`not`（不是 `&&`/`||`/`!`）：

```python
is_valid = (price > 0) and (count <= 10)
```

### Truthy／falsy：`if` 判斷的不只是 `bool`

`if` 後面接的值不一定要是 `True`/`False`，Python 會自動判斷「這個值算不算真」：`0`、`0.0`、`""`（空字串）、`[]`（空 list）、`{}`（空 dict）、`None` 都算 falsy（視為假）；其他大多數值都算 truthy（視為真）。這代表 `if my_list:` 跟 `if len(my_list) > 0:` 效果一樣，但要小心：`if score:` 在 `score = 0` 時會被當成「沒有值」跳過，即使 `0` 是一個合法的分數。這正是這套訓練後面（day01）會提到的陷阱：為什麼不能用回傳 0 代表「沒有輸入」。

## 字串

```python
name = "  S01  "
name.strip()          # "S01"，去掉前後空白
name.lower()           # "  s01  "，轉小寫
"a,b,c".split(",")     # ["a", "b", "c"]，依分隔符拆成 list
",".join(["a", "b"])   # "a,b"，list 合併成字串，跟 split 相反
name.replace("S", "X") # 把某段文字換成另一段

price = 12.5
f"價格是 {price} 元"          # f-string：{} 裡可以直接放變數或運算式
f"價格是 {price:.2f} 元"      # 12.50，:.2f 控制小數位數
```

字串可以用索引跟切片（slicing）取子字串，索引從 0 開始：

```python
s = "hello"
s[0]      # "h"
s[-1]     # "o"，負數索引代表從尾端數
s[1:3]    # "el"，取索引 1 到 2（不包含 3）
```

字串是不可變的（immutable）：`s.replace(...)`、`s.strip()` 都是回傳一個新字串，不會改動原本的 `s`。

## 控制流程

**縮排決定程式碼區塊，不是 `{}`。** 同一層縮排（習慣上用 4 個空格）代表同一個區塊：

```python
if price <= 0:
    print("價格必須是正數")
elif price > 1000:
    print("價格異常，請確認")
else:
    print("正常")
```

`for` 迴圈遍歷一個序列（list、字串、`range()` 產生的數字序列……）：

```python
for item in ["rice", "milk", "eggs"]:
    print(item)

for i in range(3):        # 0, 1, 2（不包含 3）
    print(i)

for i, item in enumerate(["rice", "milk"]):   # 同時要索引跟值
    print(i, item)
```

`while` 迴圈依條件重複，直到條件變 falsy：

```python
count = 0
while count < 3:
    print(count)
    count += 1   # 等同 count = count + 1，沒有 count++ 這種寫法
```

`break` 立刻跳出整個迴圈；`continue` 跳過這次迴圈剩下的部分，直接進下一次。

Python 3.10 起還多了 `match`/`case`，效果類似一連串 `if`/`elif`：

```python
match status_code:
    case 200:
        print("成功")
    case 404 | 500:          # | 表示「符合其中一個就算」
        print("失敗")
    case _:                    # _ 代表「其他所有情況」，等同 else
        print("未知狀態")
```

看到這個語法，先當成 `if`/`elif`/`else` 的另一種寫法即可，day10 的 `CONCEPTS.md` 會再講它真正好用的場景。

## 基本資料結構

```python
# list：有順序、可變、可重複
items = ["rice", "milk", "eggs"]
items[0]            # "rice"
items.append("oil") # 加到尾端
len(items)          # 4
"milk" in items      # True，檢查是否存在

# tuple：有順序、不可變，適合「這幾個值綁在一起,之後不會再改」的情境
point = (1.0, 2.0)
x, y = point         # tuple unpacking，一次拆成多個變數

# dict：key-value 對應，Python 3.7+ 會記住插入順序
prices = {"rice": 1.0, "milk": 8.7}
prices["rice"]              # 1.0
prices.get("eggs", 0.0)     # 0.0，key 不存在時回傳預設值，不會拋例外
prices["eggs"] = 3.0        # 新增或覆蓋
for key, value in prices.items():
    print(key, value)

# set：不重複、無順序，適合「檢查有沒有出現過」「去重複」
seen = {"S01", "S02"}
"S01" in seen        # True，比在 list 裡找快很多（尤其資料量大時）
```

`[]`、`()`、`{}` 也可以用 comprehension（生成式）一行寫出一個新的 list/dict/set，例如 `[x * 2 for x in items]`。這套訓練的 day17（OOP 那天）會實際用到 dict comprehension，這裡先知道語法長什麼樣就好。

## 函式

```python
def add(a: float, b: float = 0.0) -> float:
    """回傳 a + b。"""
    return a + b

add(1.0, 2.0)   # 3.0
add(1.0)        # 1.0，b 用預設值 0.0
add(b=2.0, a=1.0)  # 3.0，用參數名稱指定，順序可以不同
```

- `-> float` 跟 `a: float` 是型別標註（type hint），告訴人跟工具「這裡預期是什麼型別」，但 Python **執行期不會強制檢查**。這套訓練從 day01 就要求寫型別標註，`CONCEPTS.md` 會講更多。
- 函式可以回傳多個值，其實是回傳一個 tuple：`def minmax(xs): return min(xs), max(xs)`，呼叫端用 `lo, hi = minmax(xs)` 拆開。
- 沒有寫 `return` 的函式，呼叫後會拿到 `None`。

## `if __name__ == "__main__":` 是什麼？每一天的 `solution.py` 結尾都有這一段

從 day01 開始，每天的 `solution.py` 骨架結尾都長這樣：

```python
def main() -> int:
    ...
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
```

`__name__` 是每個 `.py` 檔案都自動擁有的一個內建變數，值會依「這個檔案是怎麼被執行的」而不同：

- **直接執行**這個檔案（`python solution.py`）時，Python 會把這個檔案的 `__name__` 設成字串 `"__main__"`。
- 這個檔案被**匯入**（例如 `test_solution.py` 裡寫 `from solution import mean`）時，`__name__` 會是這個模組的名字（`"solution"`），不是 `"__main__"`。

所以 `if __name__ == "__main__":` 的意思是「只有在直接執行這個檔案時才做這件事，被別人 `import` 的時候不要做」。這正是這套訓練每天的測試能運作的關鍵：`test_solution.py` 需要 `import solution` 才能呼叫裡面的函式來測試，如果沒有這個 `if` 保護，光是 `import` 這個動作就會把 `main()` 整套 CLI 邏輯也順便跑一次（可能因為讀不到命令列參數而直接報錯）。這也是為什麼 day08 之後規格會要求 `main(argv: list[str] | None = None)` 這種可以被直接呼叫測試的寫法，而不是讓 `main()` 內部自己去讀 `sys.argv`。

`raise SystemExit(main())` 則是「呼叫 `main()`，拿到它回傳的整數，把這個整數變成程式真正的結束狀態碼（exit code）」。`SystemExit` 是一個特殊的例外，Python 直譯器在最外層看到它時，不會印出 traceback、而是直接用你給的整數結束整個程式。如果只寫 `main()`（不包 `raise SystemExit(...)`），`main()` 回傳的 `2` 或 `3` 會被默默丟掉，程式對外看到的結束狀態碼永遠是 `0`（成功），不管 `main()` 內部實際判斷發生了什麼錯誤。這正是 day04 會深入講的 exit code 機制，底層用的就是這一行：`sys.exit(code)` 跟 `raise SystemExit(code)` 做的是同一件事，這套訓練的骨架選了後者。

## 例外處理入門

程式執行中出錯時，Python 會「拋出例外」（raise an exception），如果沒人處理，程式就會停下來並印出 traceback（錯誤呼叫堆疊）：

```python
try:
    result = 10 / 0
except ZeroDivisionError:
    print("不能除以零")
```

`try` 區塊裡的程式碼正常執行；如果拋出符合 `except` 指定型別的例外，就跳進對應的 `except` 區塊，不會讓程式整個中斷。這只是最小介紹，這套訓練的 day04 會深入講什麼時候該自己 `raise`、什麼時候該 `except`、為什麼 `except Exception: pass` 是地雷，這裡先知道語法長這樣，能讀懂錯誤訊息在說什麼就夠了。

## 常見陷阱（先知道，之後少踩一次）

- **縮排不一致**：同一個區塊裡混用 tab 跟空格，或縮排數量不一致，會直接 `IndentationError`。編輯器設定「Tab 轉空格」可以避免大部分問題。
- **`range(n)` 不包含 `n`**：`range(3)` 是 `0, 1, 2`，這是每個新手都會踩一次的 off-by-one（差一錯誤）。
- **浮點數不要用 `==` 比較**：`0.1 + 0.2 == 0.3` 在 Python 裡是 `False`（浮點數運算有精度誤差），要比較浮點數該用 `abs(a - b) < 0.0001` 這種容忍誤差的寫法。
- **函式預設值不要用 `[]`／`{}`**：`def f(x=[]):` 這個空 list 只會在函式定義時建立一次，所有呼叫共用同一份。這套訓練的 `final_project/CONCEPTS.md` 會用真實案例講這個地雷，這裡先知道「看到預設值是空容器要多想一下」。

## 下一步

上面哪一段讀起來還是模糊，先花點時間把那個概念補起來（隨便找 Python 官方教學或任何入門資源都可以，這份文件只是快速對照表，不是完整教材），再回來開始 `day01`。day01 的 `CONCEPTS.md` 會接著講「為什麼要拆函式」「為什麼型別標註有用」這些設計層面的問題，前提是你已經看得懂 `def`、`if`、`list` 這些語法本身。
