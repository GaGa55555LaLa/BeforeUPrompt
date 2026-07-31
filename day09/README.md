# Day 09：Git Repository 資訊工具

## 執行
```bash
python solution.py [path]
```

## 輸出
Git 根目錄、目前分支、最新 commit hash、是否有未提交修改。

可使用：
```text
git rev-parse --show-toplevel
git branch --show-current
git rev-parse HEAD
git status --porcelain
```

## 規則
- 使用 `subprocess.run()` argument list。
- `capture_output=True`、`text=True`。
- 禁止 `shell=True`。
- 非 Git repo：exit 2。
- Git 不存在：exit 3。
- 成功：exit 0。

## 測試
至少 8 個，可用 monkeypatch（暫時替換函式或物件）模擬 subprocess。

## 口頭驗收
`shell=True` 有何風險？為何 porcelain 格式適合程式解析？

## 延伸知識
看 `CONCEPTS.md`（解題前或解題後皆可）。
