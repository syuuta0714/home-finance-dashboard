"""Category service for business logic"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.category import CategoryRepository
from app.schemas.category import CategorySchema
from app.models.category import Category


class CategoryService:
    """Service for category business logic"""
    
    # Default categories data
    DEFAULT_CATEGORIES = [
        {
            "id": "housing",
            "name": "住居",
            "type": "fixed",
            "note": "住宅ローン・家賃"
        },
        {
            "id": "utilities",
            "name": "光熱費",
            "type": "fixed",
            "note": "電気・ガス・水道"
        },
        {
            "id": "communication",
            "name": "通信費",
            "type": "fixed",
            "note": "携帯・インターネット"
        },
        {
            "id": "insurance",
            "name": "保険",
            "type": "fixed",
            "note": "生命保険・損害保険"
        },
        {
            "id": "taxes",
            "name": "税金",
            "type": "fixed",
            "note": "所得税・住民税・固定資産税"
        },
        {
            "id": "food",
            "name": "食費",
            "type": "variable",
            "note": "食材・外食"
        },
        {
            "id": "daily_goods",
            "name": "日用品",
            "type": "variable",
            "note": "日用雑貨・消耗品"
        },
        {
            "id": "transportation",
            "name": "交通費",
            "type": "variable",
            "note": "ガソリン・公共交通"
        },
        {
            "id": "medical",
            "name": "医療費",
            "type": "variable",
            "note": "医療・薬"
        },
        {
            "id": "entertainment",
            "name": "娯楽・趣味",
            "type": "lifestyle",
            "note": "映画・本・ゲーム"
        },
        {
            "id": "social",
            "name": "交際費",
            "type": "lifestyle",
            "note": "飲み会・プレゼント"
        },
        {
            "id": "clothing",
            "name": "被服・美容",
            "type": "lifestyle",
            "note": "衣類・美容"
        },
        {
            "id": "education",
            "name": "教育",
            "type": "event",
            "note": "学費・教材"
        },
        {
            "id": "special",
            "name": "特別支出",
            "type": "event",
            "note": "旅行・家電・突発費"
        },
    ]
    
    def __init__(self, db: Session):
        """
        Initialize Category service.
        
        Args:
            db: Database session
        """
        self.repository = CategoryRepository(db)
        self.db = db
    
    def get_all_categories(self) -> List[CategorySchema]:
        """
        Get all categories.
        
        Returns:
            List of CategorySchema instances
        """
        categories = self.repository.get_all()
        return [CategorySchema.model_validate(cat) for cat in categories]
    
    def get_categories_by_type(self, category_type: str) -> List[CategorySchema]:
        """
        Get all categories of a specific type.
        
        Args:
            category_type: Category type (fixed, variable, lifestyle, event)
            
        Returns:
            List of CategorySchema instances for the specified type
        """
        categories = self.repository.get_by_type(category_type)
        return [CategorySchema.model_validate(cat) for cat in categories]
    
    def get_category_by_id(self, category_id: str) -> Optional[CategorySchema]:
        """
        Get a category by ID.
        
        Args:
            category_id: Category ID
            
        Returns:
            CategorySchema instance or None if not found
        """
        category = self.repository.get_by_id(category_id)
        if category:
            return CategorySchema.model_validate(category)
        return None
    
    def initialize_default_categories(self) -> None:
        """
        Initialize default categories in the database.
        Only creates categories that don't already exist.
        
        This method is idempotent - it can be called multiple times
        without creating duplicate categories.
        """
        for category_data in self.DEFAULT_CATEGORIES:
            # Check if category already exists
            existing = self.repository.get_by_id(category_data["id"])
            if not existing:
                # Create new category
                new_category = Category(
                    id=category_data["id"],
                    name=category_data["name"],
                    type=category_data["type"],
                    note=category_data["note"],
                    is_active=True
                )
                self.repository.create(new_category)
