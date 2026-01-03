"""Monthly Budget API router"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import MonthlyBudgetSchema, MonthlyBudgetCreateSchema, MonthlyBudgetDetailSchema
from app.services.monthly_budget import MonthlyBudgetService

router = APIRouter()


@router.post("/api/monthly-budgets", response_model=MonthlyBudgetSchema, status_code=201)
async def create_or_update_monthly_budget(
    budget_data: MonthlyBudgetCreateSchema,
    db: Session = Depends(get_db)
):
    """
    Register or update a monthly budget.
    If a budget with the same month and category exists, it will be updated.
    
    Args:
        budget_data: Monthly budget creation data
        db: Database session
        
    Returns:
        Created or updated monthly budget
    """
    service = MonthlyBudgetService(db)
    return service.register_budget(budget_data)


@router.get("/api/monthly-budgets", response_model=List[MonthlyBudgetDetailSchema])
async def get_monthly_budgets(
    month: str = Query(..., description="Month in YYYY-MM format"),
    category_type: Optional[str] = Query(None, description="Filter by category type (fixed, variable, lifestyle, event)"),
    db: Session = Depends(get_db)
):
    """
    Get all monthly budgets for a specific month, optionally filtered by category type.
    
    Args:
        month: Month in YYYY-MM format (required)
        category_type: Optional category type filter
        db: Database session
        
    Returns:
        List of monthly budgets with category details
    """
    service = MonthlyBudgetService(db)
    
    if category_type:
        return service.get_budgets_by_month_and_type(month, category_type)
    
    return service.get_budgets_by_month(month)


@router.get("/api/monthly-budgets/{budget_id}", response_model=MonthlyBudgetSchema)
async def get_monthly_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific monthly budget by ID.
    
    Args:
        budget_id: Monthly budget ID
        db: Database session
        
    Returns:
        Monthly budget details
        
    Raises:
        HTTPException: 404 if budget not found
    """
    service = MonthlyBudgetService(db)
    budget = service.repository.get_by_id(budget_id)
    
    if not budget:
        raise HTTPException(
            status_code=404,
            detail=f"Monthly budget with id {budget_id} not found"
        )
    
    return MonthlyBudgetSchema.model_validate(budget)


@router.delete("/api/monthly-budgets/{budget_id}")
async def delete_monthly_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a monthly budget by ID.
    
    Args:
        budget_id: Monthly budget ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if budget not found
    """
    service = MonthlyBudgetService(db)
    deleted = service.delete_budget(budget_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Monthly budget with id {budget_id} not found"
        )
    
    return {"message": "deleted"}


@router.get("/api/monthly-budgets/summary/{month}")
async def get_monthly_budget_summary(
    month: str,
    db: Session = Depends(get_db)
):
    """
    Get the total monthly budget amount for a specific month.
    
    Args:
        month: Month in YYYY-MM format
        db: Database session
        
    Returns:
        Summary with month and total budget amount
    """
    service = MonthlyBudgetService(db)
    total = service.get_budget_total(month)
    
    return {
        "month": month,
        "total_budget": total
    }
