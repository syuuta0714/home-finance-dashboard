"""MonthlyBudget service for business logic"""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session

from app.repositories.monthly_budget import MonthlyBudgetRepository
from app.repositories.category import CategoryRepository
from app.schemas.category import MonthlyBudgetSchema, MonthlyBudgetCreateSchema, MonthlyBudgetDetailSchema
from app.models.monthly_budget import MonthlyBudget


class MonthlyBudgetService:
    """Service for monthly budget business logic"""
    
    # Default monthly budgets for each category
    DEFAULT_BUDGETS = {
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
        "special": 0,
    }
    
    def __init__(self, db: Session):
        """
        Initialize MonthlyBudget service.
        
        Args:
            db: Database session
        """
        self.repository = MonthlyBudgetRepository(db)
        self.category_repository = CategoryRepository(db)
        self.db = db
    
    def register_budget(self, budget_data: MonthlyBudgetCreateSchema) -> MonthlyBudgetSchema:
        """
        Register or update a monthly budget (upsert operation).
        If a budget with the same month and category exists, update it.
        Otherwise, create a new budget.
        
        Args:
            budget_data: Monthly budget creation data
            
        Returns:
            Created or updated MonthlyBudgetSchema
        """
        budget_model = self.repository.upsert(
            month=budget_data.month,
            category_id=budget_data.category_id,
            amount=budget_data.amount
        )
        return MonthlyBudgetSchema.model_validate(budget_model)
    
    def get_budgets_by_month(self, month: str) -> List[MonthlyBudgetDetailSchema]:
        """
        Get all monthly budgets for a specific month with category details.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of MonthlyBudgetDetailSchema instances
        """
        budget_models = self.repository.get_by_month(month)
        
        result = []
        for budget in budget_models:
            category = self.category_repository.get_by_id(budget.category_id)
            if category:
                detail = MonthlyBudgetDetailSchema(
                    id=budget.id,
                    category_id=budget.category_id,
                    category_name=category.name,
                    category_type=category.type,
                    amount=budget.amount
                )
                result.append(detail)
        
        return result
    
    def get_budgets_by_month_and_type(
        self, month: str, category_type: str
    ) -> List[MonthlyBudgetDetailSchema]:
        """
        Get all monthly budgets for a specific month and category type.
        
        Args:
            month: Month in YYYY-MM format
            category_type: Category type (fixed, variable, lifestyle, event)
            
        Returns:
            List of MonthlyBudgetDetailSchema instances
        """
        budget_models = self.repository.get_by_month_and_type(month, category_type)
        
        result = []
        for budget in budget_models:
            category = self.category_repository.get_by_id(budget.category_id)
            if category:
                detail = MonthlyBudgetDetailSchema(
                    id=budget.id,
                    category_id=budget.category_id,
                    category_name=category.name,
                    category_type=category.type,
                    amount=budget.amount
                )
                result.append(detail)
        
        return result
    
    def get_budget_total(self, month: str) -> int:
        """
        Get the total monthly budget amount for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            Total budget amount in yen (0 if no budgets exist)
        """
        return self.repository.get_total_by_month(month)
    
    def delete_budget(self, budget_id: int) -> bool:
        """
        Delete a monthly budget by ID.
        
        Args:
            budget_id: Monthly budget ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete(budget_id)
    
    def initialize_default_budgets(self, month: str) -> None:
        """
        Initialize default monthly budgets for a specific month.
        Only creates budgets for categories that don't already have a budget for that month.
        
        This method is idempotent - it can be called multiple times
        without creating duplicate budgets.
        
        Args:
            month: Month in YYYY-MM format (e.g., "2025-01")
        """
        for category_id, amount in self.DEFAULT_BUDGETS.items():
            # Check if budget already exists for this month and category
            existing = self.repository.get_by_month_and_category(month, category_id)
            if not existing:
                # Create new budget
                new_budget = MonthlyBudget(
                    month=month,
                    category_id=category_id,
                    amount=amount
                )
                self.repository.create(new_budget)
