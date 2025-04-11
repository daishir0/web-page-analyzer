"""
Webページのスクリーンショットを自動取得するスクリプト

Example URLs in target_urls.txt:
https://x.com/username
https://twitter.com/username

使用方法:
    python web_scraper.py [options]

オプション:
    --input-file TEXT         URLリストのファイル名 (デフォルト: target_urls.txt)
    --output-dir TEXT        スクリーンショットの保存先ディレクトリ (デフォルト: screenshots)
    --window-width INTEGER   ブラウザウィンドウの幅 (デフォルト: 900)
    --window-height INTEGER  ブラウザウィンドウの高さ (デフォルト: 2400)
    --scroll-count INTEGER   スクロール回数 (デフォルト: 1)
    --scroll-wait INTEGER    スクロール間の待機時間（秒） (デフォルト: 2)
    --load-wait INTEGER      ページ読み込み後の待機時間（秒） (デフォルト: 10)
    --retry-count INTEGER    エラー時の再試行回数 (デフォルト: 3)
    --wait-between INTEGER   URL間の待機時間（秒） (デフォルト: 5)

使用例:
    # デフォルト設定で実行
    python web_scraper.py

    # カスタム設定で実行
    python web_scraper.py --input-file urls.txt --output-dir images --window-width 1200 --window-height 3000 --scroll-count 3

    # より多くのコンテンツを取得
    python web_scraper.py --scroll-count 5 --scroll-wait 3
"""

import asyncio
import time
import argparse
from datetime import datetime
from pathlib import Path
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from webdriver_manager.chrome import ChromeDriverManager
from fake_useragent import UserAgent
from PIL import Image
import io
import pathlib
from urllib.parse import urlparse

def parse_args():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description='Webページのスクリーンショットを自動取得')
    parser.add_argument('--input-file', default='target_urls.txt',
                      help='URLリストのファイル名 (デフォルト: target_urls.txt)')
    parser.add_argument('--output-dir', default='screenshots',
                      help='スクリーンショットの保存先ディレクトリ (デフォルト: screenshots)')
    parser.add_argument('--window-width', type=int, default=900,
                      help='ブラウザウィンドウの幅 (デフォルト: 900)')
    parser.add_argument('--window-height', type=int, default=2400,
                      help='ブラウザウィンドウの高さ (デフォルト: 2400)')
    parser.add_argument('--scroll-count', type=int, default=1,
                      help='スクロール回数 (デフォルト: 1)')
    parser.add_argument('--scroll-wait', type=int, default=2,
                      help='スクロール間の待機時間（秒） (デフォルト: 2)')
    parser.add_argument('--load-wait', type=int, default=10,
                      help='ページ読み込み後の待機時間（秒） (デフォルト: 10)')
    parser.add_argument('--retry-count', type=int, default=3,
                      help='エラー時の再試行回数 (デフォルト: 3)')
    parser.add_argument('--wait-between', type=int, default=5,
                      help='URL間の待機時間（秒） (デフォルト: 5)')
    return parser.parse_args()

def sanitize_url_for_filename(url: str) -> str:
    """URLをファイル名として使用可能な文字列に変換"""
    # プロトコルを除去（http:// or https:// → http-）
    url = url.replace('://', '-')
    # 特殊文字を置換
    replacements = {
        '/': '-',
        '\\': '-',
        ':': '-',
        '*': '-',
        '?': '-',
        '"': '-',
        '<': '-',
        '>': '-',
        '|': '-',
        ' ': '_'
    }
    for char, replacement in replacements.items():
        url = url.replace(char, replacement)
    return url

# グローバル変数としてWebDriverインスタンスを保持
driver = None

