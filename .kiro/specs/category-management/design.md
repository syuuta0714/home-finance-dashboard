# 月次予算カテゴリ拡張・管理機能 - 設計書

## 概要

本設計では、カテゴリマスタの実装、月次予算管理機能の拡張、初期データの自動登録を実現します。

## アーキテクチャ

```
Frontend (Streamlit)
    ↓
API Router (FastAPI)
    ↓
Service Layer (ビジネスロジック)
    ↓
Repository Layer (データアクセス)
    ↓
SQLAlchemy Models
    ↓
SQLite Database
```

## コンポーネント設計

### 1. データモデル

#### Category (カテゴリマスタ)

```python
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(String(50), primary_key=True)  # housing, utilities, etc.
    name = Column(String(100), nullable=False)  # 住居, 光熱費, etc.
    type = Column(String(20), nullable=False)  # fixed, variable, lifestyle, event
    is_active = Column(Boolean, default=True)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
```

#### MonthlyBudget (月次予算)

```python
class MonthlyBudget(Base):
    __tablename__ = "monthly_budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False)  # YYYY-MM
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    amount = Column(Integer, nullable=False)  # 月額（円）
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, onupdate=func.now())
    
    # Unique constraint: 同じ月・カテゴリの組み合わせは1つのみ
    __table_args__ = (
        UniqueConstraint('month', 'category_id', name='uq_month_category'),
    )
```

### 2. Pydantic スキーマ

#### CategorySchema

```python
class CategorySchema(BaseModel):
    id: str
    name: str
    type: str  # fixed, variable, lifestyle, event
    is_active: bool
    note: Optional[str]
    
    class Config:
        from_attributes = True
```

#### MonthlyBudgetSchema

```python
class MonthlyBudgetSchema(BaseModel):
    id: int
    month: str
    category_id: str
    amount: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class MonthlyBudgetCreateSchema(BaseModel):
    month: str
    category_id: str
    amount: int
```

#### MonthlyBudgetDetailSchema

```python
class MonthlyBudgetDetailSchema(BaseModel):
    category_id: str
    category_name: str
    category_type: str
    amount: int
```

### 3. API エンドポイント

#### カテゴリ管理

- `GET /api/categories` - カテゴリ一覧取得
  - Query: `type` (optional) - カテゴリタイプでフィルタ
  - Response: `List[CategorySchema]`

- `GET /api/categories/{category_id}` - カテゴリ詳細取得
  - Response: `CategorySchema`

#### 月次予算管理

- `POST /api/monthly-budgets` - 月次予算登録/更新
  - Body: `MonthlyBudgetCreateSchema`
  - Response: `MonthlyBudgetSchema`

- `GET /api/monthly-budgets` - 月次予算一覧取得
  - Query: `month` (required) - YYYY-MM形式
  - Query: `category_type` (optional) - カテゴリタイプでフィルタ
  - Response: `List[MonthlyBudgetDetailSchema]`

- `GET /api/monthly-budgets/{budget_id}` - 月次予算詳細取得
  - Response: `MonthlyBudgetSchema`

- `DELETE /api/monthly-budgets/{budget_id}` - 月次予算削除
  - Response: `{"message": "deleted"}`

- `GET /api/monthly-budgets/summary/{month}` - 月次予算合計取得
  - Response: `{"month": "2025-12", "total_budget": 325000}`

### 4. サービス層

#### CategoryService

```python
class CategoryService:
    def get_all_categories(self) -> List[Category]
    def get_categories_by_type(self, category_type: str) -> List[Category]
    def get_category_by_id(self, category_id: str) -> Optional[Category]
    def initialize_default_categories(self) -> None
```

#### MonthlyBudgetService

```python
class MonthlyBudgetService:
    def register_budget(self, budget_data: MonthlyBudgetCreateSchema) -> MonthlyBudget
    def get_budgets_by_month(self, month: str) -> List[MonthlyBudget]
    def get_budgets_by_month_and_type(self, month: str, category_type: str) -> List[MonthlyBudget]
    def get_budget_total(self, month: str) -> int
    def delete_budget(self, budget_id: int) -> bool
    def initialize_default_budgets(self, month: str) -> None
```

