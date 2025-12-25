"""Budget repository for database operations"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import datetime

from app.models.budget import Budget
from app.repositories.base import BaseRepository


class BudgetRepository(BaseRepository[Budget]):
    """Repository for Budget model with specific query methods"""
    
    def __init__(self, db: Session):
        """
        Initialize Budget repository.
        
        Args:
            db: Database session
        """
        super().__init__(Budget, db)
    
    def upsert(self, month: str, category: str, amount: int) -> Budget:
        """
        Create or update a budget (upsert operation).
        If a budget with the same month and category exists, update it.
        Otherwise, create a new budget.
        
        Args:
            month: Month in YYYY-MM format
            category: Budget category
            amount: Budget amount in yen
            
        Returns:
            Created or updated Budget instance
        """
        # Check if budget already exists
        existing = self.get_by_month_and_category(month, category)
        
        if existing:
            # Update existing budget
            existing.amount = amount
            existing.updated_at = datetime.now()
            return self.update(existing)
        else:
            # Create new budget
            new_budget = Budget(
                month=month,
                category=category,
                amount=amount
            )
            return self.create(new_budget)
    
    def get_by_month_and_category(self, month: str, category: str) -> Optional[Budget]:
        """
        Get a budget by month and category.
        
        Args:
            month: Month in YYYY-MM format
            category: Budget category
            
        Returns:
            Budget instance or None if not found
        """
        return self.db.query(Budget).filter(
            and_(
                Budget.month == month,
                Budget.category == category
            )
        ).first()
    
    def get_by_month(self, month: str) -> List[Budget]:
        """
        Get all budgets for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of Budget instances for the specified month
        """
        return self.db.query(Budget).filter(Budget.month == month).all()
    
    def delete_by_id(self, id: int) -> bool:
        """
        Delete a budget by ID.
        
        Args:
            id: Budget ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.delete(id)