class WebScraper:
    def __init__(self, url: str, config: argparse.Namespace):
        """
        Parameters:
        - url: スクレイピング対象のURL
        - config: 設定値を含むNamespace
        """
        self.url = url
        self.config = config
        self.screenshots_dir = Path(config.output_dir)
        self.screenshots_dir.mkdir(exist_ok=True)
        self.ua = UserAgent()
        self.domain = urlparse(url).netloc

    def setup_driver(self):
        """Seleniumドライバーの設定"""
        print("Chrome WebDriverを設定中...")
        chrome_driver_path = os.getenv('CHROME_DRIVER_PATH')
        if not chrome_driver_path:
            print("CHROME_DRIVER_PATHが設定されていません。ChromeDriverManagerを使用します。")
            chrome_driver_path = ChromeDriverManager().install()
        service = Service(executable_path=chrome_driver_path)
        options = Options()
        
        # ユーザーデータディレクトリを設定
        user_data_dir = pathlib.Path.home() / "chrome-data"
        user_data_dir.mkdir(exist_ok=True)
        options.add_argument(f"--user-data-dir={user_data_dir}")
        
        # ウィンドウサイズを設定
        options.add_argument(f"--window-size={self.config.window_width},{self.config.window_height}")
        # プロファイルディレクトリを設定
        options.add_argument("--profile-directory=Default")
        
        options.add_argument('--disable-extensions')  # 拡張機能を無効化
        options.add_argument('--disable-infobars')   # 情報バーを無効化
        options.add_argument(f'user-agent={self.ua.random}')

        try:
            driver = webdriver.Chrome(service=service, options=options)
            print("Chrome WebDriverの設定が完了しました")
            return driver
        except Exception as e:
            print(f"Chrome WebDriverの設定エラー: {e}")
            raise

    def take_full_page_screenshot(self, driver):
        """ページ全体のスクリーンショットを撮影して1つの画像に結合"""
        # URLをファイル名として使用可能な形式に変換
        filename = sanitize_url_for_filename(self.url)
        screenshot_path = self.screenshots_dir / f"{filename}.png"
        
        # ページ全体が読み込まれるまで待機
        try:
            WebDriverWait(driver, 20).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            print("ページの読み込みが完了しました")
        except TimeoutException:
            print("ページの読み込みタイムアウト - 再試行を続けます")
            time.sleep(5)  # 少し待機してから続行

        # スクロールしながらスクリーンショットを撮影
        print("コンテンツを読み込んでいます...")
        screenshots = []
        last_height = driver.execute_script("return document.body.scrollHeight")
        total_height = 0
        window_height = driver.execute_script("return window.innerHeight")
        
        scroll_attempts = 0
        max_scrolls = self.config.scroll_count

        while scroll_attempts < max_scrolls:
            # 現在の表示部分のスクリーンショットを撮影
            screenshot = driver.get_screenshot_as_png()
            image = Image.open(io.BytesIO(screenshot))
            screenshots.append(image)
            total_height += window_height

            # スクロール
            driver.execute_script(f"window.scrollBy(0, {window_height});")
            time.sleep(self.config.scroll_wait)
            scroll_attempts += 1
            print(f"スクロール {scroll_attempts}/{max_scrolls}")

            # 新しい高さを取得
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("これ以上スクロールできません")
                break
            last_height = new_height

        # スクリーンショットを結合
        print("スクリーンショットを結合しています...")
        total_width = screenshots[0].width
        combined_screenshot = Image.new('RGB', (total_width, total_height))
        
        y_offset = 0
        for img in screenshots:
            combined_screenshot.paste(img, (0, y_offset))
            y_offset += img.height
            img.close()

        try:
            combined_screenshot.save(str(screenshot_path))
            print(f"結合したスクリーンショットを保存しました: {screenshot_path}")
        except Exception as e:
            print(f"スクリーンショット保存中にエラーが発生しました: {e}")
        finally:
            combined_screenshot.close()
            
        return screenshot_path

    async def scrape(self):
        """スクリーンショット取得の実行（非同期版）"""
        global driver
        
        for attempt in range(self.config.retry_count):
            try:
                if driver is None:
                    driver = self.setup_driver()
                
                print(f"URLにアクセス中: {self.url}")
                driver.get(self.url)
                
                try:
                    # ページの読み込みを待機
                    WebDriverWait(driver, 30).until(
                        EC.presence_of_element_located((By.TAG_NAME, "body"))
                    )
                    print("ページの読み込みが完了しました")
                except TimeoutException:
                    print("ページの読み込みがタイムアウトしました - 処理を継続します")

                # 初期読み込みを待機（非同期sleep）
                await asyncio.sleep(self.config.load_wait)

                # スクリーンショットを撮影
                return self.take_full_page_screenshot(driver)
                
            except Exception as e:
                print(f"試行 {attempt + 1}/{self.config.retry_count} でエラーが発生: {e}")
                if attempt < self.config.retry_count - 1:
                    print(f"{self.config.wait_between}秒後に再試行します...")
                    await asyncio.sleep(self.config.wait_between)
                    if driver:
                        driver.quit()
                        driver = None
                else:
                    raise

async def main():
    """メイン処理"""
    config = parse_args()
    
    try:
        print("\n=== スクリーンショット撮影開始 ===")
        print(f"設定:")
        print(f"- 入力ファイル: {config.input_file}")
        print(f"- 出力ディレクトリ: {config.output_dir}")
        print(f"- ウィンドウサイズ: {config.window_width}x{config.window_height}")
        print(f"- スクロール回数: {config.scroll_count}")
        print(f"- スクロール待機時間: {config.scroll_wait}秒")
        print(f"- ページ読み込み待機時間: {config.load_wait}秒")
        print(f"- 再試行回数: {config.retry_count}")
        print(f"- URL間待機時間: {config.wait_between}秒")
        
        # URLリストを読み込む
        with open(config.input_file, 'r', encoding='utf-8') as f:
            urls = [line.strip() for line in f if line.strip()]
        
        if not urls:
            print(f"{config.input_file}にURLが記載されていません。")
            return
        
        print(f"\n処理対象URL: {len(urls)}件")
        
        for i, url in enumerate(urls, 1):
            print(f"\n[{i}/{len(urls)}] {url} のスクリーンショット撮影開始")
            scraper = WebScraper(url, config)
            try:
                await scraper.scrape()
                print(f"{url} のスクリーンショット撮影完了")
                # 次のURLの処理のために少し待機
                if i < len(urls):
                    print(f"{config.wait_between}秒待機します...")
                    await asyncio.sleep(config.wait_between)
            except Exception as e:
                print(f"!!! {url} のスクリーンショット撮影中にエラー: {e}")
                continue
        
        print("\n=== 全URLのスクリーンショット撮影完了 ===")
        
    except FileNotFoundError:
        print(f"{config.input_file} が見つかりません。")
        print("ファイルを作成し、1行に1URLを記載してください。")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        import traceback
        print("詳細なエラー情報:", traceback.format_exc())
    finally:
        if driver:
            driver.quit()
            print("ブラウザを終了しました。")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nプログラムが中断されました")
        if driver:
            driver.quit()
            print("ブラウザを終了しました。")