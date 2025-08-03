# db/repositories/journal_repository.py

from sqlalchemy.orm import Session
from db.models.journal import JournalEntry
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class JournalRepository:
    def __init__(self, session: Session):
        self.session = session

    def create_entry(self, user_id: int, content: str, mood: str, tags: list = None, insights: list = None):
        """Create a new journal entry"""
        try:
            entry = JournalEntry(
                user_id=user_id,
                content=content,
                mood=mood,
                tags=tags or [],
                insights=insights or []
            )
            self.session.add(entry)
            self.session.flush()  # Get the ID without committing
            return entry
        except Exception as e:
            logger.error(f"Error creating journal entry: {e}")
            raise

    def get_entry_by_id(self, entry_id: int, user_id: int):
        """Get a journal entry by ID for a specific user"""
        return self.session.query(JournalEntry).filter(
            JournalEntry.id == entry_id,
            JournalEntry.user_id == user_id,
            JournalEntry.is_deleted == False
        ).first()

    def get_entries(self, user_id: int, limit: int = 20, offset: int = 0):
        """Get journal entries for a user with pagination"""
        query = self.session.query(JournalEntry).filter(
            JournalEntry.user_id == user_id,
            JournalEntry.is_deleted == False
        ).order_by(JournalEntry.created_at.desc())
        
        total = query.count()
        entries = query.limit(limit).offset(offset).all()
        
        return entries, total

    def update_entry(self, entry_id: int, user_id: int, **kwargs):
        """Update a journal entry"""
        entry = self.get_entry_by_id(entry_id, user_id)
        if not entry:
            return None
            
        for key, value in kwargs.items():
            if hasattr(entry, key) and value is not None:
                setattr(entry, key, value)
        
        entry.updated_at = datetime.utcnow()
        self.session.flush()
        return entry

    def delete_entry(self, entry_id: int, user_id: int):
        """Soft delete a journal entry"""
        entry = self.get_entry_by_id(entry_id, user_id)
        if not entry:
            return False
            
        entry.is_deleted = True
        entry.updated_at = datetime.utcnow()
        self.session.flush()
        return True