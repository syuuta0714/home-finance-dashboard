"""Expense model definition"""

from sqlalchemy import Column, Integer, String, Date, Text, DateTime, CheckConstraint, Index
from sqlalchemy.sql import func
from app.database import Base


class Expense(Base):
    """Expense model for storing daily expenses"""
    
    __tablename__ = "expenses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    date = Column(Date, nullable=False, comment="Expense date (YYYY-MM-DD)")
    month = Column(String(7), nullable=False, comment="YYYY-MM format (derived from date)")
    category = Column(String(50), nullable=False)
    amount = Column(Integer, nullable=False, comment="Expense amount in yen")
    memo = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    
    # Constraints
    __table_args__ = (
        CheckConstraint('amount >= 0', name='check_expense_amount_positive'),
        Index('ix_expenses_month', 'month'),
        Index('ix_expenses_category', 'category'),
        Index('ix_expenses_date', 'date'),
    )
    
    def __repr__(self):
        return f"<Expense(id={self.id}, date={self.date}, category={self.category}, amount={self.amount})>"
