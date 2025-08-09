#!/usr/bin/env python3
"""
Debug script to check what data is actually being uploaded and processed
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

print("🔍 Debugging Data Upload and Processing")
print("=" * 40)

# Test file upload and examine response
try:
    with open(VALID_CSV, 'rb') as f:
        files = {'file': (os.path.basename(VALID_CSV), f, 'text/csv')}
        response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
        
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Upload successful!")
            print(f"Session ID: {data.get('session_id')}")
            print(f"Filename: {data.get('filename')}")
            print(f"Shape: {data.get('shape')}")
            print(f"Columns: {data.get('columns')}")
            print(f"Analysis available: {'analysis' in data}")
            
            if 'analysis' in data:
                analysis = data['analysis']
                print(f"\nData Analysis:")
                print(f"- Column info: {analysis.get('column_info', {})}")
                print(f"- Data types: {analysis.get('data_types', {})}")
                
            # Now test model suggestions with this session
            session_id = data.get('session_id')
            if session_id:
                print(f"\n🧠 Testing Model Suggestions...")
                payload = {"target_column": "performance_score"}
                suggestion_response = requests.post(f"{BACKEND_URL}/api/suggest-models/{session_id}", json=payload)
                print(f"Suggestion Status: {suggestion_response.status_code}")
                if suggestion_response.status_code != 200:
                    print(f"Suggestion Error: {suggestion_response.text}")
                else:
                    suggestions = suggestion_response.json()
                    print(f"Suggestions: {suggestions}")
                
        else:
            print(f"❌ Upload failed: {response.status_code}")
            print(f"Response: {response.text}")
            
except Exception as e:
    print(f"❌ Exception: {e}")
