"""
スクリーンショット画像をAI解析してJSONに変換するスクリプト

使用方法:
    python image_analyzer.py [options]

オプション:
    --input-dir TEXT    スクリーンショットの入力ディレクトリ (デフォルト: screenshots)
    --output-dir TEXT   JSON出力先ディレクトリ (デフォルト: data)
    --prompt-file TEXT  プロンプトファイル (デフォルト: prompt.txt)
    --model TEXT        使用するGPTモデル (デフォルト: gpt-4o-mini)

使用例:
    # デフォルト設定で実行
    python image_analyzer.py

    # カスタム設定で実行
    python image_analyzer.py --input-dir images --output-dir json --prompt-file custom_prompt.txt

    # 異なるモデルとファイルパターンを使用
    python image_analyzer.py --model gpt-4o --pattern "*.jpg"
"""

import os
import json
import base64
import argparse
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

def parse_args():
    """コマンドライン引数の解析"""
    parser = argparse.ArgumentParser(description='スクリーンショット画像をAI解析')
    parser.add_argument('--input-dir', default='screenshots',
                      help='スクリーンショットの入力ディレクトリ (デフォルト: screenshots)')
    parser.add_argument('--output-dir', default='data',
                      help='JSON出力先ディレクトリ (デフォルト: data)')
    parser.add_argument('--prompt-file', default='prompt.txt',
                      help='プロンプトファイル (デフォルト: prompt.txt)')
    parser.add_argument('--model', default='gpt-4o-mini',
                      help='使用するGPTモデル (デフォルト: gpt-4o-mini)')
    return parser.parse_args()

def load_prompt(prompt_file: str) -> str:
    """プロンプトファイルを読み込む"""
    try:
        with open(prompt_file, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        print(f"プロンプトファイル {prompt_file} が見つかりません。")
        raise

# 環境変数の読み込み
load_dotenv()

# OpenAIクライアントの初期化
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

class ImageAnalyzer:
    def __init__(self, config: argparse.Namespace):
        """
        Parameters:
        - config: 設定値を含むNamespace
        """
        self.config = config
        self.data_dir = Path(config.output_dir)
        self.data_dir.mkdir(exist_ok=True)
        self.input_dir = Path(config.input_dir)
        self.prompt = load_prompt(config.prompt_file)

    def analyze_image(self, image_path: Path):
        """画像を解析してJSONを生成"""
        print(f"\n画像解析中: {image_path}")
        
        # 画像をbase64エンコード
        with open(image_path, "rb") as image_file:
            base64_image = base64.b64encode(image_file.read()).decode("utf-8")

        try:
            # APIリクエスト
            response = client.chat.completions.create(
                model=self.config.model,
                messages=[
                    {"role": "system", "content": "You are a precise JSON-generating assistant that analyzes images."},
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": self.prompt},
                            {
                                "type": "image_url",
                                "image_url": {
                                    "url": f"data:image/png;base64,{base64_image}",
                                    "detail": "high"
                                }
                            }
                        ]
                    }
                ],
                max_tokens=2000
            )

            # JSONを取得
            json_data = response.choices[0].message.content
            
            try:
                # Markdownのコードブロックを除去
                json_data = json_data.strip()
                if json_data.startswith("```json"):
                    json_data = json_data[7:]  # "```json" を除去
                if json_data.endswith("```"):
                    json_data = json_data[:-3]  # "```" を除去
                json_data = json_data.strip()

                # JSONとして解析してフォーマットを整える
                parsed_json = json.loads(json_data)
                formatted_json = json.dumps(parsed_json, ensure_ascii=False, indent=2)
                
                # 同じファイル名（拡張子のみ.jsonに変更）でJSONを保存
                json_path = self.data_dir / f"{image_path.stem}.json"
                with open(json_path, "w", encoding="utf-8") as f:
                    f.write(formatted_json)
                print(f"解析結果をJSONとして保存しました: {json_path}")
                
            except json.JSONDecodeError as e:
                print(f"JSONの解析中にエラーが発生しました: {e}")
                print("APIからの生の応答:", json_data)

        except Exception as e:
            print(f"画像の解析中にエラーが発生しました: {e}")
            import traceback
            print("詳細なエラー情報:", traceback.format_exc())

def main():
    """メイン処理"""
    config = parse_args()
    
    try:
        print("\n=== 画像解析開始 ===")
        print(f"設定:")
        print(f"- 入力ディレクトリ: {config.input_dir}")
        print(f"- 出力ディレクトリ: {config.output_dir}")
        print(f"- プロンプトファイル: {config.prompt_file}")
        print(f"- 使用モデル: {config.model}")
        print("- 対象ファイル: PNG, JPG, JPEG")
        
        analyzer = ImageAnalyzer(config)
        input_dir = Path(config.input_dir)
        
        if not input_dir.exists():
            print(f"{config.input_dir}ディレクトリが見つかりません。")
            return
        
        # 画像ファイルを取得
        image_files = []
        for ext in ['*.png']:  # X用のスクリーンショットはPNGのみ
            image_files.extend(input_dir.glob(ext))
        
        # 作成日時でソート
        image_files.sort(key=lambda x: x.stat().st_mtime)
        
        if not image_files:
            print(f"{config.input_dir}ディレクトリに画像ファイルが見つかりません。")
            print("対応形式: PNG, JPG, JPEG")
            return
        
        print(f"\n処理対象ファイル: {len(image_files)}件")
        
        for i, image_path in enumerate(image_files, 1):
            print(f"\n[{i}/{len(image_files)}] {image_path.name} の解析開始")
            analyzer.analyze_image(image_path)
            print(f"{image_path.name} の解析完了")
            
        print("\n=== 全ての画像の解析が完了しました ===")
        
    except FileNotFoundError as e:
        print(f"ファイルが見つかりません: {e}")
    except Exception as e:
        print(f"予期せぬエラーが発生しました: {e}")
        import traceback
        print("詳細なエラー情報:", traceback.format_exc())

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\nプログラムが中断されました")