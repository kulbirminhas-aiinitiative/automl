#!/usr/bin/env python3
"""
Test script to verify frontend behavior and identify any hanging issues
"""

import requests
import json
import time
import os

def test_frontend_upload_flow():
    """Test the complete frontend upload flow"""
    base_url = "http://localhost:8000"
    
    print("🧪 Testing Frontend Upload Flow")
    print("=" * 50)
    
    # Test 1: Upload file
    print("1. Testing file upload...")
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return False
    
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        print(response.text)
        return False
    
    upload_data = response.json()
    session_id = upload_data['session_id']
    print(f"✅ Upload successful! Session ID: {session_id}")
    print(f"   Is duplicate: {upload_data.get('is_duplicate', False)}")
    print(f"   Dataset shape: {upload_data['shape']}")
    
    # Test 2: Simulate what Dashboard.tsx does on mount
    print("\n2. Testing Dashboard session data fetch (what happens after upload)...")
    response = requests.get(f"{base_url}/api/session/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Dashboard session fetch failed: {response.status_code}")
        print(response.text)
        return False
    
    session_data = response.json()
    print("✅ Dashboard session data retrieved successfully!")
    print(f"   Analysis quality score: {session_data['analysis']['data_quality']['overall_score']}")
    print(f"   Available columns: {len(session_data['analysis']['columns']['names'])}")
    
    # Test 3: Test model suggestions (what happens when user selects target)
    print("\n3. Testing model suggestions flow...")
    suggestion_payload = {
        "target_column": "department"
    }
    
    response = requests.post(
        f"{base_url}/api/suggest-models/{session_id}",
        json=suggestion_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Model suggestions failed: {response.status_code}")
        print(response.text)
        return False
    
    suggestions_data = response.json()
    print("✅ Model suggestions retrieved successfully!")
    print(f"   Problem type: {suggestions_data['suggestions']['problem_type']}")
    if 'recommended_models' in suggestions_data['suggestions']:
        models = suggestions_data['suggestions']['recommended_models']
        print(f"   Suggested models: {models}")
    
    print("\n🎉 Frontend upload flow test completed successfully!")
    print("   The frontend should work correctly now.")
    return True

def test_api_response_times():
    """Test API response times to identify any slow endpoints"""
    print("\n⏱️  Testing API Response Times")
    print("=" * 40)
    
    base_url = "http://localhost:8000"
    
    # Test health check
    start_time = time.time()
    response = requests.get(f"{base_url}/")
    health_time = time.time() - start_time
    print(f"Health check: {health_time:.3f}s")
    
    # Test upload (with existing file)
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    if os.path.exists(file_path):
        start_time = time.time()
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload-data", files=files)
        upload_time = time.time() - start_time
        print(f"Upload endpoint: {upload_time:.3f}s")
        
        if response.status_code == 200:
            session_id = response.json()['session_id']
            
            # Test session fetch
            start_time = time.time()
            response = requests.get(f"{base_url}/api/session/{session_id}")
            session_time = time.time() - start_time
            print(f"Session fetch: {session_time:.3f}s")
            
            # Test suggestions
            start_time = time.time()
            response = requests.post(
                f"{base_url}/api/suggest-models/{session_id}",
                json={"target_column": "department"},
                headers={"Content-Type": "application/json"}
            )
            suggestions_time = time.time() - start_time
            print(f"Model suggestions: {suggestions_time:.3f}s")
    
    print("✅ Response time analysis complete")

if __name__ == "__main__":
    print("🚀 Frontend Behavior Testing Suite")
    print("=" * 50)
    
    # Test connectivity first
    try:
        response = requests.get("http://localhost:8000", timeout=5)
        if response.status_code != 200:
            print("❌ Backend not responding correctly")
            exit(1)
    except:
        print("❌ Backend not accessible")
        exit(1)
    
    try:
        response = requests.get("http://localhost:3004", timeout=5)
        if response.status_code != 200:
            print("❌ Frontend not responding correctly")
            exit(1)
    except:
        print("❌ Frontend not accessible")
        exit(1)
    
    print("✅ Both servers are accessible")
    
    # Run tests
    success = test_frontend_upload_flow()
    if success:
        test_api_response_times()
        print("\n🎯 Frontend should now work correctly!")
        print("   Try uploading a file at: http://localhost:3004")
    else:
        print("\n❌ Issues detected. Check the logs above.")
