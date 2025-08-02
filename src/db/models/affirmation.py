# db/models/affirmation.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Text, Boolean, JSON
from sqlalchemy.orm import relationship
from datetime import datetime

from .base import Base

class Affirmation(Base):
    __tablename__ = 'affirmations'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id', ondelete='CASCADE'), nullable=True)
    content = Column(Text, nullable=False)
    category = Column(String(100), nullable=True)
    source = Column(String(50), default='user_created', nullable=True)  # 'ai_generated' or 'user_created'
    is_active = Column(Boolean, default=True, nullable=True)
    voice_enabled = Column(Boolean, default=False, nullable=True)
    voice_id = Column(String(100), nullable=True)
    
    # Schedule configuration stored as JSON
    schedule_config = Column(JSON, nullable=True)
    # Remove the old schedule_config_id as we're storing config directly
    # schedule_config_id = Column(Integer, nullable=True)
    
    last_time_seen = Column(DateTime, nullable=True)
    how_many_times_seen = Column(Integer, default=0, nullable=True)
    last_time_played = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=True)
    
    # Relationship to user
    user = relationship('User', back_populates='affirmations')
    
    def __repr__(self):
        return f"<Affirmation id={self.id} user_id={self.user_id}>"