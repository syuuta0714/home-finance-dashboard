"""Compatibility utilities for Budget and MonthlyBudget models"""

from typing import Optional, Dict, List
from sqlalchemy.orm import Session

from app.models.budget import Budget
from app.models.monthly_budget import MonthlyBudget
from app.models.category import Category
from app.repositories.budget import BudgetRepository
from app.repositories.monthly_budget import MonthlyBudgetRepository
from app.repositories.category import CategoryRepository


class BudgetCompatibilityManager:
    """
    Manages compatibility between the legacy Budget model and the new MonthlyBudget model.
    
    This class ensures that:
    1. Existing Budget data continues to work
    2. New MonthlyBudget data works with the category system
    3. Both systems can be synchronized
    """
    
    def __init__(self, db: Session):
        """
        Initialize the compatibility manager.
        
        Args:
            db: Database session
        """
        self.db = db
        self.budget_repo = BudgetRepository(db)
        self.monthly_budget_repo = MonthlyBudgetRepository(db)
        self.category_repo = CategoryRepository(db)
    
    def sync_budget_to_monthly_budget(self, budget: Budget) -> Optional[MonthlyBudget]:
        """
        Synchronize a legacy Budget record to the new MonthlyBudget system.
        
        This creates or updates a MonthlyBudget record based on a Budget record.
        The category string from Budget is mapped to a category_id in MonthlyBudget.
        
        Args:
            budget: Legacy Budget model instance
            
        Returns:
            Created or updated MonthlyBudget instance, or None if category not found
        """
        # Try to find a matching category by name or ID
        category = self._find_category_by_name_or_id(budget.category)
        
        if not category:
            # If no category found, skip this budget
            return None
        
        # Create or update MonthlyBudget
        monthly_budget = self.monthly_budget_repo.upsert(
            month=budget.month,
            category_id=category.id,
            amount=budget.amount
        )
        
        return monthly_budget
    
    def sync_monthly_budget_to_budget(self, monthly_budget: MonthlyBudget) -> Optional[Budget]:
        """
        Synchronize a new MonthlyBudget record to the legacy Budget system.
        
        This creates or updates a Budget record based on a MonthlyBudget record.
        The category_id from MonthlyBudget is mapped to a category string in Budget.
        
        Args:
            monthly_budget: New MonthlyBudget model instance
            
        Returns:
            Created or updated Budget instance, or None if category not found
        """
        # Get the category details
        category = self.category_repo.get_by_id(monthly_budget.category_id)
        
        if not category:
            # If category not found, skip this budget
            return None
        
        # Create or update Budget using the category name
        budget = self.budget_repo.upsert(
            month=monthly_budget.month,
            category=category.name,  # Use category name for backward compatibility
            amount=monthly_budget.amount
        )
        
        return budget
    
    def sync_all_budgets_to_monthly_budgets(self) -> Dict[str, int]:
        """
        Synchronize all legacy Budget records to the new MonthlyBudget system.
        
        This is useful for migration purposes.
        
        Returns:
            Dictionary with sync statistics:
            - 'total': Total budgets processed
            - 'synced': Successfully synced budgets
            - 'skipped': Budgets skipped (category not found)
        """
        all_budgets = self.budget_repo.get_all()
        
        stats = {
            'total': len(all_budgets),
            'synced': 0,
            'skipped': 0
        }
        
        for budget in all_budgets:
            result = self.sync_budget_to_monthly_budget(budget)
            if result:
                stats['synced'] += 1
            else:
                stats['skipped'] += 1
        
        return stats
    
    def sync_all_monthly_budgets_to_budgets(self) -> Dict[str, int]:
        """
        Synchronize all new MonthlyBudget records to the legacy Budget system.
        
        This is useful for backward compatibility.
        
        Returns:
            Dictionary with sync statistics:
            - 'total': Total monthly budgets processed
            - 'synced': Successfully synced budgets
            - 'skipped': Budgets skipped (category not found)
        """
        all_monthly_budgets = self.monthly_budget_repo.get_all()
        
        stats = {
            'total': len(all_monthly_budgets),
            'synced': 0,
            'skipped': 0
        }
        
        for monthly_budget in all_monthly_budgets:
            result = self.sync_monthly_budget_to_budget(monthly_budget)
            if result:
                stats['synced'] += 1
            else:
                stats['skipped'] += 1
        
        return stats
    
    def _find_category_by_name_or_id(self, category_identifier: str) -> Optional[Category]:
        """
        Find a category by name or ID.
        
        This method tries to match a category string (from legacy Budget)
        to a Category record by checking both ID and name.
        
        Args:
            category_identifier: Category name or ID
            
        Returns:
            Category instance or None if not found
        """
        # First, try to find by ID (exact match)
        category = self.category_repo.get_by_id(category_identifier)
        if category:
            return category
        
        # If not found by ID, try to find by name
        # This requires a query method that searches by name
        all_categories = self.category_repo.get_all()
        for cat in all_categories:
            if cat.name == category_identifier:
                return cat
        
        return None
    
    def verify_compatibility(self) -> Dict[str, any]:
        """
        Verify compatibility between Budget and MonthlyBudget systems.
        
        This method checks:
        1. All Budget records have corresponding categories
        2. All MonthlyBudget records have valid categories
        3. Data consistency between systems
        
        Returns:
            Dictionary with verification results:
            - 'budget_records': Total Budget records
            - 'monthly_budget_records': Total MonthlyBudget records
            - 'categories': Total categories
            - 'budget_without_category': List of Budget records without matching category
            - 'monthly_budget_without_category': List of MonthlyBudget records without valid category
            - 'is_compatible': Boolean indicating overall compatibility
        """
        all_budgets = self.budget_repo.get_all()
        all_monthly_budgets = self.monthly_budget_repo.get_all()
        all_categories = self.category_repo.get_all()
        
        budget_without_category = []
        monthly_budget_without_category = []
        
        # Check Budget records
        for budget in all_budgets:
            if not self._find_category_by_name_or_id(budget.category):
                budget_without_category.append({
                    'id': budget.id,
                    'month': budget.month,
                    'category': budget.category,
                    'amount': budget.amount
                })
        
        # Check MonthlyBudget records
        for monthly_budget in all_monthly_budgets:
            if not self.category_repo.get_by_id(monthly_budget.category_id):
                monthly_budget_without_category.append({
                    'id': monthly_budget.id,
                    'month': monthly_budget.month,
                    'category_id': monthly_budget.category_id,
                    'amount': monthly_budget.amount
                })
        
        is_compatible = len(budget_without_category) == 0 and len(monthly_budget_without_category) == 0
        
        return {
            'budget_records': len(all_budgets),
            'monthly_budget_records': len(all_monthly_budgets),
            'categories': len(all_categories),
            'budget_without_category': budget_without_category,
            'monthly_budget_without_category': monthly_budget_without_category,
            'is_compatible': is_compatible
        }
