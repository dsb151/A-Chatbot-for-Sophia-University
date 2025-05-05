# 🎓 A Chatbot for Sophia University

このリポジトリは、上智大学の学生向けに開発された情報提供チャットボットシステムです。学生生活における様々な質問（例：授業、施設、履修登録など）に、迅速かつ自動で回答することを目的としています。

## 📌 概要 / Overview

本チャットボットは、FlaskベースのWebアプリケーションで構築されており、以下の特徴を持ちます：

- 質問応答データは `qa1.json` に保存（階層構造対応）
- 管理者用UI (`admin/`) により、QAデータの編集が可能
- 日本語対応 / モバイル対応UI
- SimCSEモデルをベースとした意味検索機能（※未公開部分）

## 🗂️ ディレクトリ構成

├── app.py # Flask アプリのエントリポイント

├── manage.py # 管理画面のルーティング

├── templates/ # HTMLテンプレート

├── static/ # CSS / JS / 画像など

├── admin/ # 管理用ページ

├── qa1.json # 質問応答データ

├── suggestions.json # ユーザーからの提案を記録

├── requirements.txt # 依存パッケージ一覧



## 🚀 起動方法

Python 3.8 以降推奨。

```bash
# 仮想環境作成（任意）
python -m venv venv
source venv/bin/activate   # Windowsの場合は venv\Scripts\activate

# 依存ライブラリのインストール
pip install -r requirements.txt

# アプリ起動
python app.py
管理システム：manage.py


フレームワーク：Flask

フロントエンド：HTML / JavaScript / Bootstrap

データ形式：JSON（質問応答と提案管理）

NLPエンジン：SimCSE + cosine similarity（別リポジトリ）

📒 今後の展望
GPTベースの補助回答機能追加

質問履歴に基づくレコメンド

多言語対応（英語・中国語）

問い合わせ先

何か質問・提案があれば、GitHub Issue からお気軽にお知らせください！

