# Argo CD Application Manifest

このディレクトリには、家庭内向け生活費可視化システムをArgo CDでデプロイするためのApplicationマニフェストが含まれています。

## ファイル

- `application.yaml`: Argo CD Applicationマニフェスト

## セットアップ手順

### 1. Argo CDのインストール

k3sクラスターにArgo CDをインストールします：

```bash
kubectl create namespace argocd
kubectl apply -n argocd -f https://raw.githubusercontent.com/argoproj/argo-cd/stable/manifests/install.yaml
```

### 2. Argo CD CLIのインストール（オプション）

```bash
# macOS
brew install argocd

# Linux
curl -sSL -o argocd-linux-amd64 https://github.com/argoproj/argo-cd/releases/latest/download/argocd-linux-amd64
sudo install -m 555 argocd-linux-amd64 /usr/local/bin/argocd
rm argocd-linux-amd64
```

### 3. Argo CD UIへのアクセス

```bash
# ポートフォワードでUIにアクセス
kubectl port-forward svc/argocd-server -n argocd 8080:443

# 初期パスワードを取得
kubectl -n argocd get secret argocd-initial-admin-secret -o jsonpath="{.data.password}" | base64 -d
```

ブラウザで https://localhost:8080 にアクセスし、以下の認証情報でログイン：
- ユーザー名: `admin`
- パスワード: 上記コマンドで取得したパスワード

### 4. Gitリポジトリの設定

`application.yaml` を編集して、実際のGitリポジトリURLに変更します：

```yaml
source:
  repoURL: https://github.com/[your-username]/home-finance.git  # 実際のリポジトリURLに変更
  targetRevision: main  # または使用するブランチ名
```

### 5. Applicationの適用

```bash
kubectl apply -f argocd/application.yaml
```

### 6. 同期の確認

Argo CD UIまたはCLIで同期状態を確認：

```bash
# CLI経由
argocd app get home-finance

# 手動同期（自動同期が有効な場合は不要）
argocd app sync home-finance
```

## GitOps設定

このApplicationマニフェストには以下のGitOps設定が含まれています：

### 自動同期（Automated Sync）

```yaml
syncPolicy:
  automated:
    prune: true
    selfHeal: true
```

- **prune: true**: Gitリポジトリから削除されたリソースをクラスターからも自動削除
- **selfHeal: true**: クラスター上で手動変更されたリソースを自動的にGitの状態に戻す

### 同期オプション

```yaml
syncOptions:
  - CreateNamespace=true
```

- **CreateNamespace=true**: ターゲットネームスペース（home-finance）が存在しない場合は自動作成

## トラブルシューティング

### Applicationが同期されない

```bash
# Applicationの状態を確認
kubectl get application home-finance -n argocd -o yaml

# Argo CDのログを確認
kubectl logs -n argocd deployment/argocd-application-controller
```

### リポジトリへのアクセスエラー

プライベートリポジトリの場合、Argo CDにリポジトリ認証情報を追加する必要があります：

```bash
argocd repo add https://github.com/[your-username]/home-finance.git \
  --username [your-username] \
  --password [your-token]
```

### 同期の一時停止

自動同期を一時的に無効化する場合：

```bash
argocd app set home-finance --sync-policy none
```

再度有効化：

```bash
argocd app set home-finance --sync-policy automated --auto-prune --self-heal
```

## 参考リンク

- [Argo CD Documentation](https://argo-cd.readthedocs.io/)
- [Argo CD Best Practices](https://argo-cd.readthedocs.io/en/stable/user-guide/best_practices/)
