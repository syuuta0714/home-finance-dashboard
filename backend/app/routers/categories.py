"""Category API router"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.category import CategorySchema
from app.services.category import CategoryService

router = APIRouter()


@router.get("/api/categories", response_model=List[CategorySchema])
async def get_categories(
    type: Optional[str] = Query(None, description="Filter by category type (fixed, variable, lifestyle, event)"),
    db: Session = Depends(get_db)
):
    """
    Get all categories, optionally filtered by type.
    
    Args:
        type: Optional category type filter
        db: Database session
        
    Returns:
        List of categories
    """
    service = CategoryService(db)
    
    if type:
        return service.get_categories_by_type(type)
    
    return service.get_all_categories()


@router.get("/api/categories/{category_id}", response_model=CategorySchema)
async def get_category(
    category_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific category by ID.
    
    Args:
        category_id: Category ID
        db: Database session
        
    Returns:
        Category details
        
    Raises:
        HTTPException: 404 if category not found
    """
    service = CategoryService(db)
    category = service.get_category_by_id(category_id)
    
    if not category:
        raise HTTPException(
            status_code=404,
            detail=f"Category with id {category_id} not found"
        )
    
    return category
