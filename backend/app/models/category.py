"""Category model definition"""

from sqlalchemy import Column, String, Boolean, Text, DateTime, Index
from sqlalchemy.sql import func
from app.database import Base


class Category(Base):
    """Category model for storing budget categories"""
    
    __tablename__ = "categories"
    
    id = Column(String(50), primary_key=True, comment="Immutable category ID (snake_case)")
    name = Column(String(100), nullable=False, comment="Display name in Japanese")
    type = Column(String(20), nullable=False, comment="Category type: fixed, variable, lifestyle, event")
    is_active = Column(Boolean, nullable=False, default=True, comment="Active flag")
    note = Column(Text, nullable=True, comment="Additional notes")
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    
    # Indexes
    __table_args__ = (
        Index('ix_categories_type', 'type'),
        Index('ix_categories_is_active', 'is_active'),
    )
    
    def __repr__(self):
        return f"<Category(id={self.id}, name={self.name}, type={self.type}, is_active={self.is_active})>"
