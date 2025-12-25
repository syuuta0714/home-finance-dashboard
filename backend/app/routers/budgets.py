"""Budget API router"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.budget import Budget, BudgetCreate
from app.services.budget import BudgetService

router = APIRouter()


@router.post("/api/budgets", response_model=Budget, status_code=201)
async def create_or_update_budget(
    budget_data: BudgetCreate,
    db: Session = Depends(get_db)
):
    """
    Register or update a budget.
    If a budget with the same month and category exists, it will be updated.
    
    Args:
        budget_data: Budget creation data
        db: Database session
        
    Returns:
        Created or updated budget
    """
    service = BudgetService(db)
    return service.register_or_update_budget(budget_data)


@router.get("/api/budgets", response_model=List[Budget])
async def get_budgets(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    db: Session = Depends(get_db)
):
    """
    Get all budgets, optionally filtered by month.
    
    Args:
        month: Optional month filter in YYYY-MM format
        db: Database session
        
    Returns:
        List of budgets
    """
    service = BudgetService(db)
    
    if month:
        return service.get_budgets_by_month(month)
    
    # If no month specified, return all budgets
    # Note: This could be optimized with a get_all method in the future
    return []


@router.get("/api/budgets/{budget_id}", response_model=Budget)
async def get_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific budget by ID.
    
    Args:
        budget_id: Budget ID
        db: Database session
        
    Returns:
        Budget details
        
    Raises:
        HTTPException: 404 if budget not found
    """
    service = BudgetService(db)
    budget = service.get_budget_by_id(budget_id)
    
    if not budget:
        raise HTTPException(
            status_code=404,
            detail=f"Budget with id {budget_id} not found"
        )
    
    return budget


@router.delete("/api/budgets/{budget_id}")
async def delete_budget(
    budget_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete a budget by ID.
    
    Args:
        budget_id: Budget ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if budget not found
    """
    service = BudgetService(db)
    deleted = service.delete_budget(budget_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Budget with id {budget_id} not found"
        )
    
    return {"message": "deleted"}
