# 社群平台開發測驗

## 使用工具
- **Language:** Python 3.12
- **Framework:** FastAPI (Asynchronous)
- **Database:** SQLite (使用 SQLAlchemy + aiosqlite)
- **Authentication:** JWT (OAuth2 Password Bearer)

##  啟動前的安裝需知

##  安裝 Python 
1. **下載版本**：[Python 3.12.10 官方下載](https://www.python.org/ftp/python/3.12.10/python-3.12.10-amd64.exe)。
2. **安裝設定**：
   -  務必勾選 **"Add Python to PATH"**。
   -  選擇 **"Install Now"**。
3. **驗證指令**（開啟新 PowerShell）：
   ```powershell
   python --version  # 預期輸出: Python 3.12.10
   pip --version     # 預期輸出: pip 24.x.x
   ```

##  建立專案虛擬環境
1. **進入專案目錄**：cd C:\你的專案路徑

2. **建立 venv**：python -m venv venv

3. **啟動環境：**.\venv\Scripts\activate.ps1
   - **結果**：命令列左側出現 (venv) 字樣。


## 安裝本專案的3rd Party套件

**安裝套件**：pip install -r requirements.txt
   - 如要更新套件輸入 1. pip freeze > requirements.txt

## 設定.env檔

1. **複製檔案**: 將專案的.env.example複製貼上，重新命名為.env
2. **修改SECRET_KEY內容**: 隨機產生SECRET_KEY輸入
   ```
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```
   - 最後將產生的參數放入SECRET_KEY

## 資料庫初始化
本專案採用自動化建構機制：
- **自動建構**：啟動 FastAPI Server 時，系統會自動檢查並根據最新遷移內容建構 SQLite 資料庫

## 🛠️ 開發與資料庫維護 (Alembic)
雖然系統啟動時會自動建構資料表，但若您需要進行 Schema 修改，可參考以下指令：

1. **產生遷移腳本**：
   ```powershell
   alembic revision --autogenerate -m "描述變更內容" 
   ```  
2. **萬一DB無法遷移(由其在sqlite環境)**：請刪除所有versions的內容，刪除DB後，並重新產生初始化的遷移腳本
   ```powershell
   alembic revision --autogenerate -m "init"
   ```