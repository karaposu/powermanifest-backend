# test_ai_affirmations.sh
#!/bin/bash

# Test AI Affirmation Generation

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# API Base URL
BASE_URL="http://127.0.0.1:8188"

# Test credentials
EMAIL="e@hotmail.com"
PASSWORD="string"

echo -e "${BLUE}Testing AI Affirmation Generation${NC}"
echo "=================================="

# Step 1: Login
echo -e "\n${BLUE}1. Logging in...${NC}"
LOGIN_RESPONSE=$(curl -s -X POST "$BASE_URL/auth/login" \
  -H "Content-Type: application/json" \
  -d "{\"email\": \"$EMAIL\", \"password\": \"$PASSWORD\"}")

TOKEN=$(echo $LOGIN_RESPONSE | grep -o '"token":"[^"]*' | cut -d'"' -f4)

if [ -z "$TOKEN" ]; then
    echo -e "${RED}Failed to login${NC}"
    echo "Response: $LOGIN_RESPONSE"
    exit 1
fi

echo -e "${GREEN}Login successful${NC}"
echo "Token: ${TOKEN:0:20}..."

# Step 2: Create AI Affirmations
echo -e "\n${BLUE}2. Creating AI-generated affirmations...${NC}"

# Test request with context about financial goals
REQUEST_BODY='{
  "context_corpus": "I want to make a million dollars and achieve financial freedom",
  "affirmation_category": "wealth",
  "amount": 5,
  "style": "motivational",
  "uslub": "positive",
  "voice_enabled": false
}'

echo "Request body:"
echo "$REQUEST_BODY" | jq .

RESPONSE=$(curl -s -X POST "$BASE_URL/affirmations/ai-create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

# Check if request was successful
STATUS_CODE=$(curl -s -o /dev/null -w "%{http_code}" -X POST "$BASE_URL/affirmations/ai-create" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "$REQUEST_BODY")

echo -e "\nStatus Code: $STATUS_CODE"

if [ "$STATUS_CODE" = "201" ]; then
    echo -e "${GREEN}Success! AI affirmations created${NC}"
    echo -e "\nResponse:"
    echo "$RESPONSE" | jq .
    
    # Extract and display the affirmations
    echo -e "\n${BLUE}Generated Affirmations:${NC}"
    echo "$RESPONSE" | jq -r '.affirmations[]?.text' | nl
else
    echo -e "${RED}Failed to create AI affirmations${NC}"
    echo "Response: $RESPONSE"
fi

# Step 3: Verify by fetching all affirmations
echo -e "\n${BLUE}3. Fetching all affirmations to verify...${NC}"
ALL_AFFIRMATIONS=$(curl -s -X GET "$BASE_URL/affirmations" \
  -H "Authorization: Bearer $TOKEN")

TOTAL_COUNT=$(echo "$ALL_AFFIRMATIONS" | jq '.count')
echo -e "Total affirmations in database: ${GREEN}$TOTAL_COUNT${NC}"

# Show recent AI-generated affirmations
echo -e "\nRecent affirmations (showing first 5):"
echo "$ALL_AFFIRMATIONS" | jq -r '.affirmations[:5] | .[] | "\(.affirmation_id): \(.text) [\(.source)]"'