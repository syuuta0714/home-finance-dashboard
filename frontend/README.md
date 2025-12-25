# Home Finance Dashboard - Frontend

Streamlit frontend for the home finance dashboard system.

## 概要

Frontend UIは、家計データの可視化と入力を担当するWebアプリケーションです。Streamlitを使用して、迅速な開発と直感的なUIを実現しています。

### 技術スタック

- **Python**: 3.11+
- **Streamlit**: Webアプリケーションフレームワーク
- **Requests**: HTTP通信ライブラリ
- **Pytz**: タイムゾーン処理

### 主な機能

- **ダッシュボード**: 月次集計のリアルタイム表示
- **支出追加**: 簡単な支出記録フォーム
- **予算管理**: カテゴリ別予算設定フォーム
- **自動更新**: 30秒ごとのデータ更新
- **レスポンシブデザイン**: スマホ、PC、Kioskモード対応

## セットアップ

### ローカル開発環境

```bash
# 1. ディレクトリに移動
cd frontend

# 2. 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. Backend URLの設定
export BACKEND_URL=http://localhost:8000  # Windows: set BACKEND_URL=http://localhost:8000

# 5. 開発サーバーの起動
streamlit run app/main.py
```

ブラウザで http://localhost:8501 にアクセスします。

### Docker環境

```bash
# Dockerイメージのビルド
docker build -t home-finance-frontend .

# コンテナの起動
docker run -p 8501:8501 \
  -e BACKEND_URL=http://backend:8000 \
  -e TZ=Asia/Tokyo \
  home-finance-frontend
```

## 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `BACKEND_URL` | Backend API URL | `http://home-finance-backend:8000` | Yes |
| `TZ` | タイムゾーン | `Asia/Tokyo` | No |
| `AUTO_REFRESH_INTERVAL` | 自動更新間隔（秒） | `30` | No |
| `KIOSK_MODE` | Kioskモード有効化 | `false` | No |

### 環境変数の設定例

```bash
# ローカル開発
export BACKEND_URL=http://localhost:8000
export TZ=Asia/Tokyo
export AUTO_REFRESH_INTERVAL=30
export KIOSK_MODE=false

# Kioskモード（大きいフォント、フルスクリーン）
export KIOSK_MODE=true
```

## UI仕様

### ページ構成

#### 1. ダッシュボード (`/`)

月次集計を大きく表示するメインページです。

**表示内容:**
- 📊 **予算合計**: 今月の予算総額
- 💰 **使用合計**: 今月の支出総額
- 💵 **残額**: 予算合計 - 使用合計
- 📅 **残日数**: 月末までの残り日数
- 📈 **1日あたり残予算**: 残額 / 残日数
- 📊 **使用率**: (使用合計 / 予算合計) × 100
- ⚠️ **状態表示**: OK（緑）/ WARN（黄）/ DANGER（赤）

**状態の判定基準:**
- 🟢 **OK**: 使用率 < 70%
- 🟡 **WARN**: 使用率 70-90%
- 🔴 **DANGER**: 使用率 ≥ 90%

**自動更新:**
- 30秒ごとに自動的にデータを再取得
- `st.rerun()` を使用した自動リフレッシュ

**Kioskモード:**
- 大きいフォント
- フルスクリーン表示
- 操作不要で常時表示

#### 2. 支出追加 (`/add_expense`)

支出を記録するフォームページです。

**入力項目:**
- **日付**: 支出日（デフォルト: 今日）
- **カテゴリ**: ドロップダウンで選択
  - 食費
  - 日用品
  - 交通費
  - 娯楽
  - 医療費
  - その他
- **金額**: 数値入力（円）
- **メモ**: 任意のテキスト入力

**バリデーション:**
- 金額は0以上の整数
- 日付はYYYY-MM-DD形式
- カテゴリは必須

**送信後:**
- 成功メッセージを表示
- フォームをクリア
- ダッシュボードに即座に反映

#### 3. 予算管理 (`/manage_budget`)

月別・カテゴリ別の予算を設定するフォームページです。

**入力項目:**
- **月**: YYYY-MM形式（例: 2025-12）
- **カテゴリ別予算**: 各カテゴリの予算額を入力
  - 食費
  - 日用品
  - 交通費
  - 娯楽
  - 医療費
  - その他

**機能:**
- 既存予算の表示と編集
- 同じ月・カテゴリの組み合わせは上書き
- 予算合計の自動計算

**バリデーション:**
- 月はYYYY-MM形式
- 金額は0以上の整数

**送信後:**
- 成功メッセージを表示
- ダッシュボードに即座に反映

### レスポンシブデザイン

