# web-page-analyzer

## Overview
A tool that automatically captures web page screenshots and analyzes them using AI (GPT-4o-mini Vision). It consists of two main components:
1. Web Screenshot Tool: Captures full-page screenshots with scrolling support
2. AI Analysis Tool: Analyzes screenshots using GPT-4 Vision and outputs structured JSON data

## Installation
1. Clone the repository
```bash
git clone https://github.com/daishir0/web-page-analyzer.git
cd web-page-analyzer
```

2. Create and activate virtual environment
```bash
python -m venv venv
# For Windows
venv\Scripts\activate
# For macOS/Linux
source venv/bin/activate
```

3. Install required packages
```bash
pip install -r requirements.txt
```

4. Set up environment variables
- Copy `.env.sample` to `.env`
- Add your OpenAI API key to `.env`
- Set your Chrome Driver path in `.env` (optional, will use ChromeDriverManager if not set)
  ```
  CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe
  ```

## Usage
1. Prepare URL list
- Create `target_urls.txt` with target URLs (one per line)
- You can use `target_urls.txt.sample` as a template

2. Capture screenshots
```bash
python web_scraper.py --scroll-count 2
```

3. Analyze screenshots with AI
```bash
python image_analyzer.py
```

### Example: Scraping X (Twitter) Profiles
1. Create `target_urls.txt` with X profile URLs:
```
https://twitter.com/username1
https://x.com/username2
```

2. Use the default prompt (optimized for X profiles) or customize `prompt.txt`

3. Capture screenshots with multiple scrolls to get more tweets:
```bash
python web_scraper.py --scroll-count 3 --scroll-wait 3
```

4. Analyze the screenshots:
```bash
python image_analyzer.py
```

5. Check the results in `data/` directory. Example output:
```json
{
  "profile": {
    "display_name": "Example User",
    "username": "username1",
    "bio": "This is my bio",
    "location": "Tokyo, Japan",
    "website": "https://example.com",
    "joined": "2020-01-01",
    "followers_count": "1,234",
    "following_count": "567"
  },
  "tweets": [
    {
      "date": "2025-04-11",
      "text": "This is my latest tweet",
      "repost": 0
    },
    {
      "date": "2025-04-10",
      "text": "RT @someone: Interesting news",
      "repost": 1
    }
  ]
}
```

### Options
#### web_scraper.py
- `--input-file`: URL list file (default: target_urls.txt)
- `--output-dir`: Screenshot directory (default: screenshots)
- `--window-width`: Browser width (default: 900)
- `--window-height`: Browser height (default: 2400)
- `--scroll-count`: Number of scrolls (default: 1)
- `--scroll-wait`: Wait time between scrolls (default: 2s)
- `--load-wait`: Page load wait time (default: 10s)
- `--retry-count`: Number of retries on error (default: 3)
- `--wait-between`: Wait time between URLs (default: 5s)

#### image_analyzer.py
- `--input-dir`: Screenshot directory (default: screenshots)
- `--output-dir`: JSON output directory (default: data)
- `--prompt-file`: Prompt file (default: prompt.txt)
- `--model`: GPT model (default: gpt-4o-mini)

## Notes
- Check website terms of service before scraping
- Manage API keys securely
- Set appropriate wait times for large requests
- Screenshots and analysis results are saved in `screenshots/` and `data/` directories

## License
This project is licensed under the MIT License - see the LICENSE file for details.

---

# web-page-analyzer

## 概要
Webページのスクリーンショットを自動で撮影し、AI（GPT-4 Vision）で解析するツールです。主に2つのコンポーネントで構成されています：
1. Webスクリーンショットツール：スクロール対応の全画面キャプチャ
2. AI解析ツール：GPT-4 Visionによるスクリーンショット解析とJSON形式での出力

## インストール方法
1. リポジトリのクローン
```bash
git clone https://github.com/daishir0/web-page-analyzer.git
cd web-page-analyzer
```

2. 仮想環境の作成と有効化
```bash
python -m venv venv
# Windowsの場合
venv\Scripts\activate
# macOS/Linuxの場合
source venv/bin/activate
```

3. 必要なパッケージのインストール
```bash
pip install -r requirements.txt
```

4. 環境変数の設定
- `.env.sample`を`.env`にコピー
- OpenAI APIキーを`.env`に設定
- Chrome Driverのパスを`.env`に設定（任意、未設定の場合はChromeDriverManagerを使用）
  ```
  CHROME_DRIVER_PATH=C:\path\to\chromedriver.exe
  ```

## 使い方
1. URLリストの準備
- `target_urls.txt`に対象URLを1行ずつ記載
- `target_urls.txt.sample`をテンプレートとして使用可能

2. スクリーンショットの撮影
```bash
python web_scraper.py --scroll-count 2
```

3. AIによる解析
```bash
python image_analyzer.py
```

### 使用例：X（Twitter）プロフィールのスクレイピング
1. `target_urls.txt`にXのプロフィールURLを記載：
```
https://twitter.com/username1
https://x.com/username2
```

2. デフォルトのプロンプト（X用に最適化済み）を使用するか、`prompt.txt`をカスタマイズ

3. より多くのツイートを取得するため、複数回スクロールしてスクリーンショットを撮影：
```bash
python web_scraper.py --scroll-count 3 --scroll-wait 3
```

4. スクリーンショットを解析：
```bash
python image_analyzer.py
```

5. `data/`ディレクトリで結果を確認。出力例：
```json
{
  "profile": {
    "display_name": "サンプルユーザー",
    "username": "username1",
    "bio": "これは自己紹介です",
    "location": "東京",
    "website": "https://example.com",
    "joined": "2020-01-01",
    "followers_count": "1,234",
    "following_count": "567"
  },
  "tweets": [
    {
      "date": "2025-04-11",
      "text": "これは最新のツイートです",
      "repost": 0
    },
    {
      "date": "2025-04-10",
      "text": "RT @someone: 興味深いニュース",
      "repost": 1
    }
  ]
}
```

### オプション
#### web_scraper.py
- `--input-file`：URLリストファイル（デフォルト：target_urls.txt）
- `--output-dir`：スクリーンショット保存先（デフォルト：screenshots）
- `--window-width`：ブラウザの幅（デフォルト：900）
- `--window-height`：ブラウザの高さ（デフォルト：2400）
- `--scroll-count`：スクロール回数（デフォルト：1）
- `--scroll-wait`：スクロール間の待機時間（デフォルト：2秒）
- `--load-wait`：ページ読み込み待機時間（デフォルト：10秒）
- `--retry-count`：エラー時の再試行回数（デフォルト：3）
- `--wait-between`：URL間の待機時間（デフォルト：5秒）

#### image_analyzer.py
- `--input-dir`：スクリーンショット読み込み先（デフォルト：screenshots）
- `--output-dir`：JSON出力先（デフォルト：data）
- `--prompt-file`：プロンプトファイル（デフォルト：prompt.txt）
- `--model`：GPTモデル（デフォルト：gpt-4o-mini）

## 注意点
- スクレイピング前にウェブサイトの利用規約を確認してください
- APIキーは安全に管理してください
- 大量のリクエストを行う場合は適切な待機時間を設定してください
- スクリーンショットと解析結果は`screenshots/`と`data/`ディレクトリに保存されます

## ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。詳細はLICENSEファイルを参照してください。