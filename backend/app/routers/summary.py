"""Summary API router"""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.summary import Summary
from app.services.summary import SummaryService
from app.config import settings

router = APIRouter()


@router.get("/api/summary", response_model=Summary)
async def get_summary(
    month: Optional[str] = Query(None, description="Month in YYYY-MM format (default: current month)"),
    db: Session = Depends(get_db)
):
    """
    Get monthly summary with budget, expenses, and status.
    If no month is specified, returns the current month's summary.
    
    Args:
        month: Optional month in YYYY-MM format
        db: Database session
        
    Returns:
        Monthly summary with all calculated fields
    """
    service = SummaryService(db, timezone=settings.timezone)
    return service.calculate_summary(month)
