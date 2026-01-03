"""API endpoint tests"""

import pytest
from datetime import date


class TestHealthEndpoint:
    """Test health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check returns ok status"""
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json() == {"status": "ok"}


class TestBudgetEndpoints:
    """Test budget API endpoints"""
    
    def test_create_budget(self, client):
        """Test creating a new budget"""
        budget_data = {
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        }
        response = client.post("/api/budgets", json=budget_data)
        assert response.status_code == 201
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["category"] == "食費"
        assert data["amount"] == 50000
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data
    
    def test_create_budget_invalid_month(self, client):
        """Test creating budget with invalid month format"""
        budget_data = {
            "month": "2025/12",  # Invalid format
            "category": "食費",
            "amount": 50000
        }
        response = client.post("/api/budgets", json=budget_data)
        assert response.status_code == 422
    
    def test_create_budget_negative_amount(self, client):
        """Test creating budget with negative amount"""
        budget_data = {
            "month": "2025-12",
            "category": "食費",
            "amount": -1000
        }
        response = client.post("/api/budgets", json=budget_data)
        assert response.status_code == 422
    
    def test_get_budgets_by_month(self, client):
        """Test getting budgets filtered by month"""
        # Create test budgets
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        })
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "日用品",
            "amount": 20000
        })
        client.post("/api/budgets", json={
            "month": "2025-11",
            "category": "食費",
            "amount": 45000
        })
        
        # Get budgets for December
        response = client.get("/api/budgets?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(b["month"] == "2025-12" for b in data)
    
    def test_get_budget_by_id(self, client):
        """Test getting a specific budget by ID"""
        # Create a budget
        create_response = client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        })
        budget_id = create_response.json()["id"]
        
        # Get the budget
        response = client.get(f"/api/budgets/{budget_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget_id
        assert data["category"] == "食費"
    
    def test_get_budget_not_found(self, client):
        """Test getting non-existent budget"""
        response = client.get("/api/budgets/999")
        assert response.status_code == 404
    
    def test_update_budget(self, client):
        """Test updating an existing budget (upsert)"""
        # Create initial budget
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        })
        
        # Update with same month and category
        response = client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 55000
        })
        assert response.status_code == 201
        
        # Verify only one budget exists
        get_response = client.get("/api/budgets?month=2025-12")
        budgets = get_response.json()
        food_budgets = [b for b in budgets if b["category"] == "食費"]
        assert len(food_budgets) == 1
        assert food_budgets[0]["amount"] == 55000
    
    def test_delete_budget(self, client):
        """Test deleting a budget"""
        # Create a budget
        create_response = client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        })
        budget_id = create_response.json()["id"]
        
        # Delete the budget
        response = client.delete(f"/api/budgets/{budget_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/budgets/{budget_id}")
        assert get_response.status_code == 404


class TestExpenseEndpoints:
    """Test expense API endpoints"""
    
    def test_create_expense(self, client):
        """Test creating a new expense"""
        expense_data = {
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000,
            "memo": "スーパー"
        }
        response = client.post("/api/expenses", json=expense_data)
        assert response.status_code == 201
        data = response.json()
        assert data["date"] == "2025-12-25"
        assert data["month"] == "2025-12"
        assert data["category"] == "食費"
        assert data["amount"] == 3000
        assert data["memo"] == "スーパー"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_expense_without_memo(self, client):
        """Test creating expense without memo"""
        expense_data = {
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        }
        response = client.post("/api/expenses", json=expense_data)
        assert response.status_code == 201
        data = response.json()
        assert data["memo"] is None
    
    def test_create_expense_negative_amount(self, client):
        """Test creating expense with negative amount"""
        expense_data = {
            "date": "2025-12-25",
            "category": "食費",
            "amount": -1000
        }
        response = client.post("/api/expenses", json=expense_data)
        assert response.status_code == 422
    
    def test_get_expenses_by_month(self, client):
        """Test getting expenses filtered by month"""
        # Create test expenses
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        })
        client.post("/api/expenses", json={
            "date": "2025-12-26",
            "category": "日用品",
            "amount": 1500
        })
        client.post("/api/expenses", json={
            "date": "2025-11-30",
            "category": "食費",
            "amount": 2000
        })
        
        # Get expenses for December
        response = client.get("/api/expenses?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(e["month"] == "2025-12" for e in data)
    
    def test_get_expenses_by_category(self, client):
        """Test getting expenses filtered by category"""
        # Create test expenses
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        })
        client.post("/api/expenses", json={
            "date": "2025-12-26",
            "category": "日用品",
            "amount": 1500
        })
        
        # Get food expenses
        response = client.get("/api/expenses?category=食費")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category"] == "食費"
    
    def test_get_expenses_by_month_and_category(self, client):
        """Test getting expenses filtered by both month and category"""
        # Create test expenses
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        })
        client.post("/api/expenses", json={
            "date": "2025-12-26",
            "category": "食費",
            "amount": 2000
        })
        client.post("/api/expenses", json={
            "date": "2025-11-30",
            "category": "食費",
            "amount": 2500
        })
        
        # Get December food expenses
        response = client.get("/api/expenses?month=2025-12&category=食費")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(e["month"] == "2025-12" and e["category"] == "食費" for e in data)
    
    def test_get_expense_by_id(self, client):
        """Test getting a specific expense by ID"""
        # Create an expense
        create_response = client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        })
        expense_id = create_response.json()["id"]
        
        # Get the expense
        response = client.get(f"/api/expenses/{expense_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == expense_id
    
    def test_get_expense_not_found(self, client):
        """Test getting non-existent expense"""
        response = client.get("/api/expenses/999")
        assert response.status_code == 404
    
    def test_delete_expense(self, client):
        """Test deleting an expense"""
        # Create an expense
        create_response = client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 3000
        })
        expense_id = create_response.json()["id"]
        
        # Delete the expense
        response = client.delete(f"/api/expenses/{expense_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/expenses/{expense_id}")
        assert get_response.status_code == 404


