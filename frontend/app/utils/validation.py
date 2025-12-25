"""Client-side validation utilities"""

import re
from datetime import date
from typing import Optional, Tuple


def validate_month(month_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate month format (YYYY-MM)
    
    Args:
        month_str: Month string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not month_str:
        return False, "月を入力してください"
    
    # Check format
    if not re.match(r'^\d{4}-\d{2}$', month_str):
        return False, "月はYYYY-MM形式で入力してください（例: 2025-12）"
    
    # Check valid month range
    try:
        year, month = month_str.split("-")
        year_int = int(year)
        month_int = int(month)
        
        if year_int < 2000 or year_int > 2100:
            return False, "年は2000-2100の範囲で入力してください"
        
        if month_int < 1 or month_int > 12:
            return False, "月は01-12の範囲で入力してください"
        
        return True, None
    except:
        return False, "無効な月形式です"


def validate_date(date_str: str) -> Tuple[bool, Optional[str]]:
    """
    Validate date format (YYYY-MM-DD)
    
    Args:
        date_str: Date string to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not date_str:
        return False, "日付を入力してください"
    
    # Check format
    if not re.match(r'^\d{4}-\d{2}-\d{2}$', date_str):
        return False, "日付はYYYY-MM-DD形式で入力してください（例: 2025-12-25）"
    
    # Check valid date
    try:
        year, month, day = date_str.split("-")
        date(int(year), int(month), int(day))
        return True, None
    except ValueError:
        return False, "無効な日付です"


def validate_amount(amount: Optional[int]) -> Tuple[bool, Optional[str]]:
    """
    Validate amount (must be >= 0)
    
    Args:
        amount: Amount to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if amount is None:
        return False, "金額を入力してください"
    
    if not isinstance(amount, int):
        return False, "金額は整数で入力してください"
    
    if amount < 0:
        return False, "金額は0以上で入力してください"
    
    return True, None


def validate_category(category: str) -> Tuple[bool, Optional[str]]:
    """
    Validate category (must not be empty)
    
    Args:
        category: Category to validate
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not category or not category.strip():
        return False, "カテゴリを選択してください"
    
    return True, None


def validate_memo(memo: Optional[str], max_length: int = 500) -> Tuple[bool, Optional[str]]:
    """
    Validate memo (optional, but check length if provided)
    
    Args:
        memo: Memo to validate
        max_length: Maximum allowed length
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if memo and len(memo) > max_length:
        return False, f"メモは{max_length}文字以内で入力してください"
    
    return True, None


# Predefined categories
CATEGORIES = [
    "食費",
    "日用品",
    "交通費",
    "娯楽",
    "医療費",
    "その他"
]


def get_categories() -> list[str]:
    """
    Get list of available categories
    
    Returns:
        List of category names
    """
    return CATEGORIES.copy()
