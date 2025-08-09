#!/usr/bin/env python3
"""
Simple debug script to test a single clean upload and training
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_PORT = os.getenv('BACKEND_PORT', '8888')
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
TEST_FILE = "/Users/kulbirminhas/Documents/Repo/projects/automl/debug_simple.csv"

print("🔍 Simple Debug Test")
print("=" * 30)

# Upload and test
try:
    with open(TEST_FILE, 'rb') as f:
        files = {'file': ('debug_simple.csv', f, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
        
    if response.status_code == 200:
        data = response.json()
        session_id = data.get('session_id')
        print(f"✅ Upload: {session_id}")
        print(f"Columns: {data.get('columns')}")
        print(f"Shape: {data.get('shape')}")
        
        # Try training
        payload = {"target_column": "performance_score", "selected_models": ["linear_regression"]}
        train_response = requests.post(f"{BACKEND_URL}/api/train-model/{session_id}", json=payload)
        print(f"\\nTraining Status: {train_response.status_code}")
        
        if train_response.status_code == 200:
            print("✅ Training successful!")
            print(json.dumps(train_response.json(), indent=2)[:500] + "...")
        else:
            print(f"❌ Training failed: {train_response.text}")
    else:
        print(f"❌ Upload failed: {response.status_code} - {response.text}")
        
except Exception as e:
    print(f"❌ Exception: {e}")
    
# Clean up
if os.path.exists(TEST_FILE):
    os.remove(TEST_FILE)
