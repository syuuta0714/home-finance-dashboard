"""Category and MonthlyBudget Pydantic schemas"""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, field_validator
import re


class CategorySchema(BaseModel):
    """Schema for category response (read-only)"""
    
    id: str = Field(..., description="Immutable category ID (snake_case)")
    name: str = Field(..., description="Display name in Japanese")
    type: str = Field(..., description="Category type: fixed, variable, lifestyle, event")
    is_active: bool = Field(..., description="Active flag")
    note: Optional[str] = Field(None, description="Additional notes")
    
    class Config:
        from_attributes = True


class MonthlyBudgetSchema(BaseModel):
    """Schema for monthly budget response (read-only)"""
    
    id: int = Field(..., description="Monthly budget ID")
    month: str = Field(..., description="Month in YYYY-MM format")
    category_id: str = Field(..., description="Category ID")
    amount: int = Field(..., ge=0, description="Monthly budget amount in yen")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class MonthlyBudgetCreateSchema(BaseModel):
    """Schema for creating/updating a monthly budget"""
    
    month: str = Field(..., description="Month in YYYY-MM format")
    category_id: str = Field(..., description="Category ID")
    amount: int = Field(..., ge=0, description="Monthly budget amount in yen")
    
    @field_validator('month')
    @classmethod
    def validate_month(cls, v: str) -> str:
        """Validate month format (YYYY-MM)"""
        if not re.match(r'^\d{4}-\d{2}$', v):
            raise ValueError('month must be in YYYY-MM format')
        
        # Validate month range
        year, month = v.split('-')
        month_int = int(month)
        if month_int < 1 or month_int > 12:
            raise ValueError('month must be between 01 and 12')
        
        return v
    
    @field_validator('amount')
    @classmethod
    def validate_amount(cls, v: int) -> int:
        """Validate amount is non-negative"""
        if v < 0:
            raise ValueError('amount must be non-negative')
        return v


class MonthlyBudgetDetailSchema(BaseModel):
    """Schema for detailed monthly budget with category information"""
    
    id: int = Field(..., description="Monthly budget ID")
    category_id: str = Field(..., description="Category ID")
    category_name: str = Field(..., description="Category name in Japanese")
    category_type: str = Field(..., description="Category type: fixed, variable, lifestyle, event")
    amount: int = Field(..., ge=0, description="Monthly budget amount in yen")
    
    class Config:
        from_attributes = True
