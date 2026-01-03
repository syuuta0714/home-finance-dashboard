"""Database connection and session management"""

import logging
from datetime import datetime
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator

from app.config import settings

logger = logging.getLogger(__name__)

# Create Base class for models FIRST (before importing models)
Base = declarative_base()

# Create SQLAlchemy engine
engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {},
    echo=settings.log_level == "DEBUG"
)

# Create SessionLocal class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Import all models to register them with SQLAlchemy
# This must be done after Base is created
from app.models import Budget, Expense, Category, MonthlyBudget  # noqa: F401


def get_db() -> Generator[Session, None, None]:
    """
    Dependency function to get database session.
    Yields a database session and ensures it's closed after use.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Initialize database by creating all tables.
    Should be called on application startup.
    """
    Base.metadata.create_all(bind=engine)
    
    # Initialize default categories and budgets
    db = SessionLocal()
    try:
        from app.services.category import CategoryService
        from app.services.monthly_budget import MonthlyBudgetService
        
        # Initialize default categories
        category_service = CategoryService(db)
        category_service.initialize_default_categories()
        logger.info("Default categories initialized")
        
        # Initialize default budgets for current month
        current_month = datetime.now().strftime("%Y-%m")
        monthly_budget_service = MonthlyBudgetService(db)
        monthly_budget_service.initialize_default_budgets(current_month)
        logger.info(f"Default budgets initialized for month {current_month}")
        
        db.commit()
    except Exception as e:
        logger.error(f"Error initializing default data: {e}", exc_info=True)
        db.rollback()
    finally:
        db.close()

