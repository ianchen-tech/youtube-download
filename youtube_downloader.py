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
        
    def download_video(self, url, quality="best", audio_only=False):
        """
        下載 YouTube 影片
        
        Args:
            url (str): YouTube 影片連結
            quality (str): 影片品質 (best, worst, 720p, 480p 等)
            audio_only (bool): 是否只下載音訊
        """
        try:
            print(f"{Fore.CYAN}正在準備下載: {url}{Style.RESET_ALL}")
            
            # 設定 yt-dlp 選項
            ydl_opts = {
                'outtmpl': str(self.output_dir / '%(title)s.%(ext)s'),
                'format': self._get_format_selector(quality, audio_only),
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
            print(f"{Fore.RED}下載錯誤: {str(e)}{Style.RESET_ALL}")
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