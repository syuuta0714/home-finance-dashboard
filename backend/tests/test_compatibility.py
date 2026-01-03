"""Compatibility tests for Budget and MonthlyBudget models"""

import pytest
from datetime import date

from app.services.budget import BudgetService
from app.services.category import CategoryService
from app.services.monthly_budget import MonthlyBudgetService
from app.services.expense import ExpenseService
from app.services.summary import SummaryService
from app.schemas.budget import BudgetCreate
from app.schemas.category import MonthlyBudgetCreateSchema
from app.schemas.expense import ExpenseCreate
from app.utils.compatibility import BudgetCompatibilityManager


class TestBudgetMonthlyBudgetCompatibility:
    """Test compatibility between Budget and MonthlyBudget models"""
    
    def test_summary_with_legacy_budget(self, test_db):
        """Test that Summary service works with legacy Budget model"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Create budgets using legacy Budget model
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="日用品",
            amount=20000
        ))
        
        # Create expenses
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=30000
        ))
        
        # Calculate summary - should work with legacy Budget model
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.total_budget == 70000
        assert result.total_spent == 30000
        assert result.remaining == 40000
    
    def test_summary_with_monthly_budget(self, test_db):
        """Test that Summary service works with new MonthlyBudget model"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Create budgets using new MonthlyBudget model
        monthly_budget_service = MonthlyBudgetService(test_db)
        monthly_budget_service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=50000
        ))
        monthly_budget_service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="daily_goods",
            amount=20000
        ))
        
        # Create expenses
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=30000
        ))
        
        # Calculate summary - should work with new MonthlyBudget model
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.total_budget == 70000
        assert result.total_spent == 30000
        assert result.remaining == 40000
    
    def test_summary_prioritizes_monthly_budget(self, test_db):
        """Test that Summary service prioritizes MonthlyBudget over Budget"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Create budgets using legacy Budget model
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        
        # Create budgets using new MonthlyBudget model
        monthly_budget_service = MonthlyBudgetService(test_db)
        monthly_budget_service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=60000
        ))
        
        # Calculate summary - should use MonthlyBudget (60000) not Budget (50000)
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.total_budget == 60000
    
    def test_compatibility_manager_sync_budget_to_monthly_budget(self, test_db):
        """Test syncing Budget to MonthlyBudget"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Create a budget using legacy Budget model
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        
        # Sync to MonthlyBudget
        compatibility_manager = BudgetCompatibilityManager(test_db)
        stats = compatibility_manager.sync_all_budgets_to_monthly_budgets()
        
        assert stats['total'] == 1
        assert stats['synced'] == 1
        assert stats['skipped'] == 0
        
        # Verify MonthlyBudget was created
        monthly_budget_service = MonthlyBudgetService(test_db)
        budgets = monthly_budget_service.get_budgets_by_month("2025-12")
        
        assert len(budgets) == 1
        assert budgets[0].amount == 50000
    
    def test_compatibility_manager_verify_compatibility(self, test_db):
        """Test compatibility verification"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Create budgets using both models
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        
        monthly_budget_service = MonthlyBudgetService(test_db)
        monthly_budget_service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="daily_goods",
            amount=20000
        ))
        
        # Verify compatibility
        compatibility_manager = BudgetCompatibilityManager(test_db)
        result = compatibility_manager.verify_compatibility()
        
        assert result['budget_records'] == 1
        assert result['monthly_budget_records'] == 1
        assert result['categories'] == 14  # Default categories
        assert result['is_compatible'] == True
        assert len(result['budget_without_category']) == 0
        assert len(result['monthly_budget_without_category']) == 0
    
    def test_default_budgets_initialization(self, test_db):
        """Test that default budgets are initialized correctly"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Initialize default budgets
        monthly_budget_service = MonthlyBudgetService(test_db)
        monthly_budget_service.initialize_default_budgets("2025-12")
        
        # Verify all default budgets were created
        budgets = monthly_budget_service.get_budgets_by_month("2025-12")
        
        assert len(budgets) == 14
        
        # Verify total budget
        total = monthly_budget_service.get_budget_total("2025-12")
        assert total == 325856  # Sum of all default budgets
    
    def test_summary_with_default_budgets(self, test_db):
        """Test Summary service with default budgets"""
        # Initialize categories
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        # Initialize default budgets
        monthly_budget_service = MonthlyBudgetService(test_db)
        monthly_budget_service.initialize_default_budgets("2025-12")
        
        # Create some expenses
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=30000
        ))
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-26",
            category="日用品",
            amount=10000
        ))
        
        # Calculate summary
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.total_budget == 325856
        assert result.total_spent == 40000
        assert result.remaining == 285856
        assert result.usage_rate == pytest.approx(12.27, rel=0.01)
        assert result.status == "OK"
