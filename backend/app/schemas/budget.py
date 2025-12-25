"""Budget Pydantic schemas"""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator
import re


class BudgetCreate(BaseModel):
    """Schema for creating a budget"""
    
    month: str = Field(..., description="Month in YYYY-MM format")
    category: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., ge=0, description="Budget amount in yen")
    
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


class Budget(BaseModel):
    """Schema for budget response"""
    
    id: int
    month: str
    category: str
    amount: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True
