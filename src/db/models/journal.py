# models/journal.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, JSON, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base


class JournalEntry(Base):
    __tablename__ = 'journal_entries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, nullable=False)
    content = Column(Text, nullable=False)
    mood = Column(String(10), nullable=False)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # AI-generated fields
    tags = Column(JSON, default=list)
    insights = Column(JSON, default=list)
    processed = Column(Boolean, default=False, nullable=False)
    processing_status = Column(String(20), default='pending', nullable=False)  # pending, processing, completed, failed
    
    # Soft delete
    is_deleted = Column(Boolean, default=False, nullable=False)
    
    def __repr__(self):
        return f"<JournalEntry id={self.id} user_id={self.user_id} mood={self.mood} created_at={self.created_at}>"