- **スマホ**: 縦長レイアウト、タッチ操作対応
- **PC**: 横長レイアウト、マウス操作対応
- **Kiosk**: 大きいフォント、フルスクリーン表示

## 開発

### ディレクトリ構造

```
frontend/
├── app/
│   ├── __init__.py
│   ├── main.py              # Streamlitアプリケーション
│   ├── config.py            # 設定管理
│   ├── api_client.py        # Backend APIクライアント
│   ├── pages/               # ページコンポーネント
│   │   ├── __init__.py
│   │   ├── dashboard.py     # ダッシュボード
│   │   ├── add_expense.py   # 支出追加フォーム
│   │   └── manage_budget.py # 予算管理フォーム
│   ├── components/          # UIコンポーネント
│   │   ├── __init__.py
│   │   ├── status_card.py   # 状態表示カード
│   │   └── summary_card.py  # 集計表示カード
│   └── utils/               # ユーティリティ
│       ├── __init__.py
│       ├── formatting.py    # 数値・日付フォーマット
│       └── validation.py    # クライアント側バリデーション
├── tests/                   # テストコード
├── Dockerfile
├── requirements.txt
└── README.md
```

### コンポーネントの責務

- **main.py**: アプリケーションエントリーポイント、ページルーティング
- **api_client.py**: Backend APIとの通信、エラーハンドリング、リトライ
- **pages/**: 各ページのUI実装
- **components/**: 再利用可能なUIコンポーネント
- **utils/**: フォーマット、バリデーション等のユーティリティ

### APIクライアント

`api_client.py` は Backend API との通信を担当します。

**主な機能:**
- HTTPリクエストの送信
- エラーハンドリング
- リトライ機能（最大3回）
- タイムアウト設定

**使用例:**
```python
from app.api_client import APIClient

client = APIClient(base_url="http://localhost:8000")

# 集計データの取得
summary = client.get_summary(month="2025-12")

# 支出の登録
expense = client.create_expense({
    "date": "2025-12-25",
    "category": "食費",
    "amount": 3000,
    "memo": "スーパー"
})
```

### テスト

```bash
# テストの実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_api_client.py
```

### Streamlitの設定

`.streamlit/config.toml` でStreamlitの設定をカスタマイズできます：

```toml
[server]
port = 8501
headless = true
enableCORS = false

[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"
font = "sans serif"
```

## デプロイ

### Docker

```bash
# イメージのビルド
docker build -t home-finance-frontend:latest .

# コンテナの起動
docker run -d \
  -p 8501:8501 \
  -e BACKEND_URL=http://backend:8000 \
  -e TZ=Asia/Tokyo \
  --name home-finance-frontend \
  home-finance-frontend:latest
```

### Kubernetes

Helmチャートを使用してデプロイします。詳細は[Helm README](../helm/README.md)を参照してください。

```bash
# Helmでデプロイ
helm install home-finance ../helm -n home-finance
```

### ヘルスチェック

k8sのProbeで使用するヘルスチェックエンドポイント：

- **Liveness Probe**: `GET /_stcore/health`
- **Readiness Probe**: `GET /_stcore/health`

## トラブルシューティング

### Backend APIに接続できない

```bash
# Backend URLの確認
echo $BACKEND_URL

# Backend APIのヘルスチェック
curl $BACKEND_URL/health

# ネットワーク接続の確認
ping backend
```

### 自動更新が動作しない

```bash
# 自動更新間隔の確認
echo $AUTO_REFRESH_INTERVAL

# ブラウザのコンソールでエラーを確認
# F12キーを押して開発者ツールを開く
```

### Kioskモードが有効にならない

```bash
# Kioskモードの確認
echo $KIOSK_MODE

# trueに設定
export KIOSK_MODE=true

# Streamlitを再起動
```

### レイアウトが崩れる

```bash
# ブラウザのキャッシュをクリア
# Ctrl+Shift+R (Windows/Linux)
# Cmd+Shift+R (Mac)

# Streamlitのキャッシュをクリア
streamlit cache clear
```

## カスタマイズ

### カテゴリの追加

現在はコード内でカテゴリを定義していますが、将来的にはデータベースで管理する予定です。

カテゴリを追加する場合は、以下のファイルを編集してください：
- `app/pages/add_expense.py`
- `app/pages/manage_budget.py`

### 自動更新間隔の変更

```bash
# 60秒に変更
export AUTO_REFRESH_INTERVAL=60
```

### テーマのカスタマイズ

`.streamlit/config.toml` を編集してテーマをカスタマイズできます。

## ライセンス

このプロジェクトは家庭内利用を目的としています。
