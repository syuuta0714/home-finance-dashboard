# Home Finance Dashboard - Backend

FastAPI backend for the home finance dashboard system.

## 概要

Backend APIは、家計データの管理と集計を担当するRESTful APIサーバーです。FastAPIを使用して高速かつ型安全なAPIを提供します。

### 技術スタック

- **Python**: 3.11+
- **FastAPI**: 非同期Webフレームワーク
- **SQLAlchemy**: ORM（Object-Relational Mapping）
- **Pydantic**: データバリデーションとシリアライゼーション
- **SQLite**: データベース（PostgreSQL移行可能）
- **Uvicorn**: ASGIサーバー

### アーキテクチャ

```
Routers (APIエンドポイント)
    ↓
Services (ビジネスロジック)
    ↓
Repositories (データアクセス)
    ↓
Models (SQLAlchemy)
    ↓
Database (SQLite)
```

## セットアップ

### ローカル開発環境

```bash
# 1. ディレクトリに移動
cd backend

# 2. 仮想環境の作成
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. 依存関係のインストール
pip install -r requirements.txt

# 4. 開発サーバーの起動
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Docker環境

```bash
# Dockerイメージのビルド
docker build -t home-finance-backend .

# コンテナの起動
docker run -p 8000:8000 \
  -v $(pwd)/data:/data \
  -e DATABASE_URL=sqlite:////data/home_finance.db \
  -e TZ=Asia/Tokyo \
  home-finance-backend
```

## 環境変数

| 変数名 | 説明 | デフォルト値 | 必須 |
|--------|------|-------------|------|
| `DATABASE_URL` | データベース接続URL | `sqlite:////data/home_finance.db` | No |
| `TZ` | タイムゾーン | `Asia/Tokyo` | No |
| `LOG_LEVEL` | ログレベル (DEBUG/INFO/WARNING/ERROR) | `INFO` | No |
| `CORS_ORIGINS` | CORS許可オリジン（JSON配列） | `["*"]` | No |

### 環境変数の設定例

```bash
# ローカル開発
export DATABASE_URL=sqlite:///./home_finance.db
export TZ=Asia/Tokyo
export LOG_LEVEL=DEBUG

# PostgreSQLへの移行例
export DATABASE_URL=postgresql://user:password@localhost:5432/home_finance
```

## API仕様

### ベースURL

- ローカル開発: `http://localhost:8000`
- k8s環境: `http://home-finance.local/api`

### 対話的APIドキュメント

サーバー起動後、以下のURLでAPIドキュメントを確認できます：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### エンドポイント一覧

#### ヘルスチェック

**GET /health**

サーバーの稼働状態を確認します。

```bash
curl http://localhost:8000/health
```

レスポンス:
```json
{
  "status": "ok"
}
```

---

#### 予算管理

**POST /api/budgets**

予算を登録または更新します（同じ月・カテゴリの組み合わせは上書き）。

リクエスト:
```bash
curl -X POST http://localhost:8000/api/budgets \
  -H "Content-Type: application/json" \
  -d '{
    "month": "2025-12",
    "category": "食費",
    "amount": 50000
  }'
```

レスポンス:
```json
{
  "id": 1,
  "month": "2025-12",
  "category": "食費",
  "amount": 50000,
  "created_at": "2025-12-25T10:00:00+09:00",
  "updated_at": "2025-12-25T10:00:00+09:00"
}
```

**GET /api/budgets**

予算一覧を取得します。

クエリパラメータ:
- `month` (optional): 月でフィルタ（YYYY-MM形式）

```bash
# 全予算取得
curl http://localhost:8000/api/budgets

# 特定月の予算取得
curl http://localhost:8000/api/budgets?month=2025-12
```

**GET /api/budgets/{id}**

予算の詳細を取得します。

```bash
curl http://localhost:8000/api/budgets/1
```

**DELETE /api/budgets/{id}**

予算を削除します。

```bash
curl -X DELETE http://localhost:8000/api/budgets/1
```

---

#### 支出管理

**POST /api/expenses**

支出を登録します。

リクエスト:
```bash
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{
    "date": "2025-12-25",
    "category": "食費",
    "amount": 3000,
    "memo": "スーパーで買い物"
  }'
```

レスポンス:
```json
{
  "id": 1,
  "date": "2025-12-25",
  "month": "2025-12",
  "category": "食費",
  "amount": 3000,
  "memo": "スーパーで買い物",
  "created_at": "2025-12-25T10:00:00+09:00"
}
```

**GET /api/expenses**

支出一覧を取得します。

クエリパラメータ:
- `month` (optional): 月でフィルタ（YYYY-MM形式）
- `category` (optional): カテゴリでフィルタ

```bash
# 全支出取得
curl http://localhost:8000/api/expenses

# 特定月の支出取得
curl http://localhost:8000/api/expenses?month=2025-12

# 特定カテゴリの支出取得
curl http://localhost:8000/api/expenses?category=食費

# 月とカテゴリで絞り込み
curl http://localhost:8000/api/expenses?month=2025-12&category=食費
```

**GET /api/expenses/{id}**

支出の詳細を取得します。

```bash
curl http://localhost:8000/api/expenses/1
```

**DELETE /api/expenses/{id}**

支出を削除します。

```bash
curl -X DELETE http://localhost:8000/api/expenses/1
```

---

#### 月次集計

**GET /api/summary**

月次集計データを取得します。

