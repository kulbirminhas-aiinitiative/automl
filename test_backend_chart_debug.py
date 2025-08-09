#!/usr/bin/env python3
"""
Test backend chart endpoint with debugging
"""

import requests
import json
import traceback

def test_backend_chart_endpoint():
    """Test the backend chart endpoint with detailed debugging"""
    base_url = "http://localhost:8000"
    
    print("🔍 Backend Chart Endpoint Debug Test")
    print("=" * 40)
    
    # Upload file first
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    session_id = response.json()['session_id']
    print(f"✅ Session created: {session_id}")
    
    # Test simple chart request
    print("\n📊 Testing minimal chart request...")
    simple_payload = {
        "session_id": session_id
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-charts",
            json=simple_payload,
            headers={"Content-Type": "application/json"},
            timeout=10
        )
        
        print(f"Status: {response.status_code}")
        print(f"Headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Charts generated successfully!")
            print(f"Response keys: {list(result.keys())}")
        else:
            print(f"❌ Error: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out")
    except Exception as e:
        print(f"❌ Request failed: {e}")
        traceback.print_exc()

if __name__ == "__main__":
    test_backend_chart_endpoint()
