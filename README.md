# 家庭内向け生活費可視化システム

家庭内LANで動作する、月次予算と支出を管理・可視化するシステムです。Raspberry Pi上のk3sクラスターでの運用を想定していますが、ローカル開発環境でも簡単に起動できます。

## 概要

このシステムは、家計の状態を「常に見える化」することで、消費抑制（行動変容）につなげることを目的としています。リビングのディスプレイに常時表示することで、家族全員が受動的に家計状況を把握できます。

### システム構成

- **Backend API** (FastAPI) - RESTful APIによるデータ管理とビジネスロジック
- **Frontend UI** (Streamlit) - ダッシュボードと入力フォーム
- **Database** (SQLite) - データ永続化（将来的にPostgreSQLへ移行可能）
- **Kubernetes** (k3s) - コンテナオーケストレーション
- **Helm** - デプロイメント管理
- **Argo CD** - GitOpsによる自動デプロイ

### アーキテクチャ

```
[スマホ/PC/Kioskディスプレイ]
         ↓
    [Ingress (Traefik)]
         ↓
    ┌────────┴────────┐
    ↓                 ↓
[Frontend Pod]   [Backend Pod]
(Streamlit)      (FastAPI)
                     ↓
              [SQLite on PVC]
```

## 主な機能

- 📊 **リアルタイム可視化**: 月次予算と支出の状況を一目で確認
- 💰 **カテゴリ別予算管理**: 食費、日用品、交通費など6カテゴリの予算設定
- 📝 **簡単な支出記録**: スマホやPCから数秒で支出を記録
- ⚠️ **3段階の警告表示**: 
  - 🟢 OK (使用率 < 70%)
  - 🟡 WARN (使用率 70-90%)
  - 🔴 DANGER (使用率 ≥ 90%)
- 📈 **自動集計**: 予算合計、使用合計、残額、残日数、1日あたり残予算を自動計算
- 🔄 **30秒ごとの自動更新**: 常に最新の状態を表示
- 📱 **レスポンシブデザイン**: スマホ、PC、Kioskモード対応
- 🏠 **家庭内LAN完結**: データは外部に送信されず、プライバシーを保護

## ローカル開発環境のセットアップ

### 前提条件

- Docker Desktop または Docker Engine + Docker Compose
- Git

### クイックスタート

1. **リポジトリのクローン**

```bash
git clone <repository-url>
cd home-finance-dashboard
```

2. **Docker Composeで起動**

```bash
docker-compose up --build
```

3. **アクセス**

- Frontend UI: http://localhost:8501
- Backend API: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs

4. **停止**

```bash
docker-compose down
```

データを保持したまま停止する場合は上記コマンドのみ。データも削除する場合は：

```bash
docker-compose down -v
```

### 開発モード

Docker Composeはホットリロードに対応しています。コードを変更すると自動的に反映されます。

- Backend: `uvicorn --reload` でホットリロード有効
- Frontend: Streamlitの自動リロード機能が有効

### ログの確認

```bash
# 全サービスのログ
docker-compose logs -f

# Backendのみ
docker-compose logs -f backend

# Frontendのみ
docker-compose logs -f frontend
```

### データベースの確認

SQLiteデータベースは `./data/home_finance.db` に保存されます。

```bash
# SQLiteクライアントで確認
sqlite3 ./data/home_finance.db

# テーブル一覧
.tables

# スキーマ確認
.schema budgets
.schema expenses
```

## ローカル開発（Docker不使用）

### Backend

```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend

```bash
cd frontend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
export BACKEND_URL=http://localhost:8000  # Windows: set BACKEND_URL=http://localhost:8000
streamlit run app/main.py
```

## API エンドポイント

### ヘルスチェック

```bash
curl http://localhost:8000/health
```

### 予算管理

```bash
# 予算登録
curl -X POST http://localhost:8000/api/budgets \
  -H "Content-Type: application/json" \
  -d '{"month": "2025-12", "category": "食費", "amount": 50000}'

# 予算一覧取得
curl http://localhost:8000/api/budgets?month=2025-12
```

### 支出記録

```bash
# 支出登録
curl -X POST http://localhost:8000/api/expenses \
  -H "Content-Type: application/json" \
  -d '{"date": "2025-12-25", "category": "食費", "amount": 3000, "memo": "スーパー"}'

# 支出一覧取得
curl http://localhost:8000/api/expenses?month=2025-12
```

### 月次集計

```bash
# 今月の集計取得
curl http://localhost:8000/api/summary

