#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
簡單的 YouTube 下載工具
使用 pytube 替代 yt-dlp，更不容易被檢測為機器人
"""

import os
import time
import random
import re
from pathlib import Path
from colorama import init, Fore, Style

init(autoreset=True)

class SimpleYouTubeDownloader:
    def __init__(self, output_dir="downloads"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        
        # 模擬真實瀏覽器的請求頭
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'zh-TW,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1'
        }
    
    def _human_like_delay(self):
        """模擬人類操作延遲"""
        delay = random.uniform(2, 5)
        time.sleep(delay)
    
    def download_video(self, url, quality="highest", audio_only=False):
        """下載 YouTube 影片"""
        try:
            from pytube import YouTube
            import requests
            
            print(f"{Fore.CYAN}正在準備下載: {url}{Style.RESET_ALL}")
            
            # 模擬人類瀏覽行為 - 隨機延遲
            self._human_like_delay()
            
            # 創建 YouTube 對象，使用自定義請求頭
            yt = YouTube(url)
            
            # 獲取影片資訊
            title = yt.title
            length = yt.length
            author = yt.author
            
            print(f"{Fore.GREEN}影片標題: {title}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}上傳者: {author}{Style.RESET_ALL}")
            print(f"{Fore.GREEN}時長: {self._format_duration(length)}{Style.RESET_ALL}")
            
            # 另一個延遲，模擬用戶查看資訊的時間
            self._human_like_delay()
            
            if audio_only:
                # 下載音訊
                print(f"{Fore.YELLOW}正在下載音訊...{Style.RESET_ALL}")
                stream = yt.streams.filter(only_audio=True).first()
                if stream:
                    safe_title = self._sanitize_filename(title)
                    filename = f"{safe_title}.mp3"
                    
                    # 下載為 mp4，然後重命名為 mp3
                    downloaded_file = stream.download(output_path=self.output_dir, filename=f"{safe_title}_temp")
                    final_path = self.output_dir / filename
                    
                    # 重命名文件
                    Path(downloaded_file).rename(final_path)
                    
                    print(f"{Fore.GREEN}✓ 音訊下載完成！{Style.RESET_ALL}")
                    return True
            else:
                # 下載影片
                print(f"{Fore.YELLOW}正在下載影片...{Style.RESET_ALL}")
                
                if quality == "highest":
                    stream = yt.streams.get_highest_resolution()
                elif quality == "lowest":
                    stream = yt.streams.get_lowest_resolution()
                elif quality.endswith('p'):
                    # 嘗試獲取指定解析度
                    resolution = quality
                    stream = yt.streams.filter(res=resolution, file_extension='mp4').first()
                    if not stream:
                        # 如果指定解析度不存在，獲取最接近的
                        stream = yt.streams.filter(file_extension='mp4').first()
                else:
                    stream = yt.streams.get_highest_resolution()
                
                if stream:
                    safe_title = self._sanitize_filename(title)
                    filename = f"{safe_title}.{stream.subtype}"
                    
                    print(f"{Fore.YELLOW}下載品質: {stream.resolution} ({stream.subtype}){Style.RESET_ALL}")
                    stream.download(output_path=self.output_dir, filename=filename)
                    
                    print(f"{Fore.GREEN}✓ 影片下載完成！{Style.RESET_ALL}")
                    return True
                else:
                    print(f"{Fore.RED}找不到合適的影片流{Style.RESET_ALL}")
                    return False
            
        except ImportError:
            print(f"{Fore.RED}錯誤: 請先安裝 pytube{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}安裝命令: pip install pytube{Style.RESET_ALL}")
            return False
        except Exception as e:
            error_msg = str(e)
            
            # 提供更友好的錯誤訊息
            if "regex_search" in error_msg or "get_throttling_function_name" in error_msg:
                print(f"{Fore.RED}下載失敗: YouTube 更新了防護機制{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}解決方案:{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}1. 更新 pytube: pip install --upgrade pytube{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}2. 等待幾分鐘後重試{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}3. 嘗試其他影片{Style.RESET_ALL}")
            elif "unavailable" in error_msg.lower():
                print(f"{Fore.RED}下載失敗: 影片不可用{Style.RESET_ALL}")
                print(f"{Fore.YELLOW}可能原因: 影片被設為私人、刪除或地區限制{Style.RESET_ALL}")
            else:
                print(f"{Fore.RED}下載錯誤: {error_msg}{Style.RESET_ALL}")
            
            return False
    
    def _sanitize_filename(self, filename):
        """清理檔案名稱，移除不合法字符"""
        # 移除或替換不合法的檔案名稱字符
        illegal_chars = r'[<>:"/\\|?*]'
        safe_filename = re.sub(illegal_chars, '_', filename)
        
        # 限制檔案名稱長度
        if len(safe_filename) > 200:
            safe_filename = safe_filename[:200]
        
        return safe_filename.strip()
    
    def _format_duration(self, seconds):
        """將秒數轉換為可讀的時間格式"""
        if not seconds:
            return "未知"
        
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        
        if hours > 0:
            return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
        else:
            return f"{minutes:02d}:{seconds:02d}"
    
    def get_video_info(self, url):
        """獲取影片資訊而不下載"""
        try:
            from pytube import YouTube
            
            yt = YouTube(url)
            
            info = {
                'title': yt.title,
                'author': yt.author,
                'length': yt.length,
                'views': yt.views,
                'description': yt.description[:200] + '...' if len(yt.description) > 200 else yt.description,
                'thumbnail_url': yt.thumbnail_url,
                'available_qualities': [stream.resolution for stream in yt.streams.filter(file_extension='mp4') if stream.resolution]
            }
            
            return info
            
        except Exception as e:
            print(f"{Fore.RED}獲取影片資訊失敗: {e}{Style.RESET_ALL}")
            return None

def main():
    print(f"{Fore.MAGENTA}=== 簡單 YouTube 下載工具 ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}使用 pytube 庫，更不容易被檢測為機器人{Style.RESET_ALL}")
    print()
    
    url = input(f"{Fore.CYAN}請輸入 YouTube 影片連結: {Style.RESET_ALL}").strip()
    
    if not url:
        print(f"{Fore.RED}錯誤: 請提供有效的 YouTube 連結{Style.RESET_ALL}")
        return
    
    downloader = SimpleYouTubeDownloader()
    
    # 先獲取影片資訊
    print(f"{Fore.YELLOW}正在獲取影片資訊...{Style.RESET_ALL}")
    info = downloader.get_video_info(url)
    
    if info:
        print(f"{Fore.GREEN}可用品質: {', '.join(filter(None, info['available_qualities']))}{Style.RESET_ALL}")
        print()
    
    # 詢問下載選項
    print(f"{Fore.YELLOW}下載選項:{Style.RESET_ALL}")
    print("1. 下載影片 (最高品質)")
    print("2. 下載影片 (720p)")
    print("3. 下載影片 (480p)")
    print("4. 只下載音訊")
    
    choice = input(f"{Fore.CYAN}請選擇 (1-4，預設為1): {Style.RESET_ALL}").strip()
    
    # 設定下載參數
    quality = "highest"
    audio_only = False
    
    if choice == "2":
        quality = "720p"
    elif choice == "3":
        quality = "480p"
    elif choice == "4":
        audio_only = True
    
    print(f"{Fore.YELLOW}開始下載...{Style.RESET_ALL}")
    success = downloader.download_video(url, quality=quality, audio_only=audio_only)
    
    if success:
        print(f"{Fore.GREEN}檔案保存在: {downloader.output_dir.absolute()}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}下載失敗{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}下載已取消{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")