# schedule_config_usage_examples.md

# Schedule Configuration Usage Examples

This document shows how to use the `schedule_config` field when scheduling affirmations for specific days and times.

## Schedule Config Structure Reminder

```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly" | "daily" | "custom",
    "notification_type": "push_notification" | "none",
    "private_notification": true | false,
    "time_slots": [
      {
        "time": "HH:MM",
        "days": [0-6],
        "timezone": "timezone_string"
      }
    ]
  }
}
```

**Day Numbers:**
- 0 = Sunday
- 1 = Monday
- 2 = Tuesday
- 3 = Wednesday
- 4 = Thursday
- 5 = Friday
- 6 = Saturday

## Example 1: Only Tuesdays at 8 PM

```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": false,
    "time_slots": [
      {
        "time": "20:00",
        "days": [2],
        "timezone": "UTC-5"
      }
    ]
  }
}
```

## Example 2: Weekend Days at 5 PM

```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": false,
    "time_slots": [
      {
        "time": "17:00",
        "days": [0, 6],
        "timezone": "UTC-5"
      }
    ]
  }
}
```

## Example 3: Monday at 10 AM, 2 PM, and 10 PM

```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": false,
    "time_slots": [
      {
        "time": "10:00",
        "days": [1],
        "timezone": "UTC-5"
      },
      {
        "time": "14:00",
        "days": [1],
        "timezone": "UTC-5"
      },
      {
        "time": "22:00",
        "days": [1],
        "timezone": "UTC-5"
      }
    ]
  }
}
```

## Complete API Request Examples

### 1. Schedule an affirmation for Tuesdays at 8 PM

```bash
POST /affirmations/{affirmation_id}/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": false,
    "time_slots": [
      {
        "time": "20:00",
        "days": [2],
        "timezone": "UTC-5"
      }
    ]
  }
}
```

### 2. Schedule an affirmation for weekends at 5 PM (private notifications)

```bash
POST /affirmations/{affirmation_id}/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": true,
    "time_slots": [
      {
        "time": "17:00",
        "days": [0, 6],
        "timezone": "UTC-8"
      }
    ]
  }
}
```

### 3. Schedule for categorization only (no notifications)

```bash
POST /affirmations/{affirmation_id}/schedule
Authorization: Bearer {token}
Content-Type: application/json

{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "none",
    "private_notification": false,
    "time_slots": [
      {
        "time": "10:00",
        "days": [1],
        "timezone": "UTC+0"
      }
    ]
  }
}
```

## Tips

1. **Time Format**: Always use 24-hour format (HH:MM)
   - 8 AM = "08:00"
   - 2 PM = "14:00"
   - 8 PM = "20:00"
   - 10 PM = "22:00"

2. **Timezone**: 
   - The timezone field is optional but **highly recommended**
   - If not provided, the system will default to UTC
   - Always specify timezone to ensure notifications arrive at the correct local time
   - Timezone format options:
     - UTC offset: "UTC-5", "UTC+0", "UTC+9" (recommended)
     - Standard abbreviations: "EST", "PST", "GMT", "JST"

3. **Multiple Time Slots**: You can have multiple time slots with different days/times in a single schedule

4. **Privacy**: Set `private_notification: true` if you want the notification to show only "You have a notification from PowerManifest" without revealing the affirmation content

5. **Categorization Only**: Set `notification_type: "none"` if you want to use scheduling just for organizing affirmations by time without sending notifications

## Example: Schedule without timezone (defaults to UTC)

```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "notification_type": "push_notification",
    "private_notification": false,
    "time_slots": [
      {
        "time": "20:00",
        "days": [2]
        // timezone omitted - will default to UTC
      }
    ]
  }
}
```

**Note**: If timezone is omitted, 20:00 will be interpreted as 8 PM UTC, which is:
- 3 PM EST (UTC-5)
- 12 PM PST (UTC-8)
- 9 PM CET (UTC+1)

**Common UTC Offsets**:
- New York: UTC-5 (EST) / UTC-4 (EDT during daylight saving)
- Los Angeles: UTC-8 (PST) / UTC-7 (PDT during daylight saving)
- London: UTC+0 (GMT) / UTC+1 (BST during daylight saving)
- Tokyo: UTC+9 (no daylight saving)