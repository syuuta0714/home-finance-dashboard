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
