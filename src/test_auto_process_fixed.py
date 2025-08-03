#!/usr/bin/env python3
import requests
import time
import json

BASE_URL = "http://0.0.0.0:8188"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzU0Mzk2NjAwfQ._q75dnkD9zIzu1-Zu3htF_zQuT_r63IPuxC5rC_Wk0M"

headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

print("=" * 80)
print("TEST: Auto-processing with fixed parameter order")
print("=" * 80)

# Create entry with auto-processing (default behavior)
response = requests.post(
    f"{BASE_URL}/journal/entries",
    headers=headers,
    json={
        "content": "Today I completed a challenging project at work and learned new skills. Feeling accomplished!",
        "mood": "🎉"
    }
)

if response.status_code == 200:
    entry = response.json()
    print(f"\n✅ Created entry {entry.get('id')}:")
    print(f"  - processed: {entry.get('processed')}")
    print(f"  - processingStatus: {entry.get('processingStatus')}")
    
    # Wait for processing
    print("\n⏳ Waiting 5 seconds for AI processing...")
    time.sleep(5)
    
    # Check if it was processed
    get_response = requests.get(
        f"{BASE_URL}/journal/entries/{entry.get('id')}",
        headers=headers
    )
    
    if get_response.status_code == 200:
        processed_entry = get_response.json()
        print(f"\n📊 Entry {entry.get('id')} after waiting:")
        print(f"  - processed: {processed_entry.get('processed')}")
        print(f"  - processingStatus: {processed_entry.get('processingStatus')}")
        print(f"  - tags: {processed_entry.get('tags')}")
        print(f"  - insights: {processed_entry.get('insights')}")
        
        if processed_entry.get('processingStatus') == 'completed':
            print("\n✅ SUCCESS: Auto-processing is working!")
        else:
            print("\n❌ ISSUE: Auto-processing did not complete")
    else:
        print(f"❌ Failed to get entry: {get_response.text}")
else:
    print(f"❌ Failed to create entry: {response.text}")

# Test with autoProcess=false
print("\n" + "=" * 80)
print("TEST: Create entry with autoProcess=false")
print("=" * 80)

response2 = requests.post(
    f"{BASE_URL}/journal/entries",
    headers=headers,
    json={
        "content": "Testing entry without auto-processing",
        "mood": "🧪",
        "autoProcess": False
    }
)

if response2.status_code == 200:
    entry2 = response2.json()
    print(f"\n✅ Created entry {entry2.get('id')} with autoProcess=false:")
    print(f"  - processed: {entry2.get('processed')}")
    print(f"  - processingStatus: {entry2.get('processingStatus')}")
    
    if entry2.get('processingStatus') == 'pending':
        print("✅ Correctly set to 'pending' (not auto-processed)")
    else:
        print("❌ Should be 'pending' but got:", entry2.get('processingStatus'))