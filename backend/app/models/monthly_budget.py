"""MonthlyBudget model definition"""

from sqlalchemy import Column, Integer, String, DateTime, CheckConstraint, UniqueConstraint, ForeignKey, Index
from sqlalchemy.sql import func
from app.database import Base


class MonthlyBudget(Base):
    """MonthlyBudget model for storing monthly budget by category"""
    
    __tablename__ = "monthly_budgets"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    month = Column(String(7), nullable=False, comment="YYYY-MM format")
    category_id = Column(String(50), ForeignKey("categories.id"), nullable=False)
    amount = Column(Integer, nullable=False, comment="Monthly budget amount in yen")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_monthly_budget_amount_positive'),
        UniqueConstraint('month', 'category_id', name='uq_monthly_budget_month_category'),
        Index('ix_monthly_budgets_month', 'month'),
        Index('ix_monthly_budgets_category_id', 'category_id'),
    )
    
    def __repr__(self):
        return f"<MonthlyBudget(id={self.id}, month={self.month}, category_id={self.category_id}, amount={self.amount})>"
