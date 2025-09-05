# YouTube 影片下載工具

一個簡單易用的 YouTube 影片下載工具，基於 Python 和 yt-dlp 開發。支援命令行和網頁兩種使用方式，可部署到 Google Cloud Run。

## 功能特色

- 🎥 下載 YouTube 影片（支援多種品質選擇）
- 🎵 只下載音訊（MP3 格式）
- 📁 自訂輸出目錄
- 🎨 彩色終端輸出
- 🛡️ 完善的錯誤處理
- 📋 命令行和互動式兩種使用方式
- 🌐 現代化網頁介面
- ☁️ 支援 Cloud Run 部署
- 🚀 GitHub Actions 自動部署

## 系統需求

- Python 3.7 或更高版本
- macOS / Linux / Windows

## 安裝步驟

1. **克隆或下載專案**
   ```bash
   cd youtube-download
   ```

2. **創建虛擬環境**
   ```bash
   python3 -m venv venv
   ```

3. **激活虛擬環境**
   
   macOS/Linux:
   ```bash
   source venv/bin/activate
   ```
   
   Windows:
   ```bash
   venv\Scripts\activate
   ```

4. **安裝依賴套件**
   ```bash
   pip install -r requirements.txt
   ```

## 使用方法

### 方法一：網頁版（推薦）

1. **本地運行**
   ```bash
   source venv/bin/activate
   python app.py
   ```
   然後在瀏覽器中打開 `http://localhost:8080`

2. **Docker 運行**
   ```bash
   docker build -t youtube-downloader .
   docker run -p 8080:8080 youtube-downloader
   ```

### 方法二：互動式使用（命令行）

```bash
python download.py
```

或者直接提供連結：

```bash
python download.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 方法二：命令行使用（進階用戶）

```bash
python youtube_downloader.py "YouTube連結" [選項]
```

#### 命令行選項

- `--quality, -q`: 指定影片品質（best, worst, 720p, 480p, 360p 等）
- `--audio-only, -a`: 只下載音訊（MP3 格式）
- `--output-dir, -o`: 指定輸出目錄
- `--help, -h`: 顯示幫助資訊

## 使用範例

### 基本下載
```bash
# 下載最佳品質影片
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
```

### 指定品質下載
```bash
# 下載 720p 影片
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --quality 720p

# 下載 480p 影片
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 480p
```

### 只下載音訊
```bash
# 下載為 MP3 格式
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio-only

# 簡寫形式
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a
```

### 自訂輸出目錄
```bash
# 下載到指定目錄
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output-dir ./my_videos

# 簡寫形式
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -o ./my_videos
```

### 組合使用
```bash
# 下載 720p 影片到指定目錄
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -q 720p -o ./downloads

# 下載音訊到指定目錄
python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" -a -o ./music
```

## Cloud Run 部署

### 前置準備

1. **建立 Google Cloud 專案**
   - 前往 [Google Cloud Console](https://console.cloud.google.com/)
   - 建立新專案或選擇現有專案
   - 啟用 Cloud Run API 和 Container Registry API

2. **設定 GitHub Secrets**
   在 GitHub 儲存庫的 Settings > Secrets and variables > Actions 中新增：
   - `GCP_PROJECT_ID`: 您的 Google Cloud 專案 ID
   - `GCP_SA_KEY`: 服務帳戶金鑰（JSON 格式）

### 自動部署

1. **推送到 GitHub**
   ```bash
   git add .
   git commit -m "Initial commit"
   git push origin main
   ```

2. **GitHub Actions 會自動**
   - 建置 Docker 映像
   - 推送到 Container Registry
   - 部署到 Cloud Run
   - 測試部署狀態

### 手動部署

```bash
# 建置並推送映像
docker build -t gcr.io/YOUR_PROJECT_ID/youtube-downloader .
docker push gcr.io/YOUR_PROJECT_ID/youtube-downloader

# 部署到 Cloud Run
gcloud run deploy youtube-downloader \
  --image gcr.io/YOUR_PROJECT_ID/youtube-downloader \
  --region asia-east1 \
  --platform managed \
  --allow-unauthenticated \
  --memory 2Gi \
  --cpu 2 \
  --timeout 3600
```

## 檔案結構

```
youtube-download/
├── README.md                    # 說明文件
├── requirements.txt             # Python 依賴套件
├── app.py                      # Flask 網頁應用程式
├── youtube_downloader.py       # 命令行下載腳本
├── download.py                 # 簡化的互動式腳本
├── Dockerfile                  # Docker 容器配置
├── .dockerignore              # Docker 忽略檔案
├── cloudbuild.yaml            # Cloud Build 配置
├── .github/workflows/deploy.yml # GitHub Actions 工作流程
├── templates/
│   └── index.html             # 網頁前端介面
├── static/                    # 靜態資源目錄
├── venv/                      # Python 虛擬環境
└── downloads/                 # 預設下載目錄
```

## 支援的影片品質

- `best`: 最佳可用品質（預設）
- `worst`: 最低品質
- `720p`: 720p 解析度
- `480p`: 480p 解析度
- `360p`: 360p 解析度
- 其他 yt-dlp 支援的格式

## 常見問題

### Q: 下載失敗怎麼辦？
A: 請檢查：
- 網路連線是否正常
- YouTube 連結是否有效
- 影片是否為私人或受地區限制
- 是否已正確安裝所有依賴套件

### Q: 可以下載播放清單嗎？
A: 目前版本支援單一影片下載，播放清單功能可能在未來版本中加入。

### Q: 下載的檔案在哪裡？
A: 預設保存在 `downloads` 目錄中，可以使用 `--output-dir` 參數自訂位置。

### Q: 支援哪些影片格式？
A: 主要支援 MP4 格式的影片和 MP3 格式的音訊。

## 注意事項

- 請遵守 YouTube 的服務條款
- 僅下載您有權下載的內容
- 請勿用於商業用途
- 尊重版權所有者的權利

## 技術支援

如果遇到問題，請檢查：
1. Python 版本是否符合需求
2. 所有依賴套件是否正確安裝
3. 網路連線是否正常
4. YouTube 連結是否有效

## 更新日誌

### v1.0.0
- 初始版本發布
- 支援基本的影片和音訊下載功能
- 提供命令行和互動式兩種使用方式
- 支援多種品質選擇
- 完善的錯誤處理機制

---

**免責聲明**: 此工具僅供個人學習和研究使用，請遵守相關法律法規和平台服務條款。