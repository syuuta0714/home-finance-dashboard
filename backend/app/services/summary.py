"""Summary service for monthly aggregation and calculation"""

from typing import Optional
from datetime import datetime, date
from calendar import monthrange
from sqlalchemy.orm import Session
import pytz

from app.repositories.budget import BudgetRepository
from app.repositories.expense import ExpenseRepository
from app.schemas.summary import Summary


class SummaryService:
    """Service for monthly summary calculations"""
    
    def __init__(self, db: Session, timezone: str = "Asia/Tokyo"):
        """
        Initialize Summary service.
        
        Args:
            db: Database session
            timezone: Timezone for date calculations (default: Asia/Tokyo)
        """
        self.budget_repository = BudgetRepository(db)
        self.expense_repository = ExpenseRepository(db)
        self.timezone = pytz.timezone(timezone)
    
    def calculate_summary(self, month: Optional[str] = None) -> Summary:
        """
        Calculate monthly summary with budget, expenses, and status.
        
        Args:
            month: Month in YYYY-MM format (default: current month in configured timezone)
            
        Returns:
            Summary schema with all calculated fields
        """
        # If no month specified, use current month in the configured timezone
        if month is None:
            now = datetime.now(self.timezone)
            month = now.strftime("%Y-%m")
        
        # 1. Get total budget for the month
        budgets = self.budget_repository.get_by_month(month)
        total_budget = sum(budget.amount for budget in budgets)
        
        # 2. Get total spent for the month
        expenses = self.expense_repository.get_by_month(month)
        total_spent = sum(expense.amount for expense in expenses)
        
        # 3. Calculate remaining budget
        remaining = total_budget - total_spent
        
        # 4. Calculate remaining days in the month (Asia/Tokyo timezone)
        remaining_days = self._calculate_remaining_days(month)
        
        # 5. Calculate per-day budget
        per_day_budget = None
        if remaining_days > 0:
            per_day_budget = remaining / remaining_days
        
        # 6. Calculate usage rate
        usage_rate = 0.0
        if total_budget > 0:
            usage_rate = (total_spent / total_budget) * 100
        
        # 7. Determine status based on usage rate
        status, status_message, status_color = self._determine_status(usage_rate)
        
        return Summary(
            month=month,
            total_budget=total_budget,
            total_spent=total_spent,
            remaining=remaining,
            remaining_days=remaining_days,
            per_day_budget=per_day_budget,
            usage_rate=usage_rate,
            status=status,
            status_message=status_message,
            status_color=status_color
        )
    
    def _calculate_remaining_days(self, month: str) -> int:
        """
        Calculate remaining days in the month from today (inclusive).
        Uses the configured timezone for "today".
        
        Args:
            month: Month in YYYY-MM format
            
        Returns:
            Number of remaining days (0 if month has passed)
        """
        # Get today's date in the configured timezone
        today = datetime.now(self.timezone).date()
        
        # Parse the month
        year, month_num = map(int, month.split('-'))
        
        # Get the last day of the month
        last_day_num = monthrange(year, month_num)[1]
        last_day = date(year, month_num, last_day_num)
        
        # Calculate remaining days
        if today > last_day:
            # Month has passed
            return 0
        elif today.year == year and today.month == month_num:
            # We're in the target month
            remaining = (last_day - today).days + 1  # +1 to include today
            return max(0, remaining)
        elif today < date(year, month_num, 1):
            # Month is in the future - return total days in month
            return last_day_num
        else:
            return 0
    
    def _determine_status(self, usage_rate: float) -> tuple[str, str, str]:
        """
        Determine status based on usage rate.
        
        Args:
            usage_rate: Usage rate as percentage (0-100+)
            
        Returns:
            Tuple of (status, status_message, status_color)
        """
        if usage_rate < 70:
            return (
                "OK",
                "予算内で順調です",
                "green"
            )
        elif usage_rate < 90:
            return (
                "WARN",
                "予算の70%を超えました。注意してください",
                "yellow"
            )
        else:
            return (
                "DANGER",
                "予算の90%を超えました！支出を抑えてください",
                "red"
            )
