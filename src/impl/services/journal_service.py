# This is a clean version of journal_service.py with only the necessary methods
# Copy this content to replace the existing journal_service.py

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
    
    def create_entry(self, content: str, mood: str, user_id: int, timestamp: datetime = None, 
                     auto_process: bool = True, background_tasks=None, services=None):
        """Create a new journal entry"""
        logger.debug(f"Creating journal entry for user_id={user_id}, auto_process={auto_process}")
        
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
            
            # Automatically trigger AI processing if requested
            logger.info(f"Auto-process check: auto_process={auto_process}, background_tasks={background_tasks is not None}, services={services is not None}")
            if auto_process and background_tasks and services:
                logger.info(f"Auto-processing journal entry {entry.id}")
                # Mark as queued for processing
                entry.processing_status = 'processing'
                session.commit()
                
                # Add to background tasks
                from impl.services.journal_ai_processor import process_journal_with_ai
                background_tasks.add_task(
                    process_journal_with_ai,
                    entry_id=entry.id,
                    user_id=user_id,
                    services=services
                )
            else:
                logger.info(f"NOT auto-processing: auto_process={auto_process}, has_background_tasks={background_tasks is not None}, has_services={services is not None}")
            
            # Convert to response model
            # Handle insights - if it's a dict (from AI processing), extract relevant values
            insights_list = []
            if entry.insights:
                if isinstance(entry.insights, dict):
                    # Extract key insights from the AI-generated dict
                    if 'emotionalState' in entry.insights:
                        insights_list.append(f"Emotional state: {entry.insights['emotionalState']}")
                    if 'themes' in entry.insights:
                        for theme in entry.insights['themes']:
                            insights_list.append(f"Theme: {theme}")
                elif isinstance(entry.insights, list):
                    insights_list = entry.insights
            
            return JournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                content=entry.content,
                mood=entry.mood,
                timestamp=entry.created_at,
                tags=entry.tags,
                insights=insights_list,
                suggestionsAvailable=bool(entry.processed and entry.insights),
                processed=entry.processed,
                processingStatus=entry.processing_status
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
                # Handle insights - if it's a dict (from AI processing), extract relevant values
                insights_list = []
                if entry.insights:
                    if isinstance(entry.insights, dict):
                        # Extract key insights from the AI-generated dict
                        if 'emotionalState' in entry.insights:
                            insights_list.append(f"Emotional state: {entry.insights['emotionalState']}")
                        if 'themes' in entry.insights:
                            for theme in entry.insights['themes']:
                                insights_list.append(f"Theme: {theme}")
                    elif isinstance(entry.insights, list):
                        insights_list = entry.insights
                
                preview = JournalEntryPreview(
                    id=str(entry.id),
                    content=entry.content[:200] if len(entry.content) > 200 else entry.content,
                    mood=entry.mood,
                    timestamp=entry.created_at,
                    tags=entry.tags,
                    insights=insights_list,
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
    
    def get_entry(self, entry_id: int, user_id: int):
        """Get a specific journal entry"""
        logger.debug(f"Getting journal entry id={entry_id} for user_id={user_id}")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Get entry from repository
            entry = journal_repo.get_entry_by_id(
                entry_id=int(entry_id),
                user_id=user_id
            )
            
            if not entry:
                raise HTTPException(status_code=404, detail="Journal entry not found")
            
            # Convert to response model
            # Handle insights - if it's a dict (from AI processing), extract relevant values
            insights_list = []
            if entry.insights:
                if isinstance(entry.insights, dict):
                    # Extract key insights from the AI-generated dict
                    if 'emotionalState' in entry.insights:
                        insights_list.append(f"Emotional state: {entry.insights['emotionalState']}")
                    if 'themes' in entry.insights:
                        for theme in entry.insights['themes']:
                            insights_list.append(f"Theme: {theme}")
                elif isinstance(entry.insights, list):
                    insights_list = entry.insights
            
            return JournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                content=entry.content,
                mood=entry.mood,
                timestamp=entry.created_at,
                tags=entry.tags,
                insights=insights_list,
                suggestionsAvailable=bool(entry.processed and entry.insights),
                processed=entry.processed,
                processingStatus=entry.processing_status
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error getting journal entry: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to get journal entry")
        finally:
            session.close()
    
    def process_entry(self, entry_id: int, user_id: int, background_tasks, services):
        """Queue journal entry for AI processing"""
        logger.debug(f"Queueing journal entry id={entry_id} for AI processing")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Get entry to verify it exists and belongs to user
            entry = journal_repo.get_entry_by_id(
                entry_id=int(entry_id),
                user_id=user_id
            )
            
            if not entry:
                raise HTTPException(status_code=404, detail="Journal entry not found")
            
            # Check if already processed or processing
            if entry.processing_status == 'completed':
                logger.info(f"Entry {entry_id} already processed")
                status_message = "Entry has already been processed"
            elif entry.processing_status == 'processing':
                logger.info(f"Entry {entry_id} is currently being processed")
                status_message = "Entry is currently being processed"
            else:
                # Mark as queued for processing
                entry.processing_status = 'processing'
                session.commit()
                
                # Add to background tasks
                from impl.services.journal_ai_processor import process_journal_with_ai
                background_tasks.add_task(
                    process_journal_with_ai,
                    entry_id=entry_id,
                    user_id=user_id,
                    services=services
                )
                
                status_message = "Entry queued for AI processing"
                logger.info(f"Entry {entry_id} queued for processing")
            
            # Return response
            from models.journal.process_entry_response import ProcessEntryResponse
            return ProcessEntryResponse(
                insights={
                    "status": entry.processing_status,
                    "message": status_message,
                    "tags": entry.tags if entry.processed else [],
                    "emotionalState": entry.insights.get("emotionalState") if entry.processed and isinstance(entry.insights, dict) else None,
                    "themes": entry.insights.get("themes", []) if entry.processed and isinstance(entry.insights, dict) else [],
                    "suggestedActions": entry.insights.get("suggestedActions", []) if entry.processed and isinstance(entry.insights, dict) else []
                }
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error queueing journal entry for processing: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to queue journal entry for processing")
        finally:
            session.close()
    
    def update_entry(self, entry_id: int, content: str, mood: str, user_id: int):
        """Update a journal entry"""
        logger.debug(f"Updating journal entry id={entry_id} for user_id={user_id}")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Update the entry
            entry = journal_repo.update_entry(
                entry_id=int(entry_id),
                user_id=user_id,
                content=content,
                mood=mood
            )
            
            if not entry:
                raise HTTPException(status_code=404, detail="Journal entry not found")
            
            # Reset processing status since content changed
            entry.processed = False
            entry.processing_status = 'pending'
            entry.insights = []
            entry.tags = []
            
            session.commit()
            logger.debug(f"Journal entry updated (id={entry.id})")
            
            # Convert to response model
            return JournalEntry(
                id=str(entry.id),
                userId=str(entry.user_id),
                content=entry.content,
                mood=entry.mood,
                timestamp=entry.created_at,
                tags=entry.tags,
                insights=[],
                suggestionsAvailable=False,
                processed=entry.processed,
                processingStatus=entry.processing_status
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error updating journal entry: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to update journal entry")
        finally:
            session.close()
    
    def delete_entry(self, entry_id: int, user_id: int):
        """Delete a journal entry (soft delete)"""
        logger.debug(f"Deleting journal entry id={entry_id} for user_id={user_id}")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Delete the entry (soft delete)
            success = journal_repo.delete_entry(
                entry_id=int(entry_id),
                user_id=user_id
            )
            
            if not success:
                raise HTTPException(status_code=404, detail="Journal entry not found")
            
            session.commit()
            logger.debug(f"Journal entry deleted (id={entry_id})")
            
            # Return response
            from models.journal.delete_entry_response import DeleteEntryResponse
            return DeleteEntryResponse(
                message="Entry deleted successfully",
                entryId=str(entry_id)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error deleting journal entry: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to delete journal entry")
        finally:
            session.close()
    
    def create_affirmation_from_entry(self, entry_id: int, style: str, tone: str, user_id: int):
        """Create affirmations based on journal entry content"""
        logger.debug(f"Creating affirmation from journal entry id={entry_id}")
        
        journal_repo_provider = self.dependencies.journal_repository
        session = self._open_session()
        
        try:
            journal_repo = journal_repo_provider(session=session)
            
            # Get the entry
            entry = journal_repo.get_entry_by_id(
                entry_id=int(entry_id),
                user_id=user_id
            )
            
            if not entry:
                raise HTTPException(status_code=404, detail="Journal entry not found")
            
            # Check if entry has been processed
            if not entry.processed or not entry.insights:
                raise HTTPException(
                    status_code=400, 
                    detail="Entry must be processed before creating affirmations"
                )
            
            # Prepare context from entry and insights
            context_parts = [f"Journal entry: {entry.content}"]
            
            if isinstance(entry.insights, dict):
                if 'emotionalState' in entry.insights:
                    context_parts.append(f"Emotional state: {entry.insights['emotionalState']}")
                if 'themes' in entry.insights:
                    context_parts.append(f"Themes: {', '.join(entry.insights['themes'])}")
                if 'suggestedActions' in entry.insights:
                    context_parts.append(f"Suggested focus areas: {', '.join(entry.insights['suggestedActions'])}")
            
            context = " | ".join(context_parts)
            
            # Generate affirmations using LLM service
            from impl.myllmservice import MyLLMService
            llm_service = MyLLMService()
            
            result = llm_service.generate_affirmations_with_llm(
                context=context,
                count=5,
                style=style,
                uslub=tone
            )
            
            if not result.success:
                logger.error(f"LLM affirmation generation failed: {result.error_message}")
                raise HTTPException(status_code=500, detail="Failed to generate affirmations")
            
            # Extract affirmation content
            affirmations = result.content if isinstance(result.content, list) else []
            
            # Return response
            from models.journal.create_affirmation_response import CreateAffirmationResponse
            return CreateAffirmationResponse(
                affirmations=[aff.get('content', aff) if isinstance(aff, dict) else str(aff) for aff in affirmations],
                style=style,
                tone=tone
            )
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error creating affirmation from entry: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to create affirmation")
        finally:
            session.close()
    
    # Placeholder methods for unimplemented features
    def get_suggestions(self, entry_id: int, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def create_script_from_entry(self, entry_id: int, duration: int, type: str, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def start_coach_session_from_entry(self, entry_id: int, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def get_stats(self, period: str, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def search_entries(self, query: str, mood: str, tags: list, date_from, date_to, limit: int, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def get_patterns(self, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def export_entries(self, format: str, date_from, date_to, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")
    
    def batch_tag_management(self, action: str, entry_ids: list, tags: list, user_id: int):
        raise HTTPException(status_code=501, detail="Not implemented")