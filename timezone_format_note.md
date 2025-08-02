# timezone_format_note.md

# Timezone Format Support

The current implementation stores timezone as a string in the JSON column. The actual timezone parsing and validation would need to be implemented in the notification service that processes these schedules.

## Recommended Timezone Formats

1. **UTC Offset Format** (Recommended - most standard and universal):
   - "UTC+0" (UTC/GMT)
   - "UTC-5" (Eastern Standard Time)
   - "UTC-8" (Pacific Standard Time)
   - "UTC+9" (Japan Standard Time)

2. **Standard Abbreviations** (Optional - familiar but can be ambiguous):
   - "EST" (Eastern Standard Time)
   - "PST" (Pacific Standard Time)
   - "GMT" (Greenwich Mean Time)
   - "JST" (Japan Standard Time)

## Implementation Note

The notification service should:
1. Accept any of these formats
2. Convert them to a standard format internally
3. Handle daylight saving time appropriately
4. Validate timezone strings and reject invalid ones

For now, the database simply stores the timezone string as provided by the user.