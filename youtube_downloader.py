#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 影片下載工具
使用 yt-dlp 下載指定的 YouTube 影片
"""

import os
import sys
import argparse
from pathlib import Path
from colorama import init, Fore, Style
import yt_dlp

# 初始化 colorama
init(autoreset=True)

class YouTubeDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        # 隨機 User-Agent 列表
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/120.0'
        ]
        
    def download_video(self, url, quality="best", audio_only=False):
        """
        下載 YouTube 影片
        
        Args:
            url (str): YouTube 影片連結
            quality (str): 影片品質 (best, worst, 720p, 480p 等)
            audio_only (bool): 是否只下載音訊
        """
        try:
            import random
            import time
            
            print(f"{Fore.CYAN}正在準備下載: {url}{Style.RESET_ALL}")
            
            # 隨機延遲 1-3 秒，模擬人類行為
            time.sleep(random.uniform(1, 3))
            
            # 設定 yt-dlp 選項
            ydl_opts = {
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'format': self._get_format_selector(quality, audio_only),
                # 增強反機器人驗證設定
                'extractor_retries': 5,
                'fragment_retries': 5,
                'file_access_retries': 3,
                'retry_sleep_functions': {
                    'http': lambda n: min(2 ** n + random.uniform(0, 1), 30),
                    'fragment': lambda n: min(2 ** n + random.uniform(0, 1), 30)
                },
                # 隨機請求間隔，模擬人類瀏覽行為
                'sleep_interval': random.uniform(2, 5),
                'max_sleep_interval': random.uniform(8, 15),
                'sleep_interval_requests': random.uniform(1, 3),
                # 隨機 User-Agent
                'http_headers': {
                    'User-Agent': random.choice(self.user_agents),
                    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                    'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'DNT': '1',
                    'Connection': 'keep-alive',
                    'Upgrade-Insecure-Requests': '1'
                },
                # 使用多種客戶端策略
                'extractor_args': {
                    'youtube': {
                        'player_client': ['android', 'web', 'ios', 'mweb', 'tv_embedded'],
                        'player_skip': ['configs'],
                        'include_live_dash': False,
                        'skip': ['hls', 'dash']
                    }
                },
                # 避免過於頻繁的請求
                'concurrent_fragment_downloads': 1,
                'throttled_rate': '100K'
            }
            
            # 如果只下載音訊，設定音訊格式
            if audio_only:
                ydl_opts['postprocessors'] = [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }]
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                # 獲取影片資訊
                info = ydl.extract_info(url, download=False)
                title = info.get('title', 'Unknown')
                duration = info.get('duration', 0)
                uploader = info.get('uploader', 'Unknown')
                
                print(f"{Fore.GREEN}影片標題: {title}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}上傳者: {uploader}{Style.RESET_ALL}")
                print(f"{Fore.GREEN}時長: {self._format_duration(duration)}{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}開始下載...{Style.RESET_ALL}")
                
                # 下載影片
                ydl.download([url])
                
                print(f"{Fore.GREEN}✓ 下載完成！{Style.RESET_ALL}")
                print(f"{Fore.CYAN}檔案保存在: {self.output_dir.absolute()}{Style.RESET_ALL}")
                
        except yt_dlp.DownloadError as e:
            error_msg = str(e)
            
            # 針對常見錯誤提供更好的錯誤訊息
            if 'Failed to extract any player response' in error_msg:
                print(f"{Fore.RED}下載失敗: YouTube 播放器回應提取失敗{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}解決方案:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}1. 檢查影片連結是否正確且可存取{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}2. 等待 5-10 分鐘後重試（可能是暫時性問題）{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}3. 嘗試使用不同的影片品質設定{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}4. 確認影片未被設為私人或地區限制{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}5. 如果問題持續，可能是 YouTube 更新了防護機制{Style.RESET_ALL}")
            elif 'Sign in to confirm you\'re not a bot' in error_msg:
                print(f"{Fore.RED}下載失敗: YouTube 偵測到機器人行為{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}解決方案:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}1. 等待 5-10 分鐘後重試{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}2. 系統已自動調整請求策略，請耐心等待{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}3. 嘗試下載其他影片{Style.RESET_ALL}")
            elif 'HTTP Error 429' in error_msg:
                print(f"{Fore.RED}下載失敗: 請求過於頻繁{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}請等待幾分鐘後再試，或降低下載頻率{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}下載錯誤: {error_msg}{Style.RESET_ALL}")
            return False
        except Exception as e:
            print(f"{Fore.RED}發生未知錯誤: {str(e)}{Style.RESET_ALL}")
            return False
            
        return True
    
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

def main():
    parser = argparse.ArgumentParser(
        description='YouTube 影片下載工具',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
範例:
  python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
  python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --quality 720p
  python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --audio-only
  python youtube_downloader.py "https://www.youtube.com/watch?v=dQw4w9WgXcQ" --output-dir ./my_videos
        """
    )
    
    parser.add_argument('url', help='YouTube 影片連結')
    parser.add_argument(
        '--quality', '-q',
        default='best',
        help='影片品質 (best, worst, 720p, 480p, 360p 等，預設: best)'
    )
    parser.add_argument(
        '--audio-only', '-a',
        action='store_true',
        help='只下載音訊 (MP3 格式)'
    )
    parser.add_argument(
        '--output-dir', '-o',
        default='downloads',
        help='輸出目錄 (預設: downloads)'
    )

    
    args = parser.parse_args()
    
    # 驗證 URL
    if not args.url.strip():
        print(f"{Fore.RED}錯誤: 請提供有效的 YouTube 連結{Style.RESET_ALL}")
        sys.exit(1)
    
    # 創建下載器並開始下載
    downloader = YouTubeDownloader(args.output_dir)
    
    print(f"{Fore.MAGENTA}=== YouTube 影片下載工具 ==={Style.RESET_ALL}")
    print()
    
    success = downloader.download_video(
        args.url,
        quality=args.quality,
        audio_only=args.audio_only
    )
    
    if not success:
        sys.exit(1)

if __name__ == "__main__":
    main()