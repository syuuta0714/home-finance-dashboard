"""Backend API client with error handling and retry logic"""

import time
from typing import Optional, Dict, Any, List
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from app.config import settings


class APIError(Exception):
    """Custom exception for API errors"""
    def __init__(self, message: str, status_code: Optional[int] = None, detail: Optional[str] = None):
        self.message = message
        self.status_code = status_code
        self.detail = detail
        super().__init__(self.message)


class APIClient:
    """Client for interacting with the backend API"""
    
    def __init__(self, base_url: Optional[str] = None, timeout: int = 10, max_retries: int = 3):
        """
        Initialize API client
        
        Args:
            base_url: Base URL for the API (defaults to settings.backend_url)
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
        """
        self.base_url = (base_url or settings.backend_url).rstrip('/')
        self.timeout = timeout
        
        # Configure session with retry logic
        self.session = requests.Session()
        retry_strategy = Retry(
            total=max_retries,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["HEAD", "GET", "OPTIONS", "POST", "PUT", "DELETE"]
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request with error handling
        
        Args:
            method: HTTP method
            endpoint: API endpoint (without base URL)
            **kwargs: Additional arguments for requests
        
        Returns:
            Response object
        
        Raises:
            APIError: If request fails
        """
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = self.session.request(
                method=method,
                url=url,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response
        except requests.exceptions.HTTPError as e:
            # Extract error details from response
            detail = None
            try:
                error_data = e.response.json()
                detail = error_data.get("detail", str(e))
            except:
                detail = str(e)
            
            raise APIError(
                message=f"HTTP error: {e.response.status_code}",
                status_code=e.response.status_code,
                detail=detail
            )
        except requests.exceptions.ConnectionError as e:
            raise APIError(
                message=f"接続エラー: バックエンドに接続できません ({self.base_url})",
                detail=str(e)
            )
        except requests.exceptions.Timeout as e:
            raise APIError(
                message=f"タイムアウト: リクエストが{self.timeout}秒以内に完了しませんでした",
                detail=str(e)
            )
        except requests.exceptions.RequestException as e:
            raise APIError(
                message=f"リクエストエラー: {str(e)}",
                detail=str(e)
            )
    
    def health_check(self) -> Dict[str, Any]:
        """Check API health"""
        response = self._request("GET", "/health")
        return response.json()
    
    # Budget endpoints
    
    def create_budget(self, month: str, category: str, amount: int) -> Dict[str, Any]:
        """
        Create or update budget
        
        Args:
            month: Month in YYYY-MM format
            category: Budget category
            amount: Budget amount in yen
        
        Returns:
            Created/updated budget data
        """
        response = self._request(
            "POST",
            "/api/budgets",
            json={"month": month, "category": category, "amount": amount}
        )
        return response.json()
    
    def get_budgets(self, month: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get budgets, optionally filtered by month
        
        Args:
            month: Optional month filter in YYYY-MM format
        
        Returns:
            List of budget data
        """
        params = {"month": month} if month else {}
        response = self._request("GET", "/api/budgets", params=params)
        return response.json()
    
    def get_budget(self, budget_id: int) -> Dict[str, Any]:
        """
        Get budget by ID
        
        Args:
            budget_id: Budget ID
        
        Returns:
            Budget data
        """
        response = self._request("GET", f"/api/budgets/{budget_id}")
        return response.json()
    
    def delete_budget(self, budget_id: int) -> Dict[str, Any]:
        """
        Delete budget
        
        Args:
            budget_id: Budget ID
        
        Returns:
            Deletion confirmation
        """
        response = self._request("DELETE", f"/api/budgets/{budget_id}")
        return response.json()
    
    # Expense endpoints
    
    def create_expense(
        self,
        date: str,
        category: str,
        amount: int,
        memo: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Create expense
        
        Args:
            date: Expense date in YYYY-MM-DD format
            category: Expense category
            amount: Expense amount in yen
            memo: Optional memo
        
        Returns:
            Created expense data
        """
        data = {
            "date": date,
            "category": category,
            "amount": amount
        }
        if memo:
            data["memo"] = memo
        
        response = self._request("POST", "/api/expenses", json=data)
        return response.json()
    
    def get_expenses(
        self,
        month: Optional[str] = None,
        category: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get expenses, optionally filtered by month and/or category
        
        Args:
            month: Optional month filter in YYYY-MM format
            category: Optional category filter
        
        Returns:
            List of expense data
        """
        params = {}
        if month:
            params["month"] = month
        if category:
            params["category"] = category
        
        response = self._request("GET", "/api/expenses", params=params)
        return response.json()
    
    def get_expense(self, expense_id: int) -> Dict[str, Any]:
        """
        Get expense by ID
        
        Args:
            expense_id: Expense ID
        
        Returns:
            Expense data
        """
        response = self._request("GET", f"/api/expenses/{expense_id}")
        return response.json()
    
    def delete_expense(self, expense_id: int) -> Dict[str, Any]:
        """
        Delete expense
        
        Args:
            expense_id: Expense ID
        
        Returns:
            Deletion confirmation
        """
        response = self._request("DELETE", f"/api/expenses/{expense_id}")
        return response.json()
    
    def get_expense_statistics(self, month: str) -> Dict[str, int]:
        """
        Get expense statistics grouped by category for a specific month
        
        Args:
            month: Month in YYYY-MM format
        
        Returns:
            Dictionary with category as key and total amount as value
        """
        response = self._request("GET", f"/api/expenses/statistics/{month}")
        return response.json()
    
    # Category endpoints
    
    def get_categories(self, category_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all categories, optionally filtered by type
        
        Args:
            category_type: Optional category type filter (fixed, variable, lifestyle, event)
        
        Returns:
            List of category data
        """
        params = {"type": category_type} if category_type else {}
        response = self._request("GET", "/api/categories", params=params)
        return response.json()
    
    def get_category(self, category_id: str) -> Dict[str, Any]:
        """
        Get category by ID
        
        Args:
            category_id: Category ID
        
        Returns:
            Category data
        """
        response = self._request("GET", f"/api/categories/{category_id}")
        return response.json()
    
    # Monthly Budget endpoints
    
    def create_monthly_budget(self, month: str, category_id: str, amount: int) -> Dict[str, Any]:
        """
        Create or update monthly budget
        
        Args:
            month: Month in YYYY-MM format
            category_id: Category ID
            amount: Budget amount in yen
        
        Returns:
            Created/updated monthly budget data
        """
        response = self._request(
            "POST",
            "/api/monthly-budgets",
            json={"month": month, "category_id": category_id, "amount": amount}
        )
        return response.json()
    
    def get_monthly_budgets(
        self,
        month: str,
        category_type: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get monthly budgets for a specific month
        
        Args:
            month: Month in YYYY-MM format (required)
            category_type: Optional category type filter
        
        Returns:
            List of monthly budget data
        """
        params = {"month": month}
        if category_type:
            params["category_type"] = category_type
        
        response = self._request("GET", "/api/monthly-budgets", params=params)
        return response.json()
    
    def get_monthly_budget(self, budget_id: int) -> Dict[str, Any]:
        """
        Get monthly budget by ID
        
        Args:
            budget_id: Monthly budget ID
        
        Returns:
            Monthly budget data
        """
        response = self._request("GET", f"/api/monthly-budgets/{budget_id}")
        return response.json()
    
    def delete_monthly_budget(self, budget_id: int) -> Dict[str, Any]:
        """
        Delete monthly budget
        
        Args:
            budget_id: Monthly budget ID
        
        Returns:
            Deletion confirmation
        """
        response = self._request("DELETE", f"/api/monthly-budgets/{budget_id}")
        return response.json()
    
    def get_monthly_budget_summary(self, month: str) -> Dict[str, Any]:
        """
        Get monthly budget summary
        
        Args:
            month: Month in YYYY-MM format
        
        Returns:
            Summary data with total budget amount
        """
        response = self._request("GET", f"/api/monthly-budgets/summary/{month}")
        return response.json()
    
    # Summary endpoint
    
    def get_summary(self, month: Optional[str] = None) -> Dict[str, Any]:
        """
        Get monthly summary
        
        Args:
            month: Optional month in YYYY-MM format (defaults to current month)
        
        Returns:
            Summary data including totals, remaining, usage rate, and status
        """
        params = {"month": month} if month else {}
        response = self._request("GET", "/api/summary", params=params)
        return response.json()


# Global API client instance
api_client = APIClient()
