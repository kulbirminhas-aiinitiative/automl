#!/usr/bin/env python3
"""
End-to-end test for AutoML frontend and backend integration
Tests the complete workflow: upload → analyze → suggestions → training
"""

import requests
import json
import time
import os

def test_complete_workflow():
    """Test the complete AutoML workflow"""
    base_url = "http://localhost:8080"
    
    print("🧪 Testing Complete AutoML Workflow")
    print("=" * 50)
    
    # Test 1: Upload file
    print("1. Testing file upload...")
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/data/boston.csv"
    
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
    print(f"   Dataset shape: {upload_data['shape']}")
    print(f"   Columns: {len(upload_data['columns'])}")
    
    # Test 2: Get session data
    print("\n2. Testing session data retrieval...")
    response = requests.get(f"{base_url}/api/session/{session_id}")
    
    if response.status_code != 200:
        print(f"❌ Session retrieval failed: {response.status_code}")
        return False
    
    session_data = response.json()
    print("✅ Session data retrieved successfully!")
    print(f"   Analysis quality score: {session_data['analysis']['data_quality']['overall_score']}")
    
    # Test 3: Get model suggestions
    print("\n3. Testing AI model suggestions...")
    suggestion_payload = {
        "target_column": "MEDV"
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
    suggested_models = suggestions_data['suggestions']['recommended_models']
    print("✅ Model suggestions retrieved successfully!")
    print(f"   Suggested models: {suggested_models}")
    
    # Test 4: Train a model
    print("\n4. Testing model training...")
    training_payload = {
        "target_column": "MEDV",
        "selected_models": ["linear_regression"]
    }
    
    response = requests.post(
        f"{base_url}/api/train-model/{session_id}",
        json=training_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Model training failed: {response.status_code}")
        print(response.text)
        return False
    
    training_data = response.json()
    results = training_data['results']['results']['linear_regression']
    print("✅ Model training successful!")
    print(f"   Model: {results['model']}")
    print(f"   Training time: {results['training_time']:.3f}s")
    print(f"   R² Score: {results['metrics']['r2_score']:.3f}")
    print(f"   Test MSE: {results['metrics']['test_mse']:.3f}")
    
    # Test 5: Train multiple models
    print("\n5. Testing multiple model training...")
    multi_training_payload = {
        "target_column": "MEDV",
        "selected_models": ["random_forest", "xgboost"]
    }
    
    response = requests.post(
        f"{base_url}/api/train-model/{session_id}",
        json=multi_training_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code != 200:
        print(f"❌ Multiple model training failed: {response.status_code}")
        print(response.text)
        return False
    
    multi_training_data = response.json()
    print("✅ Multiple model training successful!")
    
    for model_name, result in multi_training_data['results']['results'].items():
        if result['status'] == 'success':
            print(f"   {model_name}: R² = {result['metrics']['r2_score']:.3f}")
        else:
            print(f"   {model_name}: Failed - {result.get('error', 'Unknown error')}")
    
    print("\n🎉 All tests passed! AutoML workflow is working correctly.")
    return True

def test_frontend_connectivity():
    """Test frontend server connectivity"""
    print("🌐 Testing Frontend Connectivity")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:3004", timeout=5)
        if response.status_code == 200:
            print("✅ Frontend server is running on port 3004")
            return True
        else:
            print(f"❌ Frontend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Frontend not accessible: {e}")
        return False

def test_backend_connectivity():
    """Test backend server connectivity"""
    print("🔧 Testing Backend Connectivity")
    print("=" * 30)
    
    try:
        response = requests.get("http://localhost:8080", timeout=5)
        if response.status_code == 200:
            print("✅ Backend server is running on port 8080")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    print("🚀 AutoML End-to-End Testing Suite")
    print("=" * 50)
    
    # Test server connectivity first
    backend_ok = test_backend_connectivity()
    frontend_ok = test_frontend_connectivity()
    
    if not backend_ok:
        print("\n❌ Backend server not running. Please start it with:")
        print("   cd backend && python main.py")
        exit(1)
    
    if not frontend_ok:
        print("\n❌ Frontend server not running. Please start it with:")
        print("   npm run dev")
        exit(1)
    
    # Run complete workflow test
    print("\n" + "=" * 50)
    success = test_complete_workflow()
    
    if success:
        print("\n🎉 All systems operational! AutoML application is ready for use.")
        print("\n📊 Access the application at: http://localhost:3004")
        print("🔧 API documentation at: http://localhost:8080/docs")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        exit(1)
