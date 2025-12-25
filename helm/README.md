# Home Finance Dashboard - Helm Chart

Helmチャートを使用して、家庭内向け生活費可視化システムをKubernetesクラスターにデプロイします。

## 概要

このHelmチャートは、以下のリソースをデプロイします：

- **Backend Deployment**: FastAPI アプリケーション
- **Frontend Deployment**: Streamlit アプリケーション
- **Backend Service**: ClusterIP サービス
- **Frontend Service**: ClusterIP サービス
- **PersistentVolumeClaim**: SQLiteデータベース用ストレージ
- **Ingress**: パスベースルーティング

## 前提条件

- Kubernetes クラスター（k3s推奨）
- Helm 3.x
- kubectl がクラスターに接続できること
- （オプション）Ingress Controller（k3sの場合はTraefikがデフォルト）

## クイックスタート

### 1. インストール

```bash
# Namespaceの作成
kubectl create namespace home-finance

# Helmチャートのインストール
helm install home-finance . -n home-finance

# デプロイ状態の確認
kubectl get pods -n home-finance
kubectl get svc -n home-finance
kubectl get ingress -n home-finance
```

### 2. アクセス

**Ingressを使用する場合:**

```bash
# /etc/hostsに追加（ローカルマシン）
echo "<Kubernetes-Node-IP> home-finance.local" | sudo tee -a /etc/hosts

# ブラウザでアクセス
http://home-finance.local/
```

**NodePortを使用する場合:**

```bash
# values.yamlでNodePortを有効化
# service.type: NodePort

# アクセス
http://<Kubernetes-Node-IP>:30501  # Frontend
http://<Kubernetes-Node-IP>:30500  # Backend
```

### 3. アンインストール

```bash
# アプリケーションの削除（PVCは保持）
helm uninstall home-finance -n home-finance

# PVCも削除する場合
kubectl delete pvc home-finance-data -n home-finance

# Namespaceも削除する場合
kubectl delete namespace home-finance
```

## 設定値（values.yaml）

### イメージ設定

```yaml
backend:
  image:
    repository: home-finance-backend
    tag: latest
    pullPolicy: IfNotPresent

frontend:
  image:
    repository: home-finance-frontend
    tag: latest
    pullPolicy: IfNotPresent
```

**カスタマイズ例:**

```bash
# カスタムイメージを使用
helm install home-finance . \
  --set backend.image.repository=myregistry/backend \
  --set backend.image.tag=v1.0.0 \
  --set frontend.image.repository=myregistry/frontend \
  --set frontend.image.tag=v1.0.0
```

### レプリカ数

```yaml
backend:
  replicaCount: 1

frontend:
  replicaCount: 1
```

**スケールアウト例:**

```bash
# レプリカ数を増やす
helm upgrade home-finance . \
  --set backend.replicaCount=2 \
  --set frontend.replicaCount=2
```

### リソース制限

```yaml
backend:
  resources:
    requests:
      memory: "128Mi"
      cpu: "100m"
    limits:
      memory: "256Mi"
      cpu: "500m"

frontend:
  resources:
    requests:
      memory: "256Mi"
      cpu: "100m"
    limits:
      memory: "512Mi"
      cpu: "500m"
```

**カスタマイズ例:**

```bash
# リソース制限を変更
helm upgrade home-finance . \
  --set backend.resources.limits.memory=512Mi \
  --set frontend.resources.limits.memory=1Gi
```

### 環境変数

```yaml
backend:
  env:
    DATABASE_URL: "sqlite:////data/home_finance.db"
    TZ: "Asia/Tokyo"
    LOG_LEVEL: "INFO"

frontend:
  env:
    BACKEND_URL: "http://home-finance-backend:8000"
    TZ: "Asia/Tokyo"
    AUTO_REFRESH_INTERVAL: "30"
    KIOSK_MODE: "false"
```

**カスタマイズ例:**

```bash
# ログレベルを変更
helm upgrade home-finance . \
  --set backend.env.LOG_LEVEL=DEBUG

# Kioskモードを有効化
helm upgrade home-finance . \
  --set frontend.env.KIOSK_MODE=true
```

### ストレージ設定

```yaml
persistence:
  enabled: true
  storageClass: "local-path"  # k3sのデフォルト
  accessMode: ReadWriteOnce
  size: 1Gi
```

**カスタマイズ例:**