クエリパラメータ:
- `month` (optional): 月を指定（YYYY-MM形式）。省略時は今月。

```bash
# 今月の集計取得
curl http://localhost:8000/api/summary

# 特定月の集計取得
curl http://localhost:8000/api/summary?month=2025-12
```

レスポンス:
```json
{
  "month": "2025-12",
  "total_budget": 300000,
  "total_spent": 150000,
  "remaining": 150000,
  "remaining_days": 6,
  "per_day_budget": 25000.0,
  "usage_rate": 50.0,
  "status": "OK",
  "status_message": "予算内で順調です",
  "status_color": "green"
}
```

### カテゴリ一覧

現在サポートされているカテゴリ（将来的に編集可能にする予定）：

- 食費
- 日用品
- 交通費
- 娯楽
- 医療費
- その他

### エラーレスポンス

エラー時は以下の形式でレスポンスを返します：

```json
{
  "detail": "エラーメッセージ",
  "error_code": "ERROR_CODE"
}
```

エラーコード:
- `VALIDATION_ERROR` (400): バリデーションエラー
- `NOT_FOUND` (404): リソースが見つからない
- `CONFLICT` (409): 重複エラー
- `INTERNAL_ERROR` (500): サーバー内部エラー

## 開発

### ディレクトリ構造

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPIアプリケーション
│   ├── config.py            # 設定管理
│   ├── database.py          # データベース接続
│   ├── models/              # SQLAlchemyモデル
│   │   ├── budget.py
│   │   └── expense.py
│   ├── schemas/             # Pydanticスキーマ
│   │   ├── budget.py
│   │   ├── expense.py
│   │   └── summary.py
│   ├── repositories/        # データアクセス層
│   │   ├── base.py
│   │   ├── budget.py
│   │   └── expense.py
│   ├── services/            # ビジネスロジック
│   │   ├── budget.py
│   │   ├── expense.py
│   │   └── summary.py
│   └── routers/             # APIエンドポイント
│       ├── health.py
│       ├── budgets.py
│       ├── expenses.py
│       └── summary.py
├── tests/                   # テストコード
├── Dockerfile
├── requirements.txt
└── README.md
```

### レイヤーの責務

- **Routers**: HTTPリクエスト/レスポンス処理、バリデーション
- **Services**: ビジネスロジック、集計計算、日付処理
- **Repositories**: データアクセス、CRUD操作
- **Models**: SQLAlchemyモデル定義
- **Schemas**: Pydanticスキーマ、入出力バリデーション

### テスト

```bash
# テストの実行
pytest

# カバレッジ付きで実行
pytest --cov=app --cov-report=html

# 特定のテストファイルのみ実行
pytest tests/test_services.py
```

### データベースマイグレーション

現在はSQLAlchemyの`create_all()`を使用していますが、将来的にAlembicを使用したマイグレーション管理を推奨します。

```bash
# Alembicのセットアップ（将来）
alembic init alembic
alembic revision --autogenerate -m "Initial migration"
alembic upgrade head
```

### ログ

ログは標準出力に出力されます。k8s環境では`kubectl logs`で確認できます。

```bash
# ローカル開発
uvicorn app.main:app --log-level debug

# k8s環境
kubectl logs -f deployment/home-finance-backend -n home-finance
```

## デプロイ

### Docker

```bash
# イメージのビルド
docker build -t home-finance-backend:latest .

# コンテナの起動
docker run -d \
  -p 8000:8000 \
  -v /path/to/data:/data \
  -e DATABASE_URL=sqlite:////data/home_finance.db \
  -e TZ=Asia/Tokyo \
  --name home-finance-backend \
  home-finance-backend:latest
```

### Kubernetes

Helmチャートを使用してデプロイします。詳細は[Helm README](../helm/README.md)を参照してください。

```bash
# Helmでデプロイ
helm install home-finance ../helm -n home-finance
```

### ヘルスチェック

k8sのProbeで使用するヘルスチェックエンドポイント：

- **Liveness Probe**: `GET /health`
- **Readiness Probe**: `GET /health`

## トラブルシューティング

### データベース接続エラー

```bash
# データベースファイルのパーミッション確認
ls -la /data/home_finance.db

# データベースの初期化
rm /data/home_finance.db
# サーバー再起動で自動的に再作成されます
```

### タイムゾーンの問題

```bash
# タイムゾーンの確認
echo $TZ

# Asia/Tokyoに設定
export TZ=Asia/Tokyo
```

### ログレベルの変更

```bash
# DEBUGレベルでログを出力
export LOG_LEVEL=DEBUG
uvicorn app.main:app --reload
```

## PostgreSQLへの移行

将来的にPostgreSQLへ移行する場合の手順：

1. **PostgreSQLのセットアップ**
```bash
# k8sにPostgreSQLをデプロイ
helm install postgresql bitnami/postgresql -n home-finance
```

2. **環境変数の変更**
```bash
export DATABASE_URL=postgresql://user:password@postgresql:5432/home_finance
```

3. **データのマイグレーション**
```bash
# SQLiteからデータをエクスポート
sqlite3 home_finance.db .dump > dump.sql

# PostgreSQLにインポート（適宜変換が必要）
psql -U user -d home_finance -f dump.sql
```

4. **アプリケーションの再起動**

SQLAlchemyを使用しているため、コードの変更は不要です。

## ライセンス

このプロジェクトは家庭内利用を目的としています。
