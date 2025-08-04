# impl/services/onboarding_service.py
import logging
from datetime import datetime
from traceback import format_exc
from fastapi import HTTPException
from typing import List, Optional

from models.onboarding.process_name_response import ProcessNameResponse
from models.onboarding.process_goals_response import ProcessGoalsResponse
from models.onboarding.complete_response import CompleteResponse

logger = logging.getLogger(__name__)


class OnboardingService:
    """Service for handling user onboarding"""
    
    def __init__(self, dependencies):
        self.dependencies = dependencies
        logger.debug("OnboardingService initialized")
    
    def _open_session(self):
        """Return a fresh SQLAlchemy Session object."""
        session_factory = self.dependencies.session_factory()
        return session_factory()
    
    def process_name(self, preferred_name: str, user_id: int):
        """Process and save user's preferred name"""
        logger.debug(f"Processing name for user_id={user_id}")
        
        if not preferred_name or not preferred_name.strip():
            raise HTTPException(status_code=400, detail="Name is required")
        
        user_repo_provider = self.dependencies.user_repository
        session = self._open_session()
        
        try:
            user_repo = user_repo_provider(session=session)
            
            # Verify user exists
            from db.models.user import User
            user = session.query(User).filter_by(user_id=user_id).first()
            if not user:
                raise HTTPException(status_code=404, detail="User not found")
            
            # Get or create UserDetails
            from db.models.user_details import UserDetails
            user_details = session.query(UserDetails).filter_by(user_id=user_id).first()
            
            if not user_details:
                user_details = UserDetails(user_id=user_id)
                session.add(user_details)
            
            # Update preferred name
            user_details.preferred_name = preferred_name.strip()
            user_details.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Updated preferred name for user {user_id}")
            
            return ProcessNameResponse(
                success=True,
                message=f"Nice to meet you, {preferred_name}!"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing name: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to process name")
        finally:
            session.close()
    
    def process_goals(self, goals: List[str], user_id: int):
        """Process and save user's goals"""
        logger.debug(f"Processing goals for user_id={user_id}")
        
        if not goals or len(goals) == 0:
            raise HTTPException(status_code=400, detail="At least one goal is required")
        
        # Clean and validate goals
        cleaned_goals = [goal.strip() for goal in goals if goal and goal.strip()]
        if not cleaned_goals:
            raise HTTPException(status_code=400, detail="At least one valid goal is required")
        
        session = self._open_session()
        
        try:
            # Get user details
            from db.models.user_details import UserDetails
            user_details = session.query(UserDetails).filter_by(user_id=user_id).first()
            
            if not user_details:
                raise HTTPException(status_code=404, detail="User details not found. Please complete name step first.")
            
            # Update goals
            user_details.goals = cleaned_goals
            user_details.updated_at = datetime.utcnow()
            
            # Generate AI coaching context based on goals
            goals_text = ", ".join(cleaned_goals)
            user_details.user_context = f"User's primary goals: {goals_text}"
            
            session.commit()
            logger.info(f"Updated goals for user {user_id}: {cleaned_goals}")
            
            return ProcessGoalsResponse(
                success=True,
                message="Your goals have been saved successfully!",
                goalsSummary=f"You're working on: {goals_text}"
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error processing goals: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to process goals")
        finally:
            session.close()
    
    def complete_onboarding(self, user_id: int):
        """Mark onboarding as complete"""
        logger.debug(f"Completing onboarding for user_id={user_id}")
        
        session = self._open_session()
        
        try:
            # Get user details
            from db.models.user_details import UserDetails
            user_details = session.query(UserDetails).filter_by(user_id=user_id).first()
            
            if not user_details:
                raise HTTPException(status_code=404, detail="User details not found")
            
            # Check if required fields are filled
            if not user_details.preferred_name:
                raise HTTPException(status_code=400, detail="Please complete the name step first")
            
            if not user_details.goals or len(user_details.goals) == 0:
                raise HTTPException(status_code=400, detail="Please complete the goals step first")
            
            # Mark onboarding as complete
            user_details.onboarding_completed = True
            user_details.onboarding_completed_at = datetime.utcnow()
            user_details.updated_at = datetime.utcnow()
            
            session.commit()
            logger.info(f"Completed onboarding for user {user_id}")
            
            # Build welcome message
            name = user_details.preferred_name
            goals_count = len(user_details.goals)
            
            return CompleteResponse(
                success=True,
                message=f"Welcome aboard, {name}! Your journey begins now.",
                nextSteps=[
                    "Start journaling to track your progress",
                    "Create your first affirmations",
                    "Explore AI coaching sessions"
                ],
                userId=str(user_id)
            )
            
        except HTTPException:
            raise
        except Exception as e:
            session.rollback()
            logger.error(f"Error completing onboarding: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Unable to complete onboarding")
        finally:
            session.close()
    
    def get_onboarding_status(self, user_id: int) -> dict:
        """Get the current onboarding status for a user"""
        session = self._open_session()
        
        try:
            from db.models.user_details import UserDetails
            user_details = session.query(UserDetails).filter_by(user_id=user_id).first()
            
            if not user_details:
                return {
                    "completed": False,
                    "steps_completed": [],
                    "next_step": "name"
                }
            
            steps_completed = []
            next_step = None
            
            if user_details.preferred_name:
                steps_completed.append("name")
            else:
                next_step = "name"
            
            if user_details.goals and len(user_details.goals) > 0:
                steps_completed.append("goals")
            elif user_details.preferred_name and not next_step:
                next_step = "goals"
            
            if user_details.onboarding_completed:
                steps_completed.append("complete")
            elif len(steps_completed) == 2 and not next_step:
                next_step = "complete"
            
            return {
                "completed": user_details.onboarding_completed,
                "steps_completed": steps_completed,
                "next_step": next_step,
                "preferred_name": user_details.preferred_name,
                "goals": user_details.goals or []
            }
            
        except Exception as e:
            logger.error(f"Error getting onboarding status: {e}")
            return {
                "completed": False,
                "steps_completed": [],
                "next_step": "name"
            }
        finally:
            session.close()