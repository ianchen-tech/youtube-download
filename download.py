#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡化的 YouTube 下載腳本
直接輸入 YouTube 連結即可下載
"""

import sys
from youtube_downloader import YouTubeDownloader
from colorama import init, Fore, Style

init(autoreset=True)

def main():
    print(f"{Fore.MAGENTA}=== YouTube 影片下載工具 ==={Style.RESET_ALL}")
    print()
    
    # 如果有命令行參數，直接使用
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        # 互動式輸入
        url = input(f"{Fore.CYAN}請輸入 YouTube 影片連結: {Style.RESET_ALL}").strip()
    
    if not url:
        print(f"{Fore.RED}錯誤: 請提供有效的 YouTube 連結{Style.RESET_ALL}")
        return
    

    
    # 詢問下載選項
    print(f"{Fore.YELLOW}下載選項:{Style.RESET_ALL}")
    print("1. 下載影片 (最佳品質)")
    print("2. 下載影片 (720p)")
    print("3. 下載影片 (480p)")
    print("4. 只下載音訊 (MP3)")
    
    choice = input(f"{Fore.CYAN}請選擇 (1-4，預設為1): {Style.RESET_ALL}").strip()
    
    # 設定下載參數
    quality = "best"
    audio_only = False
    
    if choice == "2":
        quality = "720p"
    elif choice == "3":
        quality = "480p"
    elif choice == "4":
        audio_only = True
    
    # 創建下載器並開始下載
    downloader = YouTubeDownloader()
    success = downloader.download_video(url, quality=quality, audio_only=audio_only)
    
    if success:
        print(f"{Fore.GREEN}\n下載完成！{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}\n下載失敗！{Style.RESET_ALL}")

if __name__ == "__main__":
    main()