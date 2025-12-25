"""Expense service for business logic"""

from typing import List, Optional
from datetime import date, datetime
from sqlalchemy.orm import Session
import pytz

from app.repositories.expense import ExpenseRepository
from app.schemas.expense import Expense, ExpenseCreate
from app.models.expense import Expense as ExpenseModel


class ExpenseService:
    """Service for expense business logic"""
    
    def __init__(self, db: Session, timezone: str = "Asia/Tokyo"):
        """
        Initialize Expense service.
        
        Args:
            db: Database session
            timezone: Timezone for date processing (default: Asia/Tokyo)
        """
        self.repository = ExpenseRepository(db)
        self.timezone = pytz.timezone(timezone)
    
    def register_expense(self, expense_data: ExpenseCreate) -> Expense:
        """
        Register a new expense with timezone-aware processing.
        The month is automatically derived from the date.
        
        Args:
            expense_data: Expense creation data
            
        Returns:
            Created Expense schema
        """
        # Convert string date to date object
        if isinstance(expense_data.date, str):
            expense_date = datetime.strptime(expense_data.date, "%Y-%m-%d").date()
        else:
            expense_date = expense_data.date
        
        expense_model = self.repository.create_expense(
            date=expense_date,
            category=expense_data.category,
            amount=expense_data.amount,
            memo=expense_data.memo
        )
        return Expense.model_validate(expense_model)
    
    def get_expense_by_id(self, expense_id: int) -> Optional[Expense]:
        """
        Get an expense by ID.
        
        Args:
            expense_id: Expense ID
            
        Returns:
            Expense schema or None if not found
        """
        expense_model = self.repository.get_by_id(expense_id)
        if expense_model:
            return Expense.model_validate(expense_model)
        return None
    
    def get_expenses_by_month(self, month: str) -> List[Expense]:
        """
        Get all expenses for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of Expense schemas
        """
        expense_models = self.repository.get_by_month(month)
        return [Expense.model_validate(model) for model in expense_models]
    
    def get_expenses_by_category(self, category: str) -> List[Expense]:
        """
        Get all expenses for a specific category.
        
        Args:
            category: Expense category
            
        Returns:
            List of Expense schemas
        """
        expense_models = self.repository.get_by_category(category)
        return [Expense.model_validate(model) for model in expense_models]
    
    def get_expenses_by_month_and_category(
        self, month: str, category: str
    ) -> List[Expense]:
        """
        Get all expenses for a specific month and category.
        
        Args:
            month: Month in YYYY-MM format
            category: Expense category
            
        Returns:
            List of Expense schemas
        """
        expense_models = self.repository.get_by_month_and_category(month, category)
        return [Expense.model_validate(model) for model in expense_models]
    
    def delete_expense(self, expense_id: int) -> bool:
        """
        Delete an expense by ID.
        
        Args:
            expense_id: Expense ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete_by_id(expense_id)
