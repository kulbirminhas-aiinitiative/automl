#!/usr/bin/env python3
"""
Debug script to test the training endpoint specifically
"""

import requests
import json
import os
from dotenv import load_dotenv

load_dotenv()
BACKEND_PORT = os.getenv('BACKEND_PORT', '8888')
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
TEST_FILE_DIR = os.path.dirname(__file__)
VALID_CSV = os.path.join(TEST_FILE_DIR, "test_data_fresh.csv")

print("🔍 Debugging Training Endpoint")
print("=" * 40)

# First upload file and get session
try:
    with open(VALID_CSV, 'rb') as f:
        files = {'file': (os.path.basename(VALID_CSV), f, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data.get('session_id')
            print(f"✅ Upload successful! Session: {session_id}")
            print(f"Columns: {data.get('columns')}")
            
            # Now test training directly
            print(f"\n🤖 Testing Training Endpoint...")
            payload = {"target_column": "performance_score", "selected_models": ["linear_regression"]}
            training_response = requests.post(f"{BACKEND_URL}/api/train-model/{session_id}", json=payload)
            print(f"Training Status: {training_response.status_code}")
            
            if training_response.status_code == 200:
                training_data = training_response.json()
                print(f"✅ Training successful!")
                print(f"Results: {json.dumps(training_data, indent=2)}")
            else:
                print(f"❌ Training failed!")
                print(f"Error: {training_response.text}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            
except Exception as e:
    print(f"❌ Exception: {e}")
