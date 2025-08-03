# impl/services/journal_service.py
import logging
from datetime import datetime
from traceback import format_exc
from fastapi import HTTPException

from models.journal.journal_entry import JournalEntry
from models.journal.get_entries_response import GetEntriesResponse
from models.journal.journal_entry_preview import JournalEntryPreview

logger = logging.getLogger(__name__)


class JournalService:
    """Service for handling journal operations"""
    
    def __init__(self, dependencies):
        self.dependencies = dependencies
        logger.debug("JournalService initialized")
    
    def _open_session(self):
        """Return a fresh SQLAlchemy Session object."""
        session_factory = self.dependencies.session_factory()
        return session_factory()
    
    def create_entry(self, content: str, mood: str, user_id: int, timestamp: datetime = None):
        """Create a new journal entry"""
        logger.debug(f"Creating journal entry for user_id={user_id}")
        
        if not content or not mood:
            raise HTTPException(status_code=400, detail="Content and mood are required")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Create the entry
            entry = journal_repo.create_entry(
                user_id=user_id,
                content=content,
                mood=mood
            )
            
            session.commit()
            logger.debug(f"Journal entry created (id={entry.id})")
            
            # Convert to response model
            return JournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                content=entry.content,
                mood=entry.mood,
                timestamp=entry.created_at,
                tags=entry.tags,
                insights=entry.insights,
                suggestionsAvailable=False
            )
            
        except Exception as e:
            session.rollback()
            logger.error(f"Error creating journal entry: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to create journal entry")
        finally:
            session.close()
    
    def get_entries(self, user_id: int, filter: str = None, limit: int = 20, 
                    offset: int = 0, search: str = None):
        """Get journal entries with filtering"""
        logger.debug(f"Getting journal entries for user_id={user_id}")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Get entries from repository
            entries, total = journal_repo.get_entries(
                user_id=user_id,
                limit=limit,
                offset=offset
            )
            
            # Convert to preview models
            entry_previews = []
            for entry in entries:
                preview = JournalEntryPreview(
                    id=str(entry.id),
                    content=entry.content[:200] if len(entry.content) > 200 else entry.content,
                    mood=entry.mood,
                    timestamp=entry.created_at,
                    tags=entry.tags,
                    hasAffirmation=False,
                    hasScript=False
                )
                entry_previews.append(preview)
            
            # Build response
            return GetEntriesResponse(
                entries=entry_previews,
                total=total,
                hasMore=(offset + limit) < total
            )
            
        except Exception as e:
            logger.error(f"Error getting journal entries: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to get journal entries")
        finally:
            session.close()