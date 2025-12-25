"""Expense repository for database operations"""

from typing import Optional, List
from sqlalchemy.orm import Session
from sqlalchemy import and_
from datetime import date

from app.models.expense import Expense
from app.repositories.base import BaseRepository


class ExpenseRepository(BaseRepository[Expense]):
    """Repository for Expense model with specific query methods"""
    
    def __init__(self, db: Session):
        """
        Initialize Expense repository.
        
        Args:
            db: Database session
        """
        super().__init__(Expense, db)
    
    def create_expense(
        self,
        date: date,
        category: str,
        amount: int,
        memo: Optional[str] = None
    ) -> Expense:
        """
        Create a new expense with automatic month derivation.
        
        Args:
            date: Expense date
            category: Expense category
            amount: Expense amount in yen
            memo: Optional memo
            
        Returns:
            Created Expense instance
        """
        # Automatically derive month from date (YYYY-MM format)
        month = date.strftime("%Y-%m")
        
        new_expense = Expense(
            date=date,
            month=month,
            category=category,
            amount=amount,
            memo=memo
        )
        return self.create(new_expense)
    
    def get_by_month(self, month: str) -> List[Expense]:
        """
        Get all expenses for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of Expense instances for the specified month
        """
        return self.db.query(Expense).filter(Expense.month == month).all()
    
    def get_by_category(self, category: str) -> List[Expense]:
        """
        Get all expenses for a specific category.
        
        Args:
            category: Expense category
            
        Returns:
            List of Expense instances for the specified category
        """
        return self.db.query(Expense).filter(Expense.category == category).all()
    
    def get_by_month_and_category(self, month: str, category: str) -> List[Expense]:
        """
        Get all expenses for a specific month and category.
        
        Args:
            month: Month in YYYY-MM format
            category: Expense category
            
        Returns:
            List of Expense instances for the specified month and category
        """
        return self.db.query(Expense).filter(
            and_(
                Expense.month == month,
                Expense.category == category
            )
        ).all()
    
    def delete_by_id(self, id: int) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            id: Expense ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.delete(id)
