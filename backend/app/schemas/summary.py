"""Summary Pydantic schema"""

from typing import Optional
from pydantic import BaseModel, Field


class Summary(BaseModel):
    """Schema for monthly summary"""
    
    month: str = Field(..., description="Month in YYYY-MM format")
    total_budget: int = Field(..., description="Total budget for the month in yen")
    total_spent: int = Field(..., description="Total spent for the month in yen")
    remaining: int = Field(..., description="Remaining budget in yen")
    remaining_days: int = Field(..., ge=0, description="Days remaining in the month")
    per_day_budget: Optional[float] = Field(None, description="Budget per day (None if remaining_days == 0)")
    usage_rate: float = Field(..., ge=0, description="Usage rate as percentage (0-100+)")
    status: str = Field(..., description="Status: OK, WARN, or DANGER")
    status_message: str = Field(..., description="Human-readable status message")
    status_color: str = Field(..., description="Color for status: green, yellow, or red")
