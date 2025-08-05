# coding: utf-8

from typing import Dict, List  # noqa: F401
import importlib
import pkgutil
import logging

logger = logging.getLogger(__name__)

import impl

from fastapi import (  # noqa: F401
    APIRouter,
    Body,
    Cookie,
    Depends,
    Form,
    Header,
    HTTPException,
    Path,
    Query,
    Request,
    Response,
    Security,
    status,
    BackgroundTasks,
)

from models.extra_models import TokenModel  # noqa: F401
from models.journal.create_journal_entry_request import CreateJournalEntryRequest
from models.journal.journal_entry import JournalEntry
from models.journal.journal_entry_preview import JournalEntryPreview
from models.journal.journal_entry_detail import JournalEntryDetail
from models.journal.update_journal_entry_request import UpdateJournalEntryRequest
from models.journal.process_entry_response import ProcessEntryResponse
from models.journal.suggestions_response import SuggestionsResponse
from models.journal.create_affirmation_request import CreateAffirmationRequest
from models.journal.create_affirmation_response import CreateAffirmationResponse
from models.journal.create_script_request import CreateScriptRequest
from models.journal.create_script_response import CreateScriptResponse
from models.journal.start_coach_session_response import StartCoachSessionResponse
from models.journal.journal_stats import JournalStats
from models.journal.search_results import SearchResults
from models.journal.journal_patterns import JournalPatterns
from models.journal.export_response import ExportResponse
from models.journal.batch_tag_request import BatchTagRequest
from models.journal.batch_tag_response import BatchTagResponse
from models.journal.delete_entry_response import DeleteEntryResponse
from models.journal.get_entries_response import GetEntriesResponse
from models.error_response import ErrorResponse
from security_api import get_token_bearerAuth
from core.containers import Services
from datetime import date
from typing import Optional, List as ListType


router = APIRouter()

ns_pkg = impl
for importer, name, ispkg in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


def get_services(request: Request) -> Services:
    return request.app.state.services