```bash
# ストレージサイズを変更
helm upgrade home-finance . \
  --set persistence.size=5Gi

# 異なるStorageClassを使用
helm upgrade home-finance . \
  --set persistence.storageClass=nfs-client
```

### Service設定

```yaml
backend:
  service:
    type: ClusterIP
    port: 8000

frontend:
  service:
    type: ClusterIP
    port: 8501
```

**NodePortに変更する例:**

```bash
# NodePortを使用
helm upgrade home-finance . \
  --set backend.service.type=NodePort \
  --set backend.service.nodePort=30500 \
  --set frontend.service.type=NodePort \
  --set frontend.service.nodePort=30501
```

### Ingress設定

```yaml
ingress:
  enabled: true
  className: "traefik"  # k3sのデフォルト
  host: "home-finance.local"
  annotations: {}
```

**カスタマイズ例:**

```bash
# ホスト名を変更
helm upgrade home-finance . \
  --set ingress.host=finance.example.com

# Ingressを無効化
helm upgrade home-finance . \
  --set ingress.enabled=false
```

### ヘルスチェック設定

```yaml
backend:
  livenessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 10
    periodSeconds: 30
  readinessProbe:
    httpGet:
      path: /health
      port: 8000
    initialDelaySeconds: 5
    periodSeconds: 10

frontend:
  livenessProbe:
    httpGet:
      path: /_stcore/health
      port: 8501
    initialDelaySeconds: 10
    periodSeconds: 30
  readinessProbe:
    httpGet:
      path: /_stcore/health
      port: 8501
    initialDelaySeconds: 5
    periodSeconds: 10
```

## カスタムvalues.yamlの使用

### 開発環境用

`values-dev.yaml` を作成：

```yaml
backend:
  image:
    tag: dev
  env:
    LOG_LEVEL: DEBUG

frontend:
  image:
    tag: dev
  env:
    KIOSK_MODE: "false"

persistence:
  size: 500Mi
```

デプロイ：

```bash
helm install home-finance . -f values-dev.yaml -n home-finance
```

### 本番環境用

`values-prod.yaml` を作成：

```yaml
backend:
  image:
    tag: v1.0.0
  replicaCount: 2
  resources:
    limits:
      memory: "512Mi"
      cpu: "1000m"

frontend:
  image:
    tag: v1.0.0
  replicaCount: 2
  env:
    KIOSK_MODE: "true"

persistence:
  size: 5Gi
  storageClass: "nfs-client"

ingress:
  host: "finance.home.local"
```

デプロイ：

```bash
helm install home-finance . -f values-prod.yaml -n home-finance
```

## アップグレード

### 設定変更のみ

```bash
# values.yamlを編集後
helm upgrade home-finance . -n home-finance

# または、コマンドラインで指定
helm upgrade home-finance . -n home-finance \
  --set backend.env.LOG_LEVEL=DEBUG
```

### イメージの更新

```bash
# 新しいイメージタグを指定
helm upgrade home-finance . -n home-finance \
  --set backend.image.tag=v1.1.0 \
  --set frontend.image.tag=v1.1.0
```

### ロールバック

```bash
# リビジョン履歴の確認
helm history home-finance -n home-finance

# 前のリビジョンにロールバック
helm rollback home-finance -n home-finance

# 特定のリビジョンにロールバック
helm rollback home-finance 2 -n home-finance
```

## トラブルシューティング

### Podが起動しない

```bash
# Pod状態の確認
kubectl get pods -n home-finance

# Pod詳細の確認
kubectl describe pod <pod-name> -n home-finance

# ログの確認
kubectl logs <pod-name> -n home-finance

# イベントの確認
kubectl get events -n home-finance --sort-by='.lastTimestamp'
```

### PVCがBoundにならない

```bash
# PVC状態の確認
kubectl get pvc -n home-finance

# PVC詳細の確認
kubectl describe pvc home-finance-data -n home-finance

# StorageClassの確認
kubectl get storageclass

# PVの確認
kubectl get pv
```

### Ingressが動作しない

```bash
# Ingress状態の確認
kubectl get ingress -n home-finance

# Ingress詳細の確認
kubectl describe ingress home-finance-ingress -n home-finance

# Ingress Controllerの確認（k3s）
kubectl get pods -n kube-system | grep traefik

# Ingress Controllerのログ確認
kubectl logs -n kube-system -l app.kubernetes.io/name=traefik
```

### データベースが初期化されない

