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
)

from models.extra_models import TokenModel  # noqa: F401
from models.onboarding.process_name_request import ProcessNameRequest
from models.onboarding.process_name_response import ProcessNameResponse
from models.onboarding.process_goals_request import ProcessGoalsRequest
from models.onboarding.process_goals_response import ProcessGoalsResponse
from models.onboarding.complete_response import CompleteResponse
from models.error_response import ErrorResponse
from security_api import get_token_bearerAuth



from core.containers import Services


router = APIRouter()

ns_pkg = impl
for importer, name, ispkg in pkgutil.iter_modules(ns_pkg.__path__, ns_pkg.__name__ + "."):
    importlib.import_module(name)


def get_services(request: Request) -> Services:
    return request.app.state.services


@router.post(
    "/onboarding/process-name",
    responses={
        200: {"model": ProcessNameResponse, "description": "Name processed successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
    tags=["onboarding"],
    summary="Process user input to generate a name",
    response_model_by_alias=True,
)
async def process_name(
    process_name_request: ProcessNameRequest = Body(None),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> ProcessNameResponse:
    """
    Process user input to generate a name during onboarding
    """
    try:
        logger.debug("process_name is called")
        from impl.services.onboarding_service import OnboardingService
        onboarding_service = OnboardingService(services.user_manager, services.db_session, services.openai_client)
        
        return await onboarding_service.process_name(
            user_input=process_name_request.user_input,
            direct=process_name_request.direct,
            user_id=token_bearerAuth.sub
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing name: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/onboarding/process-goals",
    responses={
        200: {"model": ProcessGoalsResponse, "description": "Goals processed successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
    tags=["onboarding"],
    summary="Process user input to generate goals and insights",
    response_model_by_alias=True,
)
async def process_goals(
    process_goals_request: ProcessGoalsRequest = Body(None),
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> ProcessGoalsResponse:
    """
    Process user input to generate goals categories, summary, and insights during onboarding
    """
    try:
        logger.debug("process_goals is called")
        from impl.services.onboarding_service import OnboardingService
        onboarding_service = OnboardingService(services.user_manager, services.db_session, services.openai_client)
        
        return await onboarding_service.process_goals(
            user_input=process_goals_request.user_input,
            user_id=token_bearerAuth.sub
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing goals: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")


@router.post(
    "/onboarding/complete",
    responses={
        200: {"model": CompleteResponse, "description": "Onboarding completed successfully"},
        400: {"model": ErrorResponse, "description": "Bad request"},
    },
    tags=["onboarding"],
    summary="Complete the onboarding process",
    response_model_by_alias=True,
)
async def complete_onboarding(
    token_bearerAuth: TokenModel = Security(
        get_token_bearerAuth
    ),
    services: Services = Depends(get_services),
) -> CompleteResponse:
    """
    Mark the onboarding process as complete for the user
    """
    try:
        logger.debug("complete_onboarding is called")
        from impl.services.onboarding_service import OnboardingService
        onboarding_service = OnboardingService(services.user_manager, services.db_session, services.openai_client)
        
        return await onboarding_service.complete_onboarding(user_id=token_bearerAuth.sub)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing onboarding: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")