@router.post(
    "/journal/entries",
    responses={
        201: {"model": JournalEntry, "description": "Entry created successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Journal Entries"],
    summary="Create a new journal entry",
    response_model_by_alias=True,
)
async def create_journal_entry(
    background_tasks: BackgroundTasks,
    create_journal_entry_request: CreateJournalEntryRequest = Body(None),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
    request: Request = None,
) -> JournalEntry:
    """Create a new journal entry"""
    try:
        logger.debug("------create_journal_entry is called")
        
        # Log all incoming data
        if request:
            logger.debug(f"Request headers: {dict(request.headers)}")
            logger.debug(f"Authorization header: {request.headers.get('authorization', 'NOT PROVIDED')}")
        
        logger.debug(f"Token info: {token_bearerAuth if token_bearerAuth else 'NO TOKEN'}")
        if token_bearerAuth:
            logger.debug(f"Token sub (user_id): {token_bearerAuth.sub}")
            logger.debug(f"Token exp: {getattr(token_bearerAuth, 'exp', 'No exp')}")
        
        logger.debug(f"Request body: {create_journal_entry_request}")
        
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.create_entry(
            content=create_journal_entry_request.content,
            mood=create_journal_entry_request.mood,
            timestamp=create_journal_entry_request.timestamp,
            user_id=int(token_bearerAuth.sub),
            auto_process=create_journal_entry_request.autoProcess if create_journal_entry_request.autoProcess is not None else True,
            background_tasks=background_tasks,
            services=services
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating journal entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/journal/entries",
    responses={
        200: {"model": GetEntriesResponse, "description": "List of journal entries"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Journal Entries"],
    summary="Get journal entries with filtering",
    response_model_by_alias=True,
)
async def get_journal_entries(
    filter: Optional[str] = Query(None, description="Time-based filter", alias="filter"),
    limit: int = Query(20, description="Number of entries to return", le=100),
    offset: int = Query(0, description="Number of entries to skip", ge=0),
    search: Optional[str] = Query(None, description="Search query for entry content"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> GetEntriesResponse:
    """Get journal entries with filtering"""
    try:
        logger.debug("get_journal_entries is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.get_entries(
            filter=filter,
            limit=limit,
            offset=offset,
            search=search,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting journal entries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/journal/entries/{entryId}",
    responses={
        200: {"model": JournalEntryDetail, "description": "Journal entry details"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Journal Entries"],
    summary="Get a specific journal entry",
    response_model_by_alias=True,
)
async def get_journal_entry(
    entryId: str = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> JournalEntry:
    """Get a specific journal entry"""
    try:
        logger.debug("get_journal_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.get_entry(
            entry_id=entryId,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting journal entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.patch(
    "/journal/entries/{entryId}",
    responses={
        200: {"model": JournalEntry, "description": "Updated entry"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Journal Entries"],
    summary="Update a journal entry",
    response_model_by_alias=True,
)
async def update_journal_entry(
    entryId: str = Path(..., description=""),
    update_journal_entry_request: UpdateJournalEntryRequest = Body(None),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> JournalEntry:
    """Update a journal entry"""
    try:
        logger.debug("update_journal_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.update_entry(
            entry_id=entryId,
            content=update_journal_entry_request.content,
            mood=update_journal_entry_request.mood,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.delete(
    "/journal/entries/{entryId}",
    responses={
        200: {"model": DeleteEntryResponse, "description": "Entry deleted successfully"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Journal Entries"],
    summary="Delete a journal entry",
    response_model_by_alias=True,
)
async def delete_journal_entry(
    entryId: str = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> DeleteEntryResponse:
    """Delete a journal entry"""
    try:
        logger.debug("delete_journal_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.delete_entry(
            entry_id=entryId,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/journal/entries/{entryId}/process",
    responses={
        200: {"model": ProcessEntryResponse, "description": "AI processing results"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["AI Processing"],
    summary="Process journal entry with AI",
    response_model_by_alias=True,
)
async def process_journal_entry(
    background_tasks: BackgroundTasks,
    entryId: str = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> ProcessEntryResponse:
    """Process journal entry with AI"""
    try:
        logger.debug("process_journal_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.process_entry(
            entry_id=entryId,
            user_id=int(token_bearerAuth.sub),
            background_tasks=background_tasks,
            services=services
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing journal entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/journal/entries/{entryId}/suggestions",
    responses={
        200: {"model": SuggestionsResponse, "description": "AI suggestions"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["AI Processing"],
    summary="Get AI suggestions for entry",
    response_model_by_alias=True,
)
async def get_entry_suggestions(
    entryId: str = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> SuggestionsResponse:
    """Get AI suggestions for entry"""
    try:
        logger.debug("get_entry_suggestions is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.get_suggestions(
            entry_id=entryId,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting entry suggestions: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/journal/entries/{entryId}/create-affirmation",
    responses={
        201: {"model": CreateAffirmationResponse, "description": "Affirmation created"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["AI Actions"],
    summary="Create affirmation from journal entry",
    response_model_by_alias=True,
)
async def create_affirmation_from_entry(
    entryId: str = Path(..., description=""),
    create_affirmation_request: CreateAffirmationRequest = Body(None),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> CreateAffirmationResponse:
    """Create affirmation from journal entry"""
    try:
        logger.debug("create_affirmation_from_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.create_affirmation_from_entry(
            entry_id=entryId,
            style=create_affirmation_request.style,
            tone=create_affirmation_request.tone,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating affirmation from entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/journal/entries/{entryId}/start-coach-session",
    responses={
        201: {"model": StartCoachSessionResponse, "description": "Coach session started"},
        404: {"model": ErrorResponse, "description": "Not found"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["AI Actions"],
    summary="Start AI coach session from journal entry context",
    response_model_by_alias=True,
)
async def start_coach_session_from_entry(
    entryId: str = Path(..., description=""),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> StartCoachSessionResponse:
    """Start AI coach session from journal entry context"""
    try:
        logger.debug("start_coach_session_from_entry is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.start_coach_session_from_entry(
            entry_id=entryId,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error starting coach session from entry: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/journal/stats",
    responses={
        200: {"model": JournalStats, "description": "Journal statistics"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Analytics"],
    summary="Get journal statistics",
    response_model_by_alias=True,
)
async def get_journal_stats(
    period: Optional[str] = Query("month", description="Time period", alias="period"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> JournalStats:
    """Get journal statistics"""
    try:
        logger.debug("get_journal_stats is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.get_stats(
            period=period,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting journal stats: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.get(
    "/journal/search",
    responses={
        200: {"model": SearchResults, "description": "Search results"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Search"],
    summary="Search journal entries",
    response_model_by_alias=True,
)
async def search_journal_entries(
    q: str = Query(..., description="Search query"),
    mood: Optional[str] = Query(None, description="Filter by mood"),
    tags: Optional[ListType[str]] = Query(None, description="Filter by tags"),
    dateFrom: Optional[date] = Query(None, description="Start date", alias="dateFrom"),
    dateTo: Optional[date] = Query(None, description="End date", alias="dateTo"),
    limit: Optional[int] = Query(20, description="Number of results"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> SearchResults:
    """Search journal entries"""
    try:
        logger.debug("search_journal_entries is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.search_entries(
            query=q,
            mood=mood,
            tags=tags,
            date_from=dateFrom,
            date_to=dateTo,
            limit=limit,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error searching journal entries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")





@router.get(
    "/journal/export",
    responses={
        200: {"model": ExportResponse, "description": "Export details"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
    },
    tags=["Export"],
    summary="Export journal entries",
    response_model_by_alias=True,
)

async def export_journal_entries(
    format: str = Query(..., description="Export format"),
    dateFrom: Optional[date] = Query(None, description="Start date", alias="dateFrom"),
    dateTo: Optional[date] = Query(None, description="End date", alias="dateTo"),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> ExportResponse:
    """Export journal entries"""
    try:
        logger.debug("export_journal_entries is called")
        from impl.services.journal_service import JournalService
        journal_service = JournalService(dependencies=services)
        
        return journal_service.export_entries(
            format=format,
            date_from=dateFrom,
            date_to=dateTo,
            user_id=int(token_bearerAuth.sub)
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting journal entries: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")

