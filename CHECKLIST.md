# 完成清單

依 dayXX 順序推進，不綁定要在幾天內做完；下面的「第一階段/第二階段」是難度里程碑，不是週數。

## 每日

- [ ] 閱讀當日 spec
- [ ] 前 20 分鐘未讓 AI 直接寫核心程式
- [ ] 功能完成
- [ ] 錯誤案例完成
- [ ] pytest 全部通過
- [ ] notes.md 已填
- [ ] ai_usage.md 已填
- [ ] 已 commit
- [ ] 能口頭解釋核心函式
- [ ] 看過 CONCEPTS.md（解題前或解題後皆可）

## 第一階段（day01～07）

- [ ] 可讀取 TOML
- [ ] 可處理 CSV
- [ ] 可寫 pytest
- [ ] 可設計簡單 CLI
- [ ] 可解釋例外與 exit code

## 第二階段（day08～14）

- [ ] 可使用 argparse，能講出 `--help` 的設計考量
- [ ] 可安全呼叫 subprocess
- [ ] 可建立 dataclass
- [ ] 可重構 I/O 與計算
- [ ] 可完成套件化 CLI
- [ ] 通過 30 分鐘獨立挑戰

## 延伸階段（day15～19，選修，不計入兩週核心天數）

- [ ] 能解釋 `sys.path`／`ModuleNotFoundError`，並在需要時寫出跟工作目錄無關、可重複呼叫的手動路徑操作
- [ ] 可讀懂並執行 `ruff`／`mypy` 的檢查結果
- [ ] 可用 `conftest.py` 共用 fixture、用 `parametrize` 收斂重複測試
- [ ] 可分辨一般 class 跟 dataclass 該用在哪種情境
- [ ] 可寫 context manager（class 版與 `contextlib.contextmanager` 版）
- [ ] 能用 `ABC`／`@abstractmethod` 設計「一個介面，多種實作」，並解釋為什麼呼叫端該依賴抽象型別而非具體子類別
- [ ] 能解釋 `async`/`await` 在等什麼、`asyncio.gather` 的兩種失敗模式，並看出 `time.sleep()` 混進 async 函式裡的地雷
