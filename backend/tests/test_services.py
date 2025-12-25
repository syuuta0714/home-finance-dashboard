"""Service layer tests"""

import pytest
from datetime import date, datetime

from app.services.budget import BudgetService
from app.services.expense import ExpenseService
from app.services.summary import SummaryService
from app.schemas.budget import BudgetCreate
from app.schemas.expense import ExpenseCreate


class TestBudgetService:
    """Test BudgetService"""
    
    def test_register_budget(self, test_db):
        """Test registering a new budget"""
        service = BudgetService(test_db)
        budget_data = BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        )
        
        result = service.register_budget(budget_data)
        
        assert result.month == "2025-12"
        assert result.category == "食費"
        assert result.amount == 50000
        assert result.id is not None
    
    def test_get_budgets_by_month(self, test_db):
        """Test getting budgets by month"""
        service = BudgetService(test_db)
        
        # Create test budgets
        service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        service.register_budget(BudgetCreate(
            month="2025-12",
            category="日用品",
            amount=20000
        ))
        service.register_budget(BudgetCreate(
            month="2025-11",
            category="食費",
            amount=45000
        ))
        
        # Get December budgets
        results = service.get_budgets_by_month("2025-12")
        
        assert len(results) == 2
        assert all(b.month == "2025-12" for b in results)
    
    def test_upsert_budget(self, test_db):
        """Test upserting (update or insert) budget"""
        service = BudgetService(test_db)
        
        # Initial insert
        service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        ))
        
        # Update with same month and category
        service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=55000
        ))
        
        # Verify only one budget exists with updated amount
        budgets = service.get_budgets_by_month("2025-12")
        food_budgets = [b for b in budgets if b.category == "食費"]
        
        assert len(food_budgets) == 1
        assert food_budgets[0].amount == 55000


class TestExpenseService:
    """Test ExpenseService"""
    
    def test_register_expense(self, test_db):
        """Test registering a new expense"""
        service = ExpenseService(test_db)
        expense_data = ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000,
            memo="スーパー"
        )
        
        result = service.register_expense(expense_data)
        
        assert result.date == "2025-12-25"
        assert result.month == "2025-12"
        assert result.category == "食費"
        assert result.amount == 3000
        assert result.memo == "スーパー"
        assert result.id is not None
    
    def test_register_expense_without_memo(self, test_db):
        """Test registering expense without memo"""
        service = ExpenseService(test_db)
        expense_data = ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000
        )
        
        result = service.register_expense(expense_data)
        
        assert result.memo is None
    
    def test_get_expenses_by_month(self, test_db):
        """Test getting expenses by month"""
        service = ExpenseService(test_db)
        
        # Create test expenses
        service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000
        ))
        service.register_expense(ExpenseCreate(
            date="2025-12-26",
            category="日用品",
            amount=1500
        ))
        service.register_expense(ExpenseCreate(
            date="2025-11-30",
            category="食費",
            amount=2000
        ))
        
        # Get December expenses
        results = service.get_expenses_by_month("2025-12")
        
        assert len(results) == 2
        assert all(e.month == "2025-12" for e in results)
    
    def test_get_expenses_by_category(self, test_db):
        """Test getting expenses by category"""
        service = ExpenseService(test_db)
        
        # Create test expenses
        service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000
        ))
        service.register_expense(ExpenseCreate(
            date="2025-12-26",
            category="日用品",
            amount=1500
        ))
        
        # Get food expenses
        results = service.get_expenses_by_category("食費")
        
        assert len(results) == 1
        assert results[0].category == "食費"
    
    def test_get_expenses_by_month_and_category(self, test_db):
        """Test getting expenses by month and category"""
        service = ExpenseService(test_db)
        
        # Create test expenses
        service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000
        ))
        service.register_expense(ExpenseCreate(
            date="2025-12-26",
            category="食費",
            amount=2000
        ))
        service.register_expense(ExpenseCreate(
            date="2025-11-30",
            category="食費",
            amount=2500
        ))
        
        # Get December food expenses
        results = service.get_expenses_by_month_and_category("2025-12", "食費")
        
        assert len(results) == 2
        assert all(e.month == "2025-12" and e.category == "食費" for e in results)


class TestSummaryService:
    """Test SummaryService"""
    
    def test_calculate_summary_no_data(self, test_db):
        """Test calculating summary with no data"""
        service = SummaryService(test_db)
        
        result = service.calculate_summary("2025-12")
        
        assert result.month == "2025-12"
        assert result.total_budget == 0
        assert result.total_spent == 0
        assert result.remaining == 0
        assert result.usage_rate == 0.0
        assert result.status == "OK"
    
    def test_calculate_summary_with_data(self, test_db):
        """Test calculating summary with budgets and expenses"""
        # Create budgets
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
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-26",
            category="日用品",
            amount=10000
        ))
        
        # Calculate summary
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.month == "2025-12"
        assert result.total_budget == 70000
        assert result.total_spent == 40000
        assert result.remaining == 30000
        assert result.usage_rate == pytest.approx(57.14, rel=0.01)
        assert result.status == "OK"
        assert result.status_color == "green"
    
    def test_status_ok(self, test_db):
        """Test OK status (usage < 70%)"""
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=100000
        ))
        
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=60000
        ))
        
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.status == "OK"
        assert result.status_color == "green"
    
    def test_status_warn(self, test_db):
        """Test WARN status (70% <= usage < 90%)"""
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=100000
        ))
        
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=75000
        ))
        
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.status == "WARN"
        assert result.status_color == "yellow"
    
    def test_status_danger(self, test_db):
        """Test DANGER status (usage >= 90%)"""
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=100000
        ))
        
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=95000
        ))
        
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        assert result.status == "DANGER"
        assert result.status_color == "red"
    
    def test_per_day_budget_calculation(self, test_db):
        """Test per day budget calculation"""
        budget_service = BudgetService(test_db)
        budget_service.register_budget(BudgetCreate(
            month="2025-12",
            category="食費",
            amount=100000
        ))
        
        expense_service = ExpenseService(test_db)
        expense_service.register_expense(ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=50000
        ))
        
        summary_service = SummaryService(test_db)
        result = summary_service.calculate_summary("2025-12")
        
        # Remaining: 50000, Remaining days depends on current date
        assert result.per_day_budget is not None
        assert result.per_day_budget > 0
