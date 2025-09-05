#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 下載工具 - Flask 網頁版
"""

import os
import tempfile
import shutil
from pathlib import Path
from flask import Flask, render_template, request, jsonify, send_file, flash, redirect, url_for
import yt_dlp
from werkzeug.utils import secure_filename
import threading
import time
import uuid

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-here')

# 全域變數來追蹤下載狀態
download_status = {}

class YouTubeDownloader:
    def __init__(self, temp_dir=None):
        self.temp_dir = temp_dir or tempfile.mkdtemp()
        
    def download_video(self, url, quality="best", audio_only=False, download_id=None):
        """
        下載 YouTube 影片
        """
        try:
            if download_id:
                download_status[download_id] = {
                    'status': 'downloading',
                    'progress': 0,
                    'title': '',
                    'error': None,
                    'file_path': None
                }
            
            # 設定 yt-dlp 選項
            ydl_opts = {
                'outtmpl': os.path.join(self.temp_dir, '%(title)s.%(ext)s'),
                'format': self._get_format_selector(quality, audio_only),
                # 添加反機器人驗證相關設定
                'extractor_retries': 3,
                'fragment_retries': 3,
                'retry_sleep_functions': {'http': lambda n: min(4 ** n, 60)},
                # 使用較慢的請求速度避免觸發限制
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                # 設定 User-Agent
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                # 嘗試使用不同的客戶端
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web'],
                        'player_skip': ['configs']
                    }
                }
            }
            
            # 如果只下載音訊，設定音訊格式
            if audio_only:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            # 進度回調函數
            def progress_hook(d):
                if download_id and d['status'] == 'downloading':
                    if 'total_bytes' in d and d['total_bytes']:
                        progress = (d['downloaded_bytes'] / d['total_bytes']) * 100
                        download_status[download_id]['progress'] = round(progress, 1)
                    elif '_percent_str' in d:
                        percent_str = d['_percent_str'].strip().replace('%', '')
                        try:
                            download_status[download_id]['progress'] = float(percent_str)
                        except:
                            pass
            
            ydl_opts['progress_hooks'] = [progress_hook]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片資訊
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                
                if download_id:
                    download_status[download_id]['title'] = title
                
                # 下載影片
                ydl.download([url])
                
                # 尋找下載的檔案
                downloaded_files = list(Path(self.temp_dir).glob('*'))
                if downloaded_files:
                    file_path = str(downloaded_files[0])
                    if download_id:
                        download_status[download_id]['status'] = 'completed'
                        download_status[download_id]['progress'] = 100
                        download_status[download_id]['file_path'] = file_path
                    return {
                        'success': True,
                        'title': title,
                        'uploader': uploader,
                        'duration': self._format_duration(duration),
                        'file_path': file_path
                    }
                else:
                    raise Exception("找不到下載的檔案")
                
        except Exception as e:
            error_msg = str(e)
            
            # 針對常見錯誤提供更好的錯誤訊息
            if 'Sign in to confirm you\'re not a bot' in error_msg:
                error_msg = (
                    "YouTube 偵測到機器人行為，請稍後再試。\n"
                    "建議解決方案：\n"
                    "1. 等待 5-10 分鐘後重試\n"
                    "2. 嘗試下載其他影片\n"
                    "3. 如果問題持續，可能需要使用瀏覽器 cookies"
                )
            elif 'HTTP Error 429' in error_msg:
                error_msg = (
                    "請求過於頻繁，已觸發 YouTube 限制。\n"
                    "請等待幾分鐘後再試，或降低下載頻率。"
                )
            elif 'Video unavailable' in error_msg:
                error_msg = "影片無法取得，可能是私人影片、地區限制或已被刪除。"
            elif 'This video is not available' in error_msg:
                error_msg = "此影片不可用，可能因版權或地區限制。"
            
            if download_id:
                download_status[download_id]['status'] = 'error'
                download_status[download_id]['error'] = error_msg
            return {
                'success': False,
                'error': error_msg
            }
    
    def _get_format_selector(self, quality, audio_only):
        """
        根據品質設定獲取格式選擇器
        """
        if audio_only:
            return 'bestaudio/best'
        
        if quality == "best":
            return 'best[ext=mp4]/best'
        elif quality == "worst":
            return 'worst[ext=mp4]/worst'
        elif quality.endswith('p'):
            height = quality[:-1]
            return f'best[height<={height}][ext=mp4]/best[height<={height}]/best[ext=mp4]/best'
        else:
            return 'best[ext=mp4]/best'
    
    def _format_duration(self, seconds):
        """
        將秒數轉換為可讀的時間格式
        """
        if not seconds:
            return "未知"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"

@app.route('/')
def index():
    """首頁"""
    return render_template('index.html')

@app.route('/download', methods=['POST'])
def download():
    """處理下載請求"""
    try:
        data = request.get_json()
        url = data.get('url', '').strip()
        quality = data.get('quality', 'best')
        audio_only = data.get('audio_only', False)
        
        if not url:
            return jsonify({'success': False, 'error': '請提供有效的 YouTube 連結'})
        
        # 生成下載ID
        download_id = str(uuid.uuid4())
        
        # 在背景執行下載
        downloader = YouTubeDownloader()
        thread = threading.Thread(
            target=downloader.download_video,
            args=(url, quality, audio_only, download_id)
        )
        thread.daemon = True
        thread.start()
        
        return jsonify({
            'success': True,
            'download_id': download_id,
            'message': '開始下載...'
        })
        
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route('/status/<download_id>')
def get_status(download_id):
    """獲取下載狀態"""
    if download_id in download_status:
        return jsonify(download_status[download_id])
    else:
        return jsonify({'status': 'not_found', 'error': '找不到下載任務'})

@app.route('/download_file/<download_id>')
def download_file(download_id):
    """下載檔案"""
    if download_id in download_status:
        status = download_status[download_id]
        if status['status'] == 'completed' and status['file_path']:
            file_path = status['file_path']
            if os.path.exists(file_path):
                filename = os.path.basename(file_path)
                return send_file(
                    file_path,
                    as_attachment=True,
                    download_name=filename
                )
    
    return jsonify({'error': '檔案不存在或下載未完成'}), 404

@app.route('/health')
def health_check():
    """健康檢查端點"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)