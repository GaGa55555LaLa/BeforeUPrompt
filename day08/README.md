# Day 08：Argparse CLI

## 執行
```bash
python solution.py --input prices.csv --baseline S01 --min-coverage 0.5 --output summary.json
```

## 參數
- `--input` 必填路徑。
- `--baseline` 必填字串。
- `--min-coverage` 選填 float，預設 0.5，範圍 0～1。
- `--output` 必填路徑。
- `--verbose` 選填 flag。

## 功能
讀 CSV；以所有 item 為完整集合；計算 coverage；低於門檻標示 invalid；輸出 JSON；建立輸出父目錄。

## 結構
至少實作：
```python
def build_parser(): ...
def run(args): ...
def main(argv: list[str] | None = None) -> int: ...
```

## 測試
至少 10 個；至少兩個直接呼叫 `main([...])`。

## 口頭驗收
為何 `main(argv=None)` 比直接讀 `sys.argv` 更容易測？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）——這天特別用你剛改過的 `../gate.py` 當案例講 CLI 設計。
