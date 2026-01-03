"""Service layer tests"""

import pytest
from datetime import date, datetime

from app.services.budget import BudgetService
from app.services.expense import ExpenseService
from app.services.summary import SummaryService
from app.services.category import CategoryService
from app.services.monthly_budget import MonthlyBudgetService
from app.schemas.budget import BudgetCreate
from app.schemas.expense import ExpenseCreate
from app.schemas.category import MonthlyBudgetCreateSchema


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



class TestCategoryService:
    """Test CategoryService"""
    
    def test_get_all_categories(self, test_db):
        """Test getting all categories"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        categories = service.get_all_categories()
        
        assert len(categories) == 14
        assert all(hasattr(cat, 'id') for cat in categories)
        assert all(hasattr(cat, 'name') for cat in categories)
        assert all(hasattr(cat, 'type') for cat in categories)
    
    def test_get_categories_by_type(self, test_db):
        """Test getting categories filtered by type"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        fixed_categories = service.get_categories_by_type("fixed")
        
        assert len(fixed_categories) == 5  # housing, utilities, communication, insurance, taxes
        assert all(cat.type == "fixed" for cat in fixed_categories)
    
    def test_get_categories_by_type_variable(self, test_db):
        """Test getting variable type categories"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        variable_categories = service.get_categories_by_type("variable")
        
        assert len(variable_categories) == 4  # food, daily_goods, transportation, medical
        assert all(cat.type == "variable" for cat in variable_categories)
    
    def test_get_categories_by_type_lifestyle(self, test_db):
        """Test getting lifestyle type categories"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        lifestyle_categories = service.get_categories_by_type("lifestyle")
        
        assert len(lifestyle_categories) == 3  # entertainment, social, clothing
        assert all(cat.type == "lifestyle" for cat in lifestyle_categories)
    
    def test_get_categories_by_type_event(self, test_db):
        """Test getting event type categories"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        event_categories = service.get_categories_by_type("event")
        
        assert len(event_categories) == 2  # education, special
        assert all(cat.type == "event" for cat in event_categories)
    
    def test_get_category_by_id(self, test_db):
        """Test getting a specific category by ID"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        category = service.get_category_by_id("housing")
        
        assert category is not None
        assert category.id == "housing"
        assert category.name == "住居"
        assert category.type == "fixed"
    
    def test_get_category_by_id_not_found(self, test_db):
        """Test getting non-existent category"""
        service = CategoryService(test_db)
        service.initialize_default_categories()
        
        category = service.get_category_by_id("nonexistent")
        
        assert category is None
    
    def test_initialize_default_categories(self, test_db):
        """Test initializing default categories"""
        service = CategoryService(test_db)
        
        service.initialize_default_categories()
        categories = service.get_all_categories()
        
        assert len(categories) == 14
        category_ids = [cat.id for cat in categories]
        assert "housing" in category_ids
        assert "food" in category_ids
        assert "special" in category_ids
    
    def test_initialize_default_categories_idempotent(self, test_db):
        """Test that initializing default categories is idempotent"""
        service = CategoryService(test_db)
        
        # Initialize twice
        service.initialize_default_categories()
        service.initialize_default_categories()
        
        categories = service.get_all_categories()
        
        # Should still have exactly 14 categories, not 28
        assert len(categories) == 14


class TestMonthlyBudgetService:
    """Test MonthlyBudgetService"""
    
    def test_register_budget(self, test_db):
        """Test registering a new monthly budget"""
        # Initialize categories first
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        budget_data = MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=90000
        )
        
        result = service.register_budget(budget_data)
        
        assert result.month == "2025-12"
        assert result.category_id == "food"
        assert result.amount == 90000
        assert result.id is not None
    
    def test_register_budget_upsert(self, test_db):
        """Test that registering budget with same month and category updates it"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Register initial budget
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=90000
        ))
        
        # Register same month and category with different amount
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=95000
        ))
        
        # Get budgets and verify only one exists with updated amount
        budgets = service.get_budgets_by_month("2025-12")
        food_budgets = [b for b in budgets if b.category_id == "food"]
        
        assert len(food_budgets) == 1
        assert food_budgets[0].amount == 95000
    
    def test_get_budgets_by_month(self, test_db):
        """Test getting budgets for a specific month"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Create budgets for December
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=90000
        ))
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="daily_goods",
            amount=20000
        ))
        
        # Create budget for November
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-11",
            category_id="food",
            amount=85000
        ))
        
        # Get December budgets
        results = service.get_budgets_by_month("2025-12")
        
        assert len(results) == 2
        assert all(b.category_id in ["food", "daily_goods"] for b in results)
    
    def test_get_budgets_by_month_and_type(self, test_db):
        """Test getting budgets filtered by month and category type"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Create budgets of different types
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="housing",  # fixed
            amount=50656
        ))
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",  # variable
            amount=90000
        ))
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="entertainment",  # lifestyle
            amount=24000
        ))
        
        # Get fixed type budgets
        results = service.get_budgets_by_month_and_type("2025-12", "fixed")
        
        assert len(results) == 1
        assert results[0].category_id == "housing"
        assert results[0].category_type == "fixed"
    
    def test_get_budget_total(self, test_db):
        """Test getting total budget for a month"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Create budgets
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="housing",
            amount=50656
        ))
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=90000
        ))
        service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="daily_goods",
            amount=20000
        ))
        
        total = service.get_budget_total("2025-12")
        
        assert total == 160656
    
    def test_get_budget_total_no_budgets(self, test_db):
        """Test getting total budget when no budgets exist"""
        service = MonthlyBudgetService(test_db)
        
        total = service.get_budget_total("2025-12")
        
        assert total == 0
    
    def test_delete_budget(self, test_db):
        """Test deleting a monthly budget"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Create a budget
        budget = service.register_budget(MonthlyBudgetCreateSchema(
            month="2025-12",
            category_id="food",
            amount=90000
        ))
        
        # Delete it
        deleted = service.delete_budget(budget.id)
        
        assert deleted is True
        
        # Verify it's deleted
        budgets = service.get_budgets_by_month("2025-12")
        assert len(budgets) == 0
    
    def test_delete_budget_not_found(self, test_db):
        """Test deleting non-existent budget"""
        service = MonthlyBudgetService(test_db)
        
        deleted = service.delete_budget(999)
        
        assert deleted is False
    
    def test_initialize_default_budgets(self, test_db):
        """Test initializing default budgets for a month"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        service.initialize_default_budgets("2025-12")
        
        budgets = service.get_budgets_by_month("2025-12")
        
        assert len(budgets) == 14
        
        # Verify specific amounts
        budget_dict = {b.category_id: b.amount for b in budgets}
        assert budget_dict["housing"] == 50656
        assert budget_dict["food"] == 90000
        assert budget_dict["special"] == 0
    
    def test_initialize_default_budgets_idempotent(self, test_db):
        """Test that initializing default budgets is idempotent"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        
        # Initialize twice
        service.initialize_default_budgets("2025-12")
        service.initialize_default_budgets("2025-12")
        
        budgets = service.get_budgets_by_month("2025-12")
        
        # Should still have exactly 14 budgets, not 28
        assert len(budgets) == 14
    
    def test_initialize_default_budgets_total(self, test_db):
        """Test that default budgets total is correct"""
        category_service = CategoryService(test_db)
        category_service.initialize_default_categories()
        
        service = MonthlyBudgetService(test_db)
        service.initialize_default_budgets("2025-12")
        
        total = service.get_budget_total("2025-12")
        
        # Total should be 325,856 yen
        assert total == 325856
