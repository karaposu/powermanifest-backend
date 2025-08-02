# test_affirmations_422.py
#!/usr/bin/env python3
"""Test script to reproduce the 422 error with scheduled_only parameter"""

import requests
import json

# Base URL
BASE_URL = "http://127.0.0.1:8000"

# User credentials
email = "e@hotmail.com"
password = "string"

# Login to get token
print("1. Logging in...")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": email, "password": password}
)

if login_response.status_code != 200:
    print(f"Login failed: {login_response.status_code}")
    print(login_response.text)
    exit(1)

token = login_response.json()["token"]
headers = {"Authorization": f"Bearer {token}"}
print(f"Login successful, token: {token[:20]}...")

# Test 1: GET affirmations without any parameters
print("\n2. Testing GET /affirmations without parameters...")
response = requests.get(f"{BASE_URL}/affirmations", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Success!")
else:
    print(f"Error: {response.text}")

# Test 2: GET affirmations with scheduled_only=false (string)
print("\n3. Testing GET /affirmations?scheduled_only=false (as string)...")
response = requests.get(f"{BASE_URL}/affirmations?scheduled_only=false", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Success!")
else:
    print(f"Error: {response.text}")

# Test 3: GET affirmations with scheduled_only=False (boolean in params)
print("\n4. Testing GET /affirmations with scheduled_only=False (as boolean in params)...")
response = requests.get(f"{BASE_URL}/affirmations", headers=headers, params={"scheduled_only": False})
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Success!")
else:
    print(f"Error: {response.text}")

# Test 4: GET affirmations with scheduled_only=true
print("\n5. Testing GET /affirmations?scheduled_only=true...")
response = requests.get(f"{BASE_URL}/affirmations?scheduled_only=true", headers=headers)
print(f"Status: {response.status_code}")
if response.status_code == 200:
    print("Success!")
else:
    print(f"Error: {response.text}")