# 特定月の集計取得
curl http://localhost:8000/api/summary?month=2025-12
```

## テスト

### Backend テスト

```bash
cd backend
pytest
```

### Frontend テスト

```bash
cd frontend
pytest
```

## k8sデプロイメント（本番環境）

本番環境（Raspberry Pi上のk3s）へのデプロイ方法です。

### 前提条件

- k3sクラスターが稼働していること
- `kubectl` がクラスターに接続できること
- Helmがインストールされていること（v3以上）
- （オプション）Argo CDがインストールされていること

### 方法1: Helmによる手動デプロイ

```bash
# 1. Namespaceの作成（初回のみ）
kubectl create namespace home-finance

# 2. Helmチャートのインストール
helm install home-finance ./helm -n home-finance

# 3. デプロイ状態の確認
kubectl get pods -n home-finance
kubectl get svc -n home-finance
kubectl get ingress -n home-finance

# 4. ログの確認
kubectl logs -f deployment/home-finance-backend -n home-finance
kubectl logs -f deployment/home-finance-frontend -n home-finance
```

**アップグレード:**

```bash
# 設定変更後のアップグレード
helm upgrade home-finance ./helm -n home-finance

# values.yamlをカスタマイズしてアップグレード
helm upgrade home-finance ./helm -n home-finance -f custom-values.yaml
```

**アンインストール:**

```bash
# アプリケーションの削除（PVCは保持）
helm uninstall home-finance -n home-finance

# PVCも削除する場合
kubectl delete pvc home-finance-data -n home-finance
```

### 方法2: Argo CDによるGitOpsデプロイ（推奨）

GitOpsによる自動デプロイを実現します。コードをGitにプッシュするだけで自動的にデプロイされます。

```bash
# 1. Argo CD Applicationの作成
kubectl apply -f argocd/application.yaml

# 2. 同期状態の確認
kubectl get application home-finance -n argocd

# 3. Argo CD UIで確認
# http://<argocd-server>/applications/home-finance
```

**自動同期の動作:**
- Gitリポジトリの変更を検知して自動デプロイ
- 不要なリソースを自動削除（prune: true）
- 差分を自動修復（selfHeal: true）

詳細は各コンポーネントのREADMEを参照してください：
- [Backend README](./backend/README.md) - API仕様と開発手順
- [Frontend README](./frontend/README.md) - UI仕様と開発手順
- [Helm README](./helm/README.md) - デプロイ手順と設定値
- [Argo CD README](./argocd/README.md) - GitOps設定

### アクセス方法

デプロイ後、以下のURLでアクセスできます：

```bash
# /etc/hostsに追加（ローカルマシン）
echo "<Raspberry-Pi-IP> home-finance.local" | sudo tee -a /etc/hosts

# ブラウザでアクセス
http://home-finance.local/
```

または、Ingressを使用せずにNodePortでアクセス：

```bash
# Frontend
http://<Raspberry-Pi-IP>:30501

# Backend API
http://<Raspberry-Pi-IP>:30500
```

## トラブルシューティング

### ポートが既に使用されている

```bash
# ポート8000または8501が使用中の場合
docker-compose down
# または、docker-compose.ymlのポート番号を変更
```

### データベースが初期化されない

```bash
# データボリュームを削除して再作成
docker-compose down -v
docker-compose up --build
```

### Backendに接続できない

```bash
# Backendのヘルスチェック
curl http://localhost:8000/health

# コンテナのログ確認
docker-compose logs backend
```

### Frontendが表示されない

```bash
# Frontendのヘルスチェック
curl http://localhost:8501/_stcore/health

# コンテナのログ確認
docker-compose logs frontend
```

## プロジェクト構造

```
.
├── backend/              # Backend API (FastAPI)
│   ├── app/
│   │   ├── models/      # SQLAlchemyモデル
│   │   ├── schemas/     # Pydanticスキーマ
│   │   ├── repositories/# データアクセス層
│   │   ├── services/    # ビジネスロジック
│   │   └── routers/     # APIエンドポイント
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── frontend/            # Frontend UI (Streamlit)
│   ├── app/
│   │   ├── pages/       # ページコンポーネント
│   │   ├── components/  # UIコンポーネント
│   │   └── utils/       # ユーティリティ
│   ├── tests/
│   ├── Dockerfile
│   └── requirements.txt
├── helm/                # Helmチャート
│   ├── templates/
│   └── values.yaml
├── argocd/              # Argo CD Application
│   ├── application.yaml # Applicationマニフェスト
│   └── README.md
├── data/                # SQLiteデータベース（ローカル開発用）
├── docker-compose.yml   # ローカル開発環境
└── README.md
```

## ライセンス

このプロジェクトは家庭内利用を目的としています。

## サポート

問題が発生した場合は、Issueを作成してください。
