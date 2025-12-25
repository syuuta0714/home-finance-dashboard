"""Expense Pydantic schemas"""

from datetime import datetime, date as date_type
from typing import Optional, Any
from pydantic import BaseModel, Field, field_serializer, model_validator


class ExpenseCreate(BaseModel):
    """Schema for creating an expense"""
    
    date: str = Field(..., description="Expense date (YYYY-MM-DD)")
    category: str = Field(..., min_length=1, max_length=50)
    amount: int = Field(..., ge=0, description="Expense amount in yen")
    memo: Optional[str] = Field(None, description="Optional memo")


class Expense(BaseModel):
    """Schema for expense response"""
    
    id: int
    date: str
    month: str
    category: str
    amount: int
    memo: Optional[str]
    created_at: datetime
    
    @model_validator(mode='before')
    @classmethod
    def convert_date_to_string(cls, data: Any) -> Any:
        """Convert date object to string before validation"""
        if isinstance(data, dict):
            if 'date' in data and isinstance(data['date'], date_type):
                data['date'] = data['date'].strftime("%Y-%m-%d")
        elif hasattr(data, 'date') and isinstance(data.date, date_type):
            # Handle SQLAlchemy model objects
            data_dict = {}
            for key in ['id', 'date', 'month', 'category', 'amount', 'memo', 'created_at']:
                value = getattr(data, key, None)
                if key == 'date' and isinstance(value, date_type):
                    data_dict[key] = value.strftime("%Y-%m-%d")
                else:
                    data_dict[key] = value
            return data_dict
        return data
    
    class Config:
        from_attributes = True
