# impl/services/affirmations/schedule_affirmation_service.py

import logging
from fastapi import HTTPException, status
from traceback import format_exc
from datetime import datetime, timedelta
import pytz

from models.affirmation.schedule_affirmation200_response import ScheduleAffirmation200Response
from models.affirmation.schedule_config import ScheduleConfig

logger = logging.getLogger(__name__)


class ScheduleAffirmationService:
    """
    Service class for scheduling an affirmation with notification settings.
    """
    
    def __init__(self, request, dependencies):
        self.request = request
        self.dependencies = dependencies
        self.response = None
        
        logger.debug(f"ScheduleAffirmationService initialized for affirmation_id: {request.affirmation_id}")
        
        self._preprocess_request_data()
        self._process_request()
    
    def _get_session(self):
        """Get database session from dependencies."""
        return self.dependencies.session_factory()()
    
    def _verify_ownership(self, affirmation, user_id):
        """Verify that the affirmation belongs to the user."""
        if affirmation.user_id != user_id:
            logger.warning(f"User {user_id} attempted to schedule affirmation {affirmation.id} owned by user {affirmation.user_id}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You don't have permission to schedule this affirmation"
            )
    
    def _create_schedule_config_dict(self, schedule_data):
        """
        Create schedule configuration dictionary to store in JSON column.
        """
        # Convert the schedule request data to a dictionary matching our schema
        schedule_config = {
            "enabled": getattr(schedule_data, 'enabled', True),
            "frequency": getattr(schedule_data, 'frequency', 'daily'),
            "notification_type": getattr(schedule_data, 'notification_type', 'push_notification'),
            "private_notification": getattr(schedule_data, 'private_notification', False),
            "time_slots": []
        }
        
        # Convert time_slots if provided
        if hasattr(schedule_data, 'time_slots') and schedule_data.time_slots:
            for slot in schedule_data.time_slots:
                schedule_config["time_slots"].append({
                    "time": slot.time,
                    "days": slot.days,
                    "timezone": getattr(slot, 'timezone', None) or 'UTC'  # Default to UTC if not provided
                })
        
        return schedule_config
    
    def _preprocess_request_data(self):
        """Validate and set schedule for affirmation."""
        session = self._get_session()
        try:
            # Get the affirmation repository
            affirmation_repo = self.dependencies.affirmation_repository(session=session)
            
            # Fetch the affirmation
            affirmation = affirmation_repo.get_affirmation_by_id(self.request.affirmation_id)
            if not affirmation:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Affirmation not found"
                )
            
            # Verify ownership
            self._verify_ownership(affirmation, self.request.user_id)
            
            # Validate schedule data
            if not hasattr(self.request, 'schedule') or not self.request.schedule:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Schedule configuration is required"
                )
            
            # Create schedule configuration dictionary
            schedule_config = self._create_schedule_config_dict(self.request.schedule)
            
            # Update affirmation with schedule_config JSON
            logger.debug(f"Updating affirmation {self.request.affirmation_id} with schedule_config: {schedule_config}")
            updated_affirmation = affirmation_repo.update_affirmation(
                affirmation_id=self.request.affirmation_id,
                schedule_config=schedule_config
            )
            
            logger.debug(f"Updated affirmation schedule_config: {updated_affirmation.schedule_config}")
            self.schedule_config = schedule_config
            logger.debug(f"Successfully scheduled affirmation {self.request.affirmation_id}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Error scheduling affirmation: {e}\n{format_exc()}")
            raise HTTPException(status_code=500, detail="Failed to schedule affirmation")
        finally:
            session.close()
    
    def _calculate_next_notification(self, schedule_config):
        """Calculate when the next notification should be sent based on the schedule."""
        if not schedule_config.get('enabled') or not schedule_config.get('time_slots'):
            return None
        
        if schedule_config.get('notification_type') == 'none':
            return None
        
        now = datetime.utcnow()
        next_times = []
        
        for slot in schedule_config['time_slots']:
            time_str = slot.get('time', '00:00')
            days = slot.get('days', [])
            timezone_str = slot.get('timezone', 'UTC')
            
            # Parse time
            hour, minute = map(int, time_str.split(':'))
            
            # Handle UTC offset format (e.g., "UTC-5")
            if timezone_str.startswith('UTC'):
                offset_str = timezone_str[3:]
                if offset_str:
                    offset_hours = int(offset_str)
                    # Convert scheduled time to UTC
                    utc_hour = (hour - offset_hours) % 24
                else:
                    utc_hour = hour
            else:
                # Default to UTC if format not recognized
                utc_hour = hour
            
            # Find next occurrence for each day
            for day in days:
                # Calculate days until next occurrence
                current_weekday = now.weekday()  # Monday is 0, Sunday is 6
                target_weekday = (day - 1) % 7  # Convert from our format (0=Sunday) to Python's (0=Monday)
                
                days_ahead = (target_weekday - current_weekday) % 7
                if days_ahead == 0:  # Same day
                    # Check if time has passed
                    target_time = now.replace(hour=utc_hour, minute=minute, second=0, microsecond=0)
                    if target_time <= now:
                        days_ahead = 7  # Next week
                
                next_date = now + timedelta(days=days_ahead)
                next_datetime = next_date.replace(hour=utc_hour, minute=minute, second=0, microsecond=0)
                next_times.append(next_datetime)
        
        # Return the earliest next notification time
        return min(next_times) if next_times else None
    
    def _process_request(self):
        """Build the response with schedule information."""
        # Calculate next notification time
        next_notification = self._calculate_next_notification(self.schedule_config)
        
        self.response = ScheduleAffirmation200Response(
            affirmation_id=str(self.request.affirmation_id),
            next_notification=next_notification
        )