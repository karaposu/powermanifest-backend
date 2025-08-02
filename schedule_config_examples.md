# schedule_config_examples.md

# Updated Schedule Configuration Examples

## New Fields Explanation:

1. **`notification_type`** (string): How to handle notifications
   - `"push_notification"`: Send push notifications at scheduled times
   - `"none"`: Only use scheduling for categorization, no notifications sent

2. **`private_notification`** (boolean): Privacy setting for push notifications
   - `true`: Notification shows "You have a notification from PowerManifest" (content hidden)
   - `false`: Notification shows the actual affirmation text

## Example Configurations:

### 1. Daily morning affirmation with visible content:
```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "daily",
    "time_slots": [
      {
        "time": "08:00",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "America/New_York"
      }
    ],
    "notification_type": "push_notification",
    "private_notification": false
  }
}
```

### 2. Private notifications (content hidden):
```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "daily",
    "time_slots": [
      {
        "time": "09:00",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "America/Los_Angeles"
      }
    ],
    "notification_type": "push_notification",
    "private_notification": true
  }
}
```

### 3. Schedule for categorization only (no notifications):
```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "time_slots": [
      {
        "time": "07:00",
        "days": [1, 3, 5],
        "timezone": "Europe/London"
      }
    ],
    "notification_type": "none",
    "private_notification": false
  }
}
```

### 4. Multiple daily reminders with privacy:
```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "daily",
    "time_slots": [
      {
        "time": "06:00",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "Asia/Tokyo"
      },
      {
        "time": "12:00",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "Asia/Tokyo"
      },
      {
        "time": "18:00",
        "days": [0, 1, 2, 3, 4, 5, 6],
        "timezone": "Asia/Tokyo"
      }
    ],
    "notification_type": "push_notification",
    "private_notification": true
  }
}
```

### 5. Weekday work affirmations (visible):
```json
{
  "schedule_config": {
    "enabled": true,
    "frequency": "weekly",
    "time_slots": [
      {
        "time": "08:30",
        "days": [1, 2, 3, 4, 5],
        "timezone": "America/Chicago"
      }
    ],
    "notification_type": "push_notification",
    "private_notification": false
  }
}
```

### 6. Disabled schedule:
```json
{
  "schedule_config": {
    "enabled": false,
    "frequency": "daily",
    "time_slots": [],
    "notification_type": "none",
    "private_notification": false
  }
}
```

## Use Cases:

1. **Public Affirmations**: Set `private_notification: false` for motivational quotes that can be shown in notifications
2. **Private Affirmations**: Set `private_notification: true` for personal/sensitive affirmations
3. **Time-based Categorization**: Set `notification_type: "none"` to group affirmations by time without sending notifications
4. **Mixed Privacy**: Different affirmations can have different privacy settings based on their content sensitivity