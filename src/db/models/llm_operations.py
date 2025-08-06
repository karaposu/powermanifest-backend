# db/models/llm_operations.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base, get_current_time


class LlmOperations(Base):
    __tablename__ = 'llm_operations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=False)
    operation_type = Column(String, nullable=False)  # 'chat_message', 'journal_analysis', 'affirmation_generation'
    usage_data = Column(JSON, nullable=False)  # stores tokens, model, cost, etc.
    created_at = Column(DateTime, default=get_current_time, nullable=False)
    
    # Relationship back to user
    user = relationship('User', backref='llm_operations')
    
    def __repr__(self):
        return f"<LlmOperations id={self.id} user_id={self.user_id} operation={self.operation_type}>"