class TestSummaryEndpoint:
    """Test summary API endpoint"""
    
    def test_get_summary_no_data(self, client):
        """Test getting summary with no budgets or expenses"""
        response = client.get("/api/summary?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["total_budget"] == 0
        assert data["total_spent"] == 0
        assert data["remaining"] == 0
        assert data["usage_rate"] == 0.0
        assert data["status"] == "OK"
    
    def test_get_summary_with_data(self, client):
        """Test getting summary with budgets and expenses"""
        # Create budgets
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 50000
        })
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "日用品",
            "amount": 20000
        })
        
        # Create expenses
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 30000
        })
        client.post("/api/expenses", json={
            "date": "2025-12-26",
            "category": "日用品",
            "amount": 10000
        })
        
        # Get summary
        response = client.get("/api/summary?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["total_budget"] == 70000
        assert data["total_spent"] == 40000
        assert data["remaining"] == 30000
        assert data["usage_rate"] == pytest.approx(57.14, rel=0.01)
        assert data["status"] == "OK"
        assert data["status_color"] == "green"
    
    def test_get_summary_warn_status(self, client):
        """Test summary with WARN status (70-90% usage)"""
        # Create budget
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 100000
        })
        
        # Create expense (75% usage)
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 75000
        })
        
        # Get summary
        response = client.get("/api/summary?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["usage_rate"] == 75.0
        assert data["status"] == "WARN"
        assert data["status_color"] == "yellow"
    
    def test_get_summary_danger_status(self, client):
        """Test summary with DANGER status (>=90% usage)"""
        # Create budget
        client.post("/api/budgets", json={
            "month": "2025-12",
            "category": "食費",
            "amount": 100000
        })
        
        # Create expense (95% usage)
        client.post("/api/expenses", json={
            "date": "2025-12-25",
            "category": "食費",
            "amount": 95000
        })
        
        # Get summary
        response = client.get("/api/summary?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["usage_rate"] == 95.0
        assert data["status"] == "DANGER"
        assert data["status_color"] == "red"
    
    def test_get_summary_current_month(self, client):
        """Test getting summary for current month (no month parameter)"""
        response = client.get("/api/summary")
        assert response.status_code == 200
        data = response.json()
        assert "month" in data
        assert "total_budget" in data
        assert "total_spent" in data



class TestCategoryEndpoints:
    """Test category API endpoints"""
    
    def test_get_categories(self, client):
        """Test getting all categories"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 14
        assert all("id" in cat for cat in data)
        assert all("name" in cat for cat in data)
        assert all("type" in cat for cat in data)
    
    def test_get_categories_by_type(self, client):
        """Test getting categories filtered by type"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        response = client.get("/api/categories?type=fixed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 5
        assert all(cat["type"] == "fixed" for cat in data)
    
    def test_get_category_by_id(self, client):
        """Test getting a specific category by ID"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        response = client.get("/api/categories/housing")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == "housing"
        assert data["name"] == "住居"
        assert data["type"] == "fixed"
    
    def test_get_category_not_found(self, client):
        """Test getting non-existent category"""
        response = client.get("/api/categories/nonexistent")
        assert response.status_code == 404


class TestMonthlyBudgetEndpoints:
    """Test monthly budget API endpoints"""
    
    def test_create_monthly_budget(self, client):
        """Test creating a new monthly budget"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        budget_data = {
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        }
        response = client.post("/api/monthly-budgets", json=budget_data)
        assert response.status_code == 201
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["category_id"] == "food"
        assert data["amount"] == 90000
        assert "id" in data
    
    def test_create_monthly_budget_upsert(self, client):
        """Test that creating budget with same month and category updates it"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create initial budget
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        
        # Update with same month and category
        response = client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 95000
        })
        assert response.status_code == 201
        
        # Verify only one budget exists
        get_response = client.get("/api/monthly-budgets?month=2025-12")
        budgets = get_response.json()
        food_budgets = [b for b in budgets if b["category_id"] == "food"]
        assert len(food_budgets) == 1
        assert food_budgets[0]["amount"] == 95000
    
    def test_get_monthly_budgets_by_month(self, client):
        """Test getting monthly budgets for a specific month"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create budgets
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "daily_goods",
            "amount": 20000
        })
        client.post("/api/monthly-budgets", json={
            "month": "2025-11",
            "category_id": "food",
            "amount": 85000
        })
        
        # Get December budgets
        response = client.get("/api/monthly-budgets?month=2025-12")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert all(b["category_id"] in ["food", "daily_goods"] for b in data)
    
    def test_get_monthly_budgets_by_month_and_type(self, client):
        """Test getting monthly budgets filtered by month and category type"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create budgets of different types
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "housing",
            "amount": 50656
        })
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        
        # Get fixed type budgets
        response = client.get("/api/monthly-budgets?month=2025-12&category_type=fixed")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["category_id"] == "housing"
        assert data[0]["category_type"] == "fixed"
    
    def test_get_monthly_budget_by_id(self, client):
        """Test getting a specific monthly budget by ID"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create a budget
        create_response = client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        budget_id = create_response.json()["id"]
        
        # Get the budget
        response = client.get(f"/api/monthly-budgets/{budget_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == budget_id
        assert data["category_id"] == "food"
    
    def test_get_monthly_budget_not_found(self, client):
        """Test getting non-existent monthly budget"""
        response = client.get("/api/monthly-budgets/999")
        assert response.status_code == 404
    
    def test_delete_monthly_budget(self, client):
        """Test deleting a monthly budget"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create a budget
        create_response = client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        budget_id = create_response.json()["id"]
        
        # Delete the budget
        response = client.delete(f"/api/monthly-budgets/{budget_id}")
        assert response.status_code == 200
        
        # Verify it's deleted
        get_response = client.get(f"/api/monthly-budgets/{budget_id}")
        assert get_response.status_code == 404
    
    def test_get_monthly_budget_summary(self, client):
        """Test getting monthly budget summary"""
        # Initialize categories
        from app.services.category import CategoryService
        from app.database import get_db
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Create budgets
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "housing",
            "amount": 50656
        })
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "food",
            "amount": 90000
        })
        client.post("/api/monthly-budgets", json={
            "month": "2025-12",
            "category_id": "daily_goods",
            "amount": 20000
        })
        
        # Get summary
        response = client.get("/api/monthly-budgets/summary/2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["total_budget"] == 160656
    
    def test_get_monthly_budget_summary_no_budgets(self, client):
        """Test getting monthly budget summary with no budgets"""
        response = client.get("/api/monthly-budgets/summary/2025-12")
        assert response.status_code == 200
        data = response.json()
        assert data["month"] == "2025-12"
        assert data["total_budget"] == 0


class TestInitialDataRegistration:
    """Test initial data registration for categories and budgets"""
    
    def test_default_categories_initialization(self, client):
        """Test that default categories are initialized correctly"""
        from app.services.category import CategoryService
        from app.database import get_db
        
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        
        # Get all categories
        categories = service.get_all_categories()
        
        # Verify 14 categories exist
        assert len(categories) == 14
        
        # Verify specific categories exist
        category_ids = [cat.id for cat in categories]
        assert "housing" in category_ids
        assert "food" in category_ids
        assert "utilities" in category_ids
        assert "special" in category_ids
        
        db.close()
    
    def test_default_categories_via_api(self, client):
        """Test that default categories are accessible via API"""
        from app.services.category import CategoryService
        from app.database import get_db
        
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Get categories via API
        response = client.get("/api/categories")
        assert response.status_code == 200
        categories = response.json()
        
        # Verify 14 categories
        assert len(categories) == 14
        
        # Verify category structure
        for cat in categories:
            assert "id" in cat
            assert "name" in cat
            assert "type" in cat
            assert "is_active" in cat
    
    def test_default_categories_by_type(self, client):
        """Test that categories can be filtered by type"""
        from app.services.category import CategoryService
        from app.database import get_db
        
        db = next(get_db())
        service = CategoryService(db)
        service.initialize_default_categories()
        db.close()
        
        # Get fixed type categories
        response = client.get("/api/categories?type=fixed")
        assert response.status_code == 200
        fixed_categories = response.json()
        
        # Verify fixed categories (housing, utilities, communication, insurance, taxes)
        assert len(fixed_categories) == 5
        assert all(cat["type"] == "fixed" for cat in fixed_categories)
        
        # Get variable type categories
        response = client.get("/api/categories?type=variable")
        assert response.status_code == 200
        variable_categories = response.json()
        
        # Verify variable categories (food, daily_goods, transportation, medical)
        assert len(variable_categories) == 4
        assert all(cat["type"] == "variable" for cat in variable_categories)
    
    def test_default_budgets_initialization(self, client):
        """Test that default budgets are initialized correctly"""
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        from app.database import get_db
        from datetime import datetime
        
        db = next(get_db())
        
        # Initialize categories first
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        
        # Initialize default budgets
        current_month = datetime.now().strftime("%Y-%m")
        budget_service = MonthlyBudgetService(db)
        budget_service.initialize_default_budgets(current_month)
        
        # Get budgets for current month
        budgets = budget_service.get_budgets_by_month(current_month)
        
        # Verify 14 budgets exist
        assert len(budgets) == 14
        
        # Verify specific budget amounts
        budget_dict = {b.category_id: b.amount for b in budgets}
        assert budget_dict["housing"] == 50656
        assert budget_dict["food"] == 90000
        assert budget_dict["utilities"] == 17000
        
        db.close()
    
    def test_default_budgets_via_api(self, client):
        """Test that default budgets are accessible via API"""
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        from app.database import get_db
        from datetime import datetime
        
        db = next(get_db())
        
        # Initialize categories and budgets
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        
        current_month = datetime.now().strftime("%Y-%m")
        budget_service = MonthlyBudgetService(db)
        budget_service.initialize_default_budgets(current_month)
        
        db.close()
        
        # Get budgets via API
        response = client.get(f"/api/monthly-budgets?month={current_month}")
        assert response.status_code == 200
        budgets = response.json()
        
        # Verify 14 budgets
        assert len(budgets) == 14
        
        # Verify budget structure
        for budget in budgets:
            assert "category_id" in budget
            assert "category_name" in budget
            assert "category_type" in budget
            assert "amount" in budget
    
    def test_default_budgets_total(self, client):
        """Test that default budgets total is correct"""
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        from app.database import get_db
        from datetime import datetime
        
        db = next(get_db())
        
        # Initialize categories and budgets
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        
        current_month = datetime.now().strftime("%Y-%m")
        budget_service = MonthlyBudgetService(db)
        budget_service.initialize_default_budgets(current_month)
        
        # Get budgets and print them
        budgets = budget_service.get_budgets_by_month(current_month)
        total_from_budgets = sum(b.amount for b in budgets)
        
        # Get total budget
        total = budget_service.get_budget_total(current_month)
        
        # Verify total matches the sum of individual budgets
        assert total == total_from_budgets
        # Verify we have 14 budgets
        assert len(budgets) == 14
        
        db.close()
    
    def test_default_budgets_via_summary_api(self, client):
        """Test that default budgets total is accessible via summary API"""
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        from app.database import get_db
        from datetime import datetime
        
        db = next(get_db())
        
        # Initialize categories and budgets
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        
        current_month = datetime.now().strftime("%Y-%m")
        budget_service = MonthlyBudgetService(db)
        budget_service.initialize_default_budgets(current_month)
        
        # Get the expected total
        expected_total = budget_service.get_budget_total(current_month)
        
        db.close()
        
        # Get summary via API
        response = client.get(f"/api/monthly-budgets/summary/{current_month}")
        assert response.status_code == 200
        data = response.json()
        
        # Verify total budget matches
        assert data["month"] == current_month
        assert data["total_budget"] == expected_total
    
    def test_no_duplicate_categories_on_reinit(self, client):
        """Test that reinitializing categories doesn't create duplicates"""
        from app.services.category import CategoryService
        from app.database import get_db
        
        db = next(get_db())
        service = CategoryService(db)
        
        # Initialize categories twice
        service.initialize_default_categories()
        service.initialize_default_categories()
        
        # Get all categories
        categories = service.get_all_categories()
        
        # Verify still only 14 categories
        assert len(categories) == 14
        
        db.close()
    
    def test_no_duplicate_budgets_on_reinit(self, client):
        """Test that reinitializing budgets doesn't create duplicates"""
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        from app.database import get_db
        from datetime import datetime
        
        db = next(get_db())
        
        # Initialize categories
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        
        current_month = datetime.now().strftime("%Y-%m")
        budget_service = MonthlyBudgetService(db)
        
        # Initialize budgets twice
        budget_service.initialize_default_budgets(current_month)
        budget_service.initialize_default_budgets(current_month)
        
        # Get budgets
        budgets = budget_service.get_budgets_by_month(current_month)
        
        # Verify still only 14 budgets
        assert len(budgets) == 14
        
        db.close()
