"""Schema validation tests"""

import pytest
from datetime import date, datetime
from pydantic import ValidationError

from app.schemas.budget import Budget, BudgetCreate
from app.schemas.expense import Expense, ExpenseCreate
from app.schemas.summary import Summary


class TestBudgetSchemas:
    """Test Budget schemas"""
    
    def test_budget_create_valid(self):
        """Test creating valid BudgetCreate"""
        budget = BudgetCreate(
            month="2025-12",
            category="食費",
            amount=50000
        )
        assert budget.month == "2025-12"
        assert budget.category == "食費"
        assert budget.amount == 50000
    
    def test_budget_create_invalid_month_format(self):
        """Test BudgetCreate with invalid month format"""
        with pytest.raises(ValidationError):
            BudgetCreate(
                month="2025/12",  # Invalid format
                category="食費",
                amount=50000
            )
    
    def test_budget_create_invalid_month_range(self):
        """Test BudgetCreate with invalid month range"""
        with pytest.raises(ValidationError):
            BudgetCreate(
                month="2025-13",  # Invalid month
                category="食費",
                amount=50000
            )
    
    def test_budget_create_negative_amount(self):
        """Test BudgetCreate with negative amount"""
        with pytest.raises(ValidationError):
            BudgetCreate(
                month="2025-12",
                category="食費",
                amount=-1000
            )
    
    def test_budget_create_empty_category(self):
        """Test BudgetCreate with empty category"""
        with pytest.raises(ValidationError):
            BudgetCreate(
                month="2025-12",
                category="",
                amount=50000
            )


class TestExpenseSchemas:
    """Test Expense schemas"""
    
    def test_expense_create_valid(self):
        """Test creating valid ExpenseCreate"""
        expense = ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000,
            memo="スーパー"
        )
        assert expense.date == "2025-12-25"
        assert expense.category == "食費"
        assert expense.amount == 3000
        assert expense.memo == "スーパー"
    
    def test_expense_create_without_memo(self):
        """Test ExpenseCreate without memo"""
        expense = ExpenseCreate(
            date="2025-12-25",
            category="食費",
            amount=3000
        )
        assert expense.memo is None
    
    def test_expense_create_negative_amount(self):
        """Test ExpenseCreate with negative amount"""
        with pytest.raises(ValidationError):
            ExpenseCreate(
                date="2025-12-25",
                category="食費",
                amount=-1000
            )
    
    def test_expense_create_empty_category(self):
        """Test ExpenseCreate with empty category"""
        with pytest.raises(ValidationError):
            ExpenseCreate(
                date="2025-12-25",
                category="",
                amount=3000
            )
    
    def test_expense_date_conversion(self):
        """Test Expense schema converts date object to string"""
        # Simulate SQLAlchemy model data
        model_data = {
            "id": 1,
            "date": date(2025, 12, 25),
            "month": "2025-12",
            "category": "食費",
            "amount": 3000,
            "memo": "テスト",
            "created_at": datetime(2025, 12, 25, 10, 0, 0)
        }
        
        expense = Expense.model_validate(model_data)
        
        assert expense.date == "2025-12-25"
        assert isinstance(expense.date, str)


class TestSummarySchema:
    """Test Summary schema"""
    
    def test_summary_valid(self):
        """Test creating valid Summary"""
        summary = Summary(
            month="2025-12",
            total_budget=100000,
            total_spent=50000,
            remaining=50000,
            remaining_days=10,
            per_day_budget=5000.0,
            usage_rate=50.0,
            status="OK",
            status_message="予算内で順調です",
            status_color="green"
        )
        assert summary.month == "2025-12"
        assert summary.total_budget == 100000
        assert summary.usage_rate == 50.0
        assert summary.status == "OK"
    
    def test_summary_no_per_day_budget(self):
        """Test Summary with no per_day_budget (remaining_days = 0)"""
        summary = Summary(
            month="2025-12",
            total_budget=100000,
            total_spent=50000,
            remaining=50000,
            remaining_days=0,
            per_day_budget=None,
            usage_rate=50.0,
            status="OK",
            status_message="予算内で順調です",
            status_color="green"
        )
        assert summary.per_day_budget is None
    
    def test_summary_negative_remaining_days(self):
        """Test Summary with negative remaining_days"""
        with pytest.raises(ValidationError):
            Summary(
                month="2025-12",
                total_budget=100000,
                total_spent=50000,
                remaining=50000,
                remaining_days=-1,
                per_day_budget=5000.0,
                usage_rate=50.0,
                status="OK",
                status_message="予算内で順調です",
                status_color="green"
            )
