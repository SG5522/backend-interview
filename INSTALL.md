#  啟動前的安裝需知

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

## 修改DB相關
1. **調整完db欄位**：請使用下述指令
```
alembic revision --autogenerate -m "描述內容"
```
2. **萬一DB無法遷移(由其在sqlite環境)**：請刪除所有versions的內容，並輸入下述指令

```
alembic revision --autogenerate -m "init"
```