### 5. リポジトリ層

#### CategoryRepository

```python
class CategoryRepository(BaseRepository[Category]):
    def get_by_type(self, category_type: str) -> List[Category]
    def get_all_active(self) -> List[Category]
```

#### MonthlyBudgetRepository

```python
class MonthlyBudgetRepository(BaseRepository[MonthlyBudget]):
    def get_by_month(self, month: str) -> List[MonthlyBudget]
    def get_by_month_and_category(self, month: str, category_id: str) -> Optional[MonthlyBudget]
    def get_by_month_and_type(self, month: str, category_type: str) -> List[MonthlyBudget]
    def get_total_by_month(self, month: str) -> int
    def upsert(self, month: str, category_id: str, amount: int) -> MonthlyBudget
```

## 初期データ

### 14個の標準カテゴリ

| ID | 名前 | タイプ | 説明 |
|---|---|---|---|
| housing | 住居 | fixed | 住宅ローン・家賃 |
| utilities | 光熱費 | fixed | 電気・ガス・水道 |
| communication | 通信費 | fixed | 携帯・インターネット |
| insurance | 保険 | fixed | 生命保険・損害保険 |
| taxes | 税金 | fixed | 所得税・住民税・固定資産税 |
| food | 食費 | variable | 食材・外食 |
| daily_goods | 日用品 | variable | 日用雑貨・消耗品 |
| transportation | 交通費 | variable | ガソリン・公共交通 |
| medical | 医療費 | variable | 医療・薬 |
| entertainment | 娯楽・趣味 | lifestyle | 映画・本・ゲーム |
| social | 交際費 | lifestyle | 飲み会・プレゼント |
| clothing | 被服・美容 | lifestyle | 衣類・美容 |
| education | 教育 | event | 学費・教材 |
| special | 特別支出 | event | 旅行・家電・突発費 |

### デフォルト月次予算

```json
{
  "housing": 50656,
  "utilities": 17000,
  "communication": 11633,
  "insurance": 10350,
  "taxes": 25583,
  "food": 90000,
  "daily_goods": 20000,
  "transportation": 15000,
  "medical": 3000,
  "entertainment": 24000,
  "social": 10000,
  "clothing": 10000,
  "education": 39000,
  "special": 0
}
```

合計: 325,856円

## エラーハンドリング

| エラー | ステータス | メッセージ |
|---|---|---|
| カテゴリが見つからない | 404 | Category not found |
| 月次予算が見つからない | 404 | Monthly budget not found |
| バリデーションエラー | 422 | Validation error |
| 重複登録 | 409 | Budget already exists for this month and category |

## テスト戦略

### ユニットテスト

- CategoryService のテスト
- MonthlyBudgetService のテスト
- CategoryRepository のテスト
- MonthlyBudgetRepository のテスト

### 統合テスト

- API エンドポイントのテスト
- 初期データ登録のテスト
- 既存機能との互換性テスト

### 手動テスト

- UI での予算設定フロー
- 既存の支出・予算機能との連携確認

## 既存機能との互換性

### 既存の Budget モデルとの関係

- 既存の `Budget` モデルは `MonthlyBudget` に統合される
- 既存のカテゴリ（食費、日用品など）は新しいカテゴリマスタにマッピングされる
- 既存の API は後方互換性を保つ

### マイグレーション戦略

1. 新しい `Category` テーブルを作成
2. 新しい `MonthlyBudget` テーブルを作成
3. 既存の `Budget` データを `MonthlyBudget` にマイグレーション
4. 既存の API は新しいテーブルを使用するように更新
5. 古いテーブルは段階的に廃止

## 今後の拡張

- ユーザーカスタムカテゴリの追加
- カテゴリの並び順カスタマイズ
- カテゴリ別の目標値設定
- カテゴリ別の実績分析