```bash
# PVCのマウント確認
kubectl exec -it <backend-pod-name> -n home-finance -- ls -la /data

# データベースファイルの確認
kubectl exec -it <backend-pod-name> -n home-finance -- ls -la /data/home_finance.db

# データベースの再初期化（注意: データが削除されます）
kubectl delete pvc home-finance-data -n home-finance
helm upgrade home-finance . -n home-finance
```

### Backend APIに接続できない

```bash
# Service状態の確認
kubectl get svc -n home-finance

# Endpointsの確認
kubectl get endpoints -n home-finance

# Backend Podへの接続テスト
kubectl exec -it <frontend-pod-name> -n home-finance -- \
  curl http://home-finance-backend:8000/health

# ネットワークポリシーの確認
kubectl get networkpolicies -n home-finance
```

## モニタリング

### リソース使用状況

```bash
# Pod のリソース使用状況
kubectl top pods -n home-finance

# Node のリソース使用状況
kubectl top nodes
```

### ログの確認

```bash
# Backend ログ
kubectl logs -f deployment/home-finance-backend -n home-finance

# Frontend ログ
kubectl logs -f deployment/home-finance-frontend -n home-finance

# 全Podのログ
kubectl logs -f -l app.kubernetes.io/instance=home-finance -n home-finance
```

### メトリクス（Prometheus使用時）

```bash
# ServiceMonitorの作成（Prometheus Operatorを使用している場合）
kubectl apply -f - <<EOF
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: home-finance
  namespace: home-finance
spec:
  selector:
    matchLabels:
      app.kubernetes.io/instance: home-finance
  endpoints:
  - port: http
    interval: 30s
EOF
```

## バックアップとリストア

### データベースのバックアップ

```bash
# SQLiteファイルをローカルにコピー
kubectl cp home-finance/<backend-pod-name>:/data/home_finance.db \
  ./backup/home_finance_$(date +%Y%m%d).db -n home-finance

# または、PVCを直接マウントしてバックアップ
kubectl run backup --rm -it --image=busybox \
  --overrides='{"spec":{"volumes":[{"name":"data","persistentVolumeClaim":{"claimName":"home-finance-data"}}],"containers":[{"name":"backup","image":"busybox","volumeMounts":[{"name":"data","mountPath":"/data"}],"stdin":true,"tty":true}]}}' \
  -n home-finance
# コンテナ内で: tar czf /tmp/backup.tar.gz /data
```

### データベースのリストア

```bash
# バックアップファイルをPodにコピー
kubectl cp ./backup/home_finance_20251225.db \
  home-finance/<backend-pod-name>:/data/home_finance.db -n home-finance

# Podを再起動
kubectl rollout restart deployment/home-finance-backend -n home-finance
```

## PostgreSQLへの移行

将来的にPostgreSQLへ移行する場合の手順：

### 1. PostgreSQLのデプロイ

```bash
# Bitnami PostgreSQL Helmチャートを使用
helm repo add bitnami https://charts.bitnami.com/bitnami
helm install postgresql bitnami/postgresql \
  --set auth.username=homeadmin \
  --set auth.password=homepassword \
  --set auth.database=home_finance \
  -n home-finance
```

### 2. values.yamlの更新

```yaml
backend:
  env:
    DATABASE_URL: "postgresql://homeadmin:homepassword@postgresql:5432/home_finance"
```

### 3. データのマイグレーション

```bash
# SQLiteからエクスポート
kubectl exec -it <backend-pod-name> -n home-finance -- \
  sqlite3 /data/home_finance.db .dump > dump.sql

# PostgreSQLにインポート（適宜変換が必要）
kubectl exec -it postgresql-0 -n home-finance -- \
  psql -U homeadmin -d home_finance -f /tmp/dump.sql
```

### 4. アプリケーションの更新

```bash
helm upgrade home-finance . -n home-finance
```

## セキュリティ

### Secretの使用

機密情報はSecretで管理することを推奨します：

```bash
# Secretの作成
kubectl create secret generic home-finance-secrets \
  --from-literal=database-password=mypassword \
  -n home-finance

# values.yamlで参照
backend:
  env:
    DATABASE_PASSWORD:
      valueFrom:
        secretKeyRef:
          name: home-finance-secrets
          key: database-password
```

### NetworkPolicyの適用

```yaml
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: home-finance-network-policy
  namespace: home-finance
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/instance: home-finance
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: home-finance
  egress:
  - to:
    - namespaceSelector:
        matchLabels:
          name: home-finance
```

## ライセンス

このプロジェクトは家庭内利用を目的としています。
