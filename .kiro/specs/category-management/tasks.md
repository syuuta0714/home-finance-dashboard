# 月次予算カテゴリ拡張・管理機能 - 実装計画

## 実装タスク

- [x] 1. データベーススキーマの実装
  - [x] 1.1 Category モデルの作成
    - SQLAlchemy モデルを定義（id, name, type, is_active, note）
    - _要件: 1_
  - [x] 1.2 MonthlyBudget モデルの作成
    - SQLAlchemy モデルを定義（month, category_id, amount）
    - Unique constraint を設定（month + category_id）
    - _要件: 2_
  - [x] 1.3 データベースマイグレーション
    - 新しいテーブルを作成
    - 既存の Budget テーブルとの関係を確認
    - _要件: 6_

- [x] 2. Pydantic スキーマの実装
  - [x] 2.1 CategorySchema の作成
    - CategorySchema（読み取り用）を定義
    - _要件: 1_
  - [x] 2.2 MonthlyBudgetSchema の作成
    - MonthlyBudgetSchema（読み取り用）を定義
    - MonthlyBudgetCreateSchema（作成用）を定義
    - MonthlyBudgetDetailSchema（詳細表示用）を定義
    - _要件: 2, 5_

- [x] 3. リポジトリ層の実装
  - [x] 3.1 CategoryRepository の作成
    - BaseRepository を継承
    - get_by_type() メソッドを実装
    - get_all_active() メソッドを実装
    - _要件: 1_
  - [x] 3.2 MonthlyBudgetRepository の作成
    - BaseRepository を継承
    - get_by_month() メソッドを実装
    - get_by_month_and_category() メソッドを実装
    - get_by_month_and_type() メソッドを実装
    - get_total_by_month() メソッドを実装
    - upsert() メソッドを実装（上書き登録）
    - _要件: 2, 4, 5_

- [x] 4. サービス層の実装
  - [x] 4.1 CategoryService の作成
    - get_all_categories() メソッドを実装
    - get_categories_by_type() メソッドを実装
    - get_category_by_id() メソッドを実装
    - initialize_default_categories() メソッドを実装
    - _要件: 1, 3_
  - [x] 4.2 MonthlyBudgetService の作成
    - register_budget() メソッドを実装
    - get_budgets_by_month() メソッドを実装
    - get_budgets_by_month_and_type() メソッドを実装
    - get_budget_total() メソッドを実装
    - delete_budget() メソッドを実装
    - initialize_default_budgets() メソッドを実装
    - _要件: 2, 3, 4, 5_

- [x] 5. API ルーターの実装
  - [x] 5.1 カテゴリ API ルーターの作成
    - GET /api/categories エンドポイント（フィルタ対応）
    - GET /api/categories/{category_id} エンドポイント
    - _要件: 1_
  - [x] 5.2 月次予算 API ルーターの作成
    - POST /api/monthly-budgets エンドポイント
    - GET /api/monthly-budgets エンドポイント（フィルタ対応）
    - GET /api/monthly-budgets/{budget_id} エンドポイント
    - DELETE /api/monthly-budgets/{budget_id} エンドポイント
    - GET /api/monthly-budgets/summary/{month} エンドポイント
    - _要件: 2, 4, 5_

- [x] 6. 初期データの実装
  - [x] 6.1 デフォルトカテゴリの登録
    - 14個の標準カテゴリをデータベースに登録
    - 初回起動時に自動実行
    - _要件: 1, 3_
  - [x] 6.2 デフォルト月次予算の登録
    - 当月のデフォルト予算を自動登録
    - 重複登録を防止
    - _要件: 3_

- [x] 7. 既存機能との統合
  - [x] 7.1 既存の Budget モデルとの互換性確認
    - 既存の支出・予算機能が新しいカテゴリシステムと連携することを確認
    - _要件: 6_
  - [x] 7.2 既存の Summary 機能の更新
    - 新しいカテゴリシステムに対応
    - _要件: 6_

- [x] 8. テストの実装
  - [x] 8.1 CategoryService のユニットテスト
    - get_all_categories() のテスト
    - get_categories_by_type() のテスト
    - initialize_default_categories() のテスト
    - _要件: 1, 3_
  - [x] 8.2 MonthlyBudgetService のユニットテスト
    - register_budget() のテスト
    - get_budgets_by_month() のテスト
    - get_budget_total() のテスト
    - initialize_default_budgets() のテスト
    - _要件: 2, 3, 4, 5_
  - [x] 8.3 API エンドポイントの統合テスト
    - カテゴリ API のテスト
    - 月次予算 API のテスト
    - 初期データ登録のテスト
    - _要件: 1, 2, 3, 4, 5_
  - [x]* 8.4 既存機能との互換性テスト
    - 既存の支出・予算機能が正常に動作することを確認
    - _要件: 6_

- [x] 9. ドキュメントの更新
  - [x] 9.1 Backend README の更新
    - 新しい API エンドポイントのドキュメント追加
    - _要件: 1, 2, 4, 5_
  - [x] 9.2 API ドキュメント（Swagger）の確認
    - 新しいエンドポイントが正しく表示されることを確認
    - _要件: 1, 2, 4, 5_
