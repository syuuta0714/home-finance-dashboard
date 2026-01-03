"""Expense API router"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.expense import Expense, ExpenseCreate
from app.services.expense import ExpenseService
from app.config import settings

router = APIRouter()


@router.post("/api/expenses", response_model=Expense, status_code=201)
async def create_expense(
    expense_data: ExpenseCreate,
    db: Session = Depends(get_db)
):
    """
    Register a new expense.
    The month is automatically derived from the date.
    
    Args:
        expense_data: Expense creation data
        db: Database session
        
    Returns:
        Created expense
    """
    service = ExpenseService(db, timezone=settings.timezone)
    return service.register_expense(expense_data)


@router.get("/api/expenses", response_model=List[Expense])
async def get_expenses(
    month: Optional[str] = Query(None, description="Filter by month (YYYY-MM)"),
    category: Optional[str] = Query(None, description="Filter by category"),
    db: Session = Depends(get_db)
):
    """
    Get all expenses, optionally filtered by month and/or category.
    
    Args:
        month: Optional month filter in YYYY-MM format
        category: Optional category filter
        db: Database session
        
    Returns:
        List of expenses
    """
    service = ExpenseService(db, timezone=settings.timezone)
    
    if month and category:
        return service.get_expenses_by_month_and_category(month, category)
    elif month:
        return service.get_expenses_by_month(month)
    elif category:
        return service.get_expenses_by_category(category)
    
    # If no filters specified, return empty list
    # Note: This could be optimized with a get_all method in the future
    return []


@router.get("/api/expenses/{expense_id}", response_model=Expense)
async def get_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    """
    Get a specific expense by ID.
    
    Args:
        expense_id: Expense ID
        db: Database session
        
    Returns:
        Expense details
        
    Raises:
        HTTPException: 404 if expense not found
    """
    service = ExpenseService(db, timezone=settings.timezone)
    expense = service.get_expense_by_id(expense_id)
    
    if not expense:
        raise HTTPException(
            status_code=404,
            detail=f"Expense with id {expense_id} not found"
        )
    
    return expense


@router.delete("/api/expenses/{expense_id}")
async def delete_expense(
    expense_id: int,
    db: Session = Depends(get_db)
):
    """
    Delete an expense by ID.
    
    Args:
        expense_id: Expense ID
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: 404 if expense not found
    """
    service = ExpenseService(db, timezone=settings.timezone)
    deleted = service.delete_expense(expense_id)
    
    if not deleted:
        raise HTTPException(
            status_code=404,
            detail=f"Expense with id {expense_id} not found"
        )
    
    return {"message": "deleted"}


@router.get("/api/expenses/statistics/{month}")
async def get_expense_statistics(
    month: str,
    db: Session = Depends(get_db)
):
    """
    Get expense statistics grouped by category for a specific month.
    
    Args:
        month: Month in YYYY-MM format
        db: Database session
        
    Returns:
        Dictionary with category as key and total amount as value
    """
    service = ExpenseService(db, timezone=settings.timezone)
    return service.get_expenses_summary_by_category(month)
