"""Category repository for database operations"""

from typing import List
from sqlalchemy.orm import Session

from app.models.category import Category
from app.repositories.base import BaseRepository


class CategoryRepository(BaseRepository[Category]):
    """Repository for Category model with specific query methods"""
    
    def __init__(self, db: Session):
        """
        Initialize Category repository.
        
        Args:
            db: Database session
        """
        super().__init__(Category, db)
    
    def get_by_type(self, category_type: str) -> List[Category]:
        """
        Get all categories of a specific type.
        
        Args:
            category_type: Category type (fixed, variable, lifestyle, event)
            
        Returns:
            List of Category instances for the specified type
        """
        return self.db.query(Category).filter(Category.type == category_type).all()
    
    def get_all_active(self) -> List[Category]:
        """
        Get all active categories.
        
        Returns:
            List of active Category instances
        """
        return self.db.query(Category).filter(Category.is_active == True).all()
