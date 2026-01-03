"""MonthlyBudget repository for database operations"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_, func
from datetime import datetime

from app.models.monthly_budget import MonthlyBudget
from app.models.category import Category
from app.repositories.base import BaseRepository


class MonthlyBudgetRepository(BaseRepository[MonthlyBudget]):
    """Repository for MonthlyBudget model with specific query methods"""
    
    def __init__(self, db: Session):
        """
        Initialize MonthlyBudget repository.
        
        Args:
            db: Database session
        """
        super().__init__(MonthlyBudget, db)
    
    def get_by_month(self, month: str) -> List[MonthlyBudget]:
        """
        Get all monthly budgets for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of MonthlyBudget instances for the specified month
        """
        return self.db.query(MonthlyBudget).filter(MonthlyBudget.month == month).all()
    
    def get_by_month_and_category(self, month: str, category_id: str) -> Optional[MonthlyBudget]:
        """
        Get a monthly budget by month and category.
        
        Args:
            month: Month in YYYY-MM format
            category_id: Category ID
            
        Returns:
            MonthlyBudget instance or None if not found
        """
        return self.db.query(MonthlyBudget).filter(
            and_(
                MonthlyBudget.month == month,
                MonthlyBudget.category_id == category_id
            )
        ).first()
    
    def get_by_month_and_type(self, month: str, category_type: str) -> List[MonthlyBudget]:
        """
        Get all monthly budgets for a specific month and category type.
        
        Args:
            month: Month in YYYY-MM format
            category_type: Category type (fixed, variable, lifestyle, event)
            
        Returns:
            List of MonthlyBudget instances for the specified month and type
        """
        return self.db.query(MonthlyBudget).join(
            Category,
            MonthlyBudget.category_id == Category.id
        ).filter(
            and_(
                MonthlyBudget.month == month,
                Category.type == category_type
            )
        ).all()
    
    def get_total_by_month(self, month: str) -> int:
        """
        Get the total monthly budget amount for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            Total budget amount in yen (0 if no budgets exist)
        """
        result = self.db.query(func.sum(MonthlyBudget.amount)).filter(
            MonthlyBudget.month == month
        ).scalar()
        return result if result is not None else 0
    
    def upsert(self, month: str, category_id: str, amount: int) -> MonthlyBudget:
        """
        Create or update a monthly budget (upsert operation).
        If a budget with the same month and category exists, update it.
        Otherwise, create a new budget.
        
        Args:
            month: Month in YYYY-MM format
            category_id: Category ID
            amount: Budget amount in yen
            
        Returns:
            Created or updated MonthlyBudget instance
        """
        # Check if budget already exists
        existing = self.get_by_month_and_category(month, category_id)
        
        if existing:
            # Update existing budget
            existing.amount = amount
            existing.updated_at = datetime.now()
            return self.update(existing)
        else:
            # Create new budget
            new_budget = MonthlyBudget(
                month=month,
                category_id=category_id,
                amount=amount
            )
            return self.create(new_budget)
