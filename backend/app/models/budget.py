"""Budget model definition"""

from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class Budget(Base):
    """Budget model for storing monthly budget by category"""
    
    __tablename__ = "budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False, comment="YYYY-MM format")
    category = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False, comment="Budget amount in yen")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_budget_amount_positive'),
        UniqueConstraint('month', 'category', name='uq_budget_month_category'),
        Index('ix_budgets_month', 'month'),
        Index('ix_budgets_category', 'category'),
    )
    
    def __repr__(self):
        return f"<Budget(id={self.id}, month={self.month}, category={self.category}, amount={self.amount})>"
