"""Budget service for business logic"""

from typing import List, Optional
from sqlalchemy.orm import Session

from app.repositories.budget import BudgetRepository
from app.schemas.budget import Budget, BudgetCreate
from app.models.budget import Budget as BudgetModel


class BudgetService:
    """Service for budget business logic"""
    
    def __init__(self, db: Session):
        """
        Initialize Budget service.
        
        Args:
            db: Database session
        """
        self.repository = BudgetRepository(db)
    
    def register_or_update_budget(self, budget_data: BudgetCreate) -> Budget:
        """
        Register or update a budget (upsert operation).
        If a budget with the same month and category exists, update it.
        Otherwise, create a new budget.
        
        Args:
            budget_data: Budget creation data
            
        Returns:
            Created or updated Budget schema
        """
        budget_model = self.repository.upsert(
            month=budget_data.month,
            category=budget_data.category,
            amount=budget_data.amount
        )
        return Budget.model_validate(budget_model)
    
    def register_budget(self, budget_data: BudgetCreate) -> Budget:
        """
        Alias for register_or_update_budget for backward compatibility.
        
        Args:
            budget_data: Budget creation data
            
        Returns:
            Created or updated Budget schema
        """
        return self.register_or_update_budget(budget_data)
    
    def get_budget_by_id(self, budget_id: int) -> Optional[Budget]:
        """
        Get a budget by ID.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            Budget schema or None if not found
        """
        budget_model = self.repository.get_by_id(budget_id)
        if budget_model:
            return Budget.model_validate(budget_model)
        return None
    
    def get_budgets_by_month(self, month: str) -> List[Budget]:
        """
        Get all budgets for a specific month.
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            List of Budget schemas
        """
        budget_models = self.repository.get_by_month(month)
        return [Budget.model_validate(model) for model in budget_models]
    
    def delete_budget(self, budget_id: int) -> bool:
        """
        Delete a budget by ID.
        
        Args:
            budget_id: Budget ID
            
        Returns:
            True if deleted, False if not found
        """
        return self.repository.delete_by_id(budget_id)
