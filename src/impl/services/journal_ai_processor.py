# impl/services/journal_ai_processor.py
import logging
from traceback import format_exc

logger = logging.getLogger(__name__)


def process_journal_with_ai(entry_id: int, user_id: int, services):
    """Background task to process journal entry with AI"""
    logger.info(f"Starting AI processing for entry {entry_id}")
    
    # Open a new session for background task
    session_factory = services.session_factory()
    session = session_factory()
    
    try:
        # Get the repository
        journal_repo = services.journal_repository(session=session)
        
        # Get the entry
        entry = journal_repo.get_entry_by_id(entry_id, user_id)
        if not entry:
            logger.error(f"Entry {entry_id} not found")
            return
        
        # Update status to processing
        entry.processing_status = 'processing'
        session.commit()
        
        # Call LLM service to analyze the entry
        from impl.myllmservice import MyLLMService
        llm_service = MyLLMService()
        
        result = llm_service.analyze_journal_entry(
            content=entry.content,
            mood=entry.mood
        )
        
        if result.success:
            insights = result.content
        else:
            logger.error(f"LLM analysis failed: {result.error_message}")
            raise Exception(f"LLM analysis failed: {result.error_message}")
        
        # Update entry with results
        entry.insights = insights
        entry.tags = insights.get("tags", [])
        entry.processed = True
        entry.processing_status = 'completed'
        
        session.commit()
        logger.info(f"Successfully processed entry {entry_id}")
        
    except Exception as e:
        logger.error(f"Error processing entry {entry_id}: {e}\n{format_exc()}")
        # Mark as failed
        try:
            entry.processing_status = 'failed'
            session.commit()
        except:
            pass
    finally:
        session.close()