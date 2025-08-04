# here is db/models/user_details.py


from sqlalchemy import (
    create_engine, Column, Integer, String, DateTime, Float, Text,
    ForeignKey, LargeBinary, Boolean, UniqueConstraint, CheckConstraint, or_, func
)
from sqlalchemy.types import JSON
from sqlalchemy.orm import declarative_base, relationship, sessionmaker
from datetime import datetime
import uuid
from werkzeug.security import generate_password_hash

from .base import Base, get_current_time

from typing import Optional, Dict, Any, List



class UserDetails(Base):
    __tablename__ = 'user_details'
    setting_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey('users.user_id'), nullable=False)
    
    # Onboarding fields
    preferred_name = Column(String(100), nullable=True)  # How they want to be addressed
    goals = Column(JSON, default=list)  # List of user's goals from onboarding
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_completed_at = Column(DateTime, nullable=True)
    
    # Preferences and settings
    preferred_language = Column(String(10), default='en', nullable=False)
    timezone = Column(String(50), default='UTC', nullable=False)
    notification_preferences = Column(JSON, default=dict)  # email, push, in-app settings
    
    # Coaching preferences
    coaching_style = Column(String(50), default='balanced')  # supportive, challenging, balanced
    focus_areas = Column(JSON, default=list)  # career, relationships, health, etc.
    preferred_affirmation_style = Column(String(50), default='motivational')
    preferred_affirmation_tone = Column(String(50), default='powerful')
    
    # User state and progress
    current_emotional_state = Column(String(50), nullable=True)  # from latest journal entries
    motivation_level = Column(Integer, default=5)  # 1-10 scale
    last_journal_entry_at = Column(DateTime, nullable=True)
    total_journal_entries = Column(Integer, default=0)
    streak_days = Column(Integer, default=0)  # consecutive days of engagement
    last_activity_at = Column(DateTime, default=get_current_time)
    
    # AI coaching context
    user_context = Column(Text, nullable=True)  # Summary of user's situation for AI
    coaching_notes = Column(JSON, default=list)  # AI-generated insights over time
    
    # Timestamps
    created_at = Column(DateTime, default=get_current_time, nullable=False)
    updated_at = Column(DateTime, default=get_current_time, onupdate=get_current_time, nullable=False)
    
    login_time_logs = relationship(
        "LoginTimeLog",
        back_populates="user_details",
        cascade="all, delete-orphan"
    )
    
    @property
    def last_login_at(self) -> Optional[datetime]:
        """Returns the latest login datetime."""
        if not self.login_time_logs:
            return None
        return max(log.login_datetime for log in self.login_time_logs)
    
    user = relationship("User", back_populates="user_details")
    # user = relationship("User", back_populates="settings")