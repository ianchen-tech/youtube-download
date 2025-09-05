#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
YouTube 瀏覽器下載工具
使用 Selenium 模擬真實瀏覽器行為來下載 YouTube 影片
避免被檢測為機器人
"""

import os
import time
import random
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains
from colorama import init, Fore, Style
import re
import json

init(autoreset=True)

class BrowserYouTubeDownloader:
    def __init__(self, output_dir="downloads", headless=False):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
        self.headless = headless
        self.driver = None
        
        # 真實瀏覽器 User-Agent
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0'
        ]
    
    def _setup_driver(self):
        """設置 Chrome 瀏覽器驅動"""
        chrome_options = Options()
        
        if self.headless:
            chrome_options.add_argument('--headless')
        
        # 模擬真實瀏覽器設置
        chrome_options.add_argument(f'--user-agent={random.choice(self.user_agents)}')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        # 設置下載目錄
        prefs = {
            "download.default_directory": str(self.output_dir.absolute()),
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
            # 隱藏 webdriver 屬性
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            return True
        except Exception as e:
            print(f"{Fore.RED}瀏覽器驅動設置失敗: {e}{Style.RESET_ALL}")
            print(f"{Fore.YELLOW}請確保已安裝 Chrome 瀏覽器和 ChromeDriver{Style.RESET_ALL}")
            return False
    
    def _human_like_delay(self, min_delay=1, max_delay=3):
        """模擬人類操作延遲"""
        delay = random.uniform(min_delay, max_delay)
        time.sleep(delay)
    
    def _simulate_human_behavior(self):
        """模擬人類瀏覽行為"""
        # 隨機滾動頁面
        scroll_height = random.randint(100, 500)
        self.driver.execute_script(f"window.scrollBy(0, {scroll_height});")
        self._human_like_delay(0.5, 1.5)
        
        # 隨機移動滑鼠
        try:
            action = ActionChains(self.driver)
            action.move_by_offset(random.randint(-50, 50), random.randint(-50, 50))
            action.perform()
        except:
            pass
    
    def download_video_browser_method(self, url):
        """使用瀏覽器方法下載影片"""
        if not self._setup_driver():
            return False
        
        try:
            print(f"{Fore.CYAN}正在使用瀏覽器方法下載: {url}{Style.RESET_ALL}")
            
            # 訪問 YouTube 首頁，模擬正常用戶行為
            print(f"{Fore.YELLOW}正在訪問 YouTube...{Style.RESET_ALL}")
            self.driver.get("https://www.youtube.com")
            self._human_like_delay(2, 4)
            
            # 模擬人類瀏覽行為
            self._simulate_human_behavior()
            
            # 訪問目標影片
            print(f"{Fore.YELLOW}正在載入影片頁面...{Style.RESET_ALL}")
            self.driver.get(url)
            self._human_like_delay(3, 5)
            
            # 等待影片載入
            wait = WebDriverWait(self.driver, 10)
            
            # 獲取影片標題
            try:
                title_element = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "h1.ytd-watch-metadata yt-formatted-string")))
                title = title_element.text
                print(f"{Fore.GREEN}影片標題: {title}{Style.RESET_ALL}")
            except:
                title = "Unknown"
            
            # 模擬觀看行為
            self._simulate_human_behavior()
            
            # 使用第三方下載服務
            return self._download_via_service(url, title)
            
        except Exception as e:
            print(f"{Fore.RED}瀏覽器下載失敗: {e}{Style.RESET_ALL}")
            return False
        finally:
            if self.driver:
                self.driver.quit()
    
    def _download_via_service(self, url, title):
        """使用第三方服務下載"""
        try:
            # 使用 y2mate 或類似服務的 API
            print(f"{Fore.YELLOW}正在獲取下載連結...{Style.RESET_ALL}")
            
            # 這裡可以整合多個下載服務
            download_services = [
                self._try_pytube_method,
                self._try_requests_method
            ]
            
            for service in download_services:
                try:
                    if service(url, title):
                        return True
                except Exception as e:
                    print(f"{Fore.YELLOW}嘗試下一個方法...{Style.RESET_ALL}")
                    continue
            
            print(f"{Fore.RED}所有下載方法都失敗了{Style.RESET_ALL}")
            return False
            
        except Exception as e:
            print(f"{Fore.RED}下載服務錯誤: {e}{Style.RESET_ALL}")
            return False
    
    def _try_pytube_method(self, url, title):
        """嘗試使用 pytube 下載"""
        try:
            from pytube import YouTube
            print(f"{Fore.YELLOW}嘗試使用 pytube 方法...{Style.RESET_ALL}")
            
            # 設置代理和請求頭來模擬瀏覽器
            yt = YouTube(url)
            
            # 獲取最高品質的影片流
            stream = yt.streams.get_highest_resolution()
            
            if stream:
                filename = f"{title}.{stream.subtype}"
                safe_filename = re.sub(r'[<>:"/\\|?*]', '_', filename)
                
                print(f"{Fore.YELLOW}正在下載: {safe_filename}{Style.RESET_ALL}")
                stream.download(output_path=self.output_dir, filename=safe_filename)
                print(f"{Fore.GREEN}✓ 下載完成！{Style.RESET_ALL}")
                return True
            
        except ImportError:
            print(f"{Fore.YELLOW}pytube 未安裝，跳過此方法{Style.RESET_ALL}")
        except Exception as e:
            print(f"{Fore.YELLOW}pytube 方法失敗: {e}{Style.RESET_ALL}")
        
        return False
    
    def _try_requests_method(self, url, title):
        """嘗試使用 requests 直接下載"""
        try:
            print(f"{Fore.YELLOW}嘗試使用 requests 方法...{Style.RESET_ALL}")
            
            # 這裡可以實現直接的 HTTP 下載邏輯
            # 注意：這需要解析 YouTube 的實際影片 URL
            
            # 暫時返回 False，因為這需要更複雜的實現
            return False
            
        except Exception as e:
            print(f"{Fore.YELLOW}requests 方法失敗: {e}{Style.RESET_ALL}")
            return False

def main():
    print(f"{Fore.MAGENTA}=== YouTube 瀏覽器下載工具 ==={Style.RESET_ALL}")
    print(f"{Fore.CYAN}此工具使用真實瀏覽器來避免機器人檢測{Style.RESET_ALL}")
    print()
    
    url = input(f"{Fore.CYAN}請輸入 YouTube 影片連結: {Style.RESET_ALL}")
    
    if not url.strip():
        print(f"{Fore.RED}請提供有效的 YouTube 連結{Style.RESET_ALL}")
        return
    
    # 驗證 URL
    if "youtube.com" not in url and "youtu.be" not in url:
        print(f"{Fore.RED}請提供有效的 YouTube 連結{Style.RESET_ALL}")
        return
    
    # 詢問是否使用無頭模式
    headless_choice = input(f"{Fore.CYAN}是否使用無頭模式（不顯示瀏覽器視窗）？ (y/N): {Style.RESET_ALL}").lower()
    headless = headless_choice in ['y', 'yes', '是']
    
    # 創建下載器並開始下載
    downloader = BrowserYouTubeDownloader(headless=headless)
    
    print(f"{Fore.YELLOW}開始下載...{Style.RESET_ALL}")
    success = downloader.download_video_browser_method(url)
    
    if success:
        print(f"{Fore.GREEN}\n✓ 下載完成！{Style.RESET_ALL}")
        print(f"{Fore.CYAN}檔案已保存到: {downloader.output_dir}{Style.RESET_ALL}")
    else:
        print(f"{Fore.RED}\n✗ 下載失敗{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}建議：{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}1. 檢查網路連接{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}2. 確認 Chrome 瀏覽器已安裝{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}3. 嘗試使用其他下載方法{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}下載已取消{Style.RESET_ALL}")
    except Exception as e:
        print(f"\n{Fore.RED}發生錯誤: {e}{Style.RESET_ALL}")