"""Formatting utilities for numbers and dates"""

from datetime import date, datetime
from typing import Optional
import pytz
from app.config import settings


def format_currency(amount: int) -> str:
    """
    Format amount as Japanese yen currency
    
    Args:
        amount: Amount in yen
    
    Returns:
        Formatted string (e.g., "¥123,456")
    """
    return f"¥{amount:,}"


def format_percentage(value: float, decimals: int = 1) -> str:
    """
    Format value as percentage
    
    Args:
        value: Percentage value (0-100+)
        decimals: Number of decimal places
    
    Returns:
        Formatted string (e.g., "75.5%")
    """
    return f"{value:.{decimals}f}%"


def format_date(date_obj: date) -> str:
    """
    Format date as Japanese format
    
    Args:
        date_obj: Date object
    
    Returns:
        Formatted string (e.g., "2025年12月25日")
    """
    return date_obj.strftime("%Y年%m月%d日")


def format_month(month_str: str) -> str:
    """
    Format month string as Japanese format
    
    Args:
        month_str: Month in YYYY-MM format
    
    Returns:
        Formatted string (e.g., "2025年12月")
    """
    try:
        year, month = month_str.split("-")
        return f"{year}年{month}月"
    except:
        return month_str


def get_current_month(tz: Optional[str] = None) -> str:
    """
    Get current month in YYYY-MM format
    
    Args:
        tz: Timezone (defaults to settings.timezone)
    
    Returns:
        Current month string (e.g., "2025-12")
    """
    timezone = pytz.timezone(tz or settings.timezone)
    now = datetime.now(timezone)
    return now.strftime("%Y-%m")


def get_current_date(tz: Optional[str] = None) -> date:
    """
    Get current date in specified timezone
    
    Args:
        tz: Timezone (defaults to settings.timezone)
    
    Returns:
        Current date object
    """
    timezone = pytz.timezone(tz or settings.timezone)
    now = datetime.now(timezone)
    return now.date()


def parse_date(date_str: str) -> Optional[date]:
    """
    Parse date string in YYYY-MM-DD format
    
    Args:
        date_str: Date string
    
    Returns:
        Date object or None if invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").date()
    except:
        return None


def parse_month(month_str: str) -> Optional[tuple[int, int]]:
    """
    Parse month string in YYYY-MM format
    
    Args:
        month_str: Month string
    
    Returns:
        Tuple of (year, month) or None if invalid
    """
    try:
        year, month = month_str.split("-")
        return (int(year), int(month))
    except:
        return None


def format_days_remaining(days: int) -> str:
    """
    Format remaining days
    
    Args:
        days: Number of days
    
    Returns:
        Formatted string (e.g., "15日")
    """
    if days < 0:
        return "0日"
    return f"{days}日"


def format_per_day_budget(amount: Optional[float]) -> str:
    """
    Format per-day budget amount
    
    Args:
        amount: Amount per day (can be None)
    
    Returns:
        Formatted string (e.g., "¥5,000/日" or "-")
    """
    if amount is None:
        return "-"
    return f"{format_currency(int(amount))}/日"
