#!/usr/bin/env python3
"""
Final Comprehensive End-to-End Test for AutoML Frontend and Backend Integration
Tests the complete workflow with fresh data for each test to avoid caching issues
"""

import requests
import json
import time
import os
import random
import string
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
BACKEND_PORT = os.getenv('BACKEND_PORT', '8888')
FRONTEND_PORT = os.getenv('FRONTEND_PORT', '3333')
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
TEST_FILE_DIR = os.path.dirname(__file__)

def create_unique_test_data():
    """Create unique test data to avoid caching issues"""
    random_suffix = ''.join(random.choices(string.ascii_lowercase, k=5))
    data = [
        f"name,age,salary,experience,department,performance_score,years_in_company",
        f"Alice_{random_suffix},28,65000,3,Engineering,85,2",
        f"Bob_{random_suffix},32,75000,5,Marketing,92,4",
        f"Carol_{random_suffix},45,95000,12,Sales,78,8",
        f"David_{random_suffix},29,58000,2,HR,88,1",
        f"Eve_{random_suffix},38,82000,8,Engineering,91,6",
        f"Frank_{random_suffix},26,52000,1,Marketing,82,1",
        f"Grace_{random_suffix},41,88000,10,Sales,87,7",
        f"Henry_{random_suffix},33,72000,6,HR,89,4",
        f"Iris_{random_suffix},31,69000,4,Engineering,86,3",
        f"Jack_{random_suffix},27,62000,2,Marketing,84,2"
    ]
    filename = f"test_data_unique_{random_suffix}.csv"
    filepath = os.path.join(TEST_FILE_DIR, filename)
    
    with open(filepath, 'w') as f:
        f.write('\\n'.join(data))
    
    return filepath, filename

# --- Test Logger ---
def log_test(name, status, message=""):
    status_emoji = "✅" if status else "❌"
    print(f"{status_emoji} {name}: {message}")

# --- Test Functions ---

def test_server_connectivity():
    """Tests if backend and frontend servers are running."""
    print("\\n🔌 Testing Server Connectivity")
    print("-" * 40)
    try:
        response = requests.get(BACKEND_URL, timeout=5)
        log_test("Backend Connectivity", response.status_code == 200, f"Status: {response.status_code}")
        backend_ok = response.status_code == 200
    except requests.RequestException as e:
        log_test("Backend Connectivity", False, f"Error: {e}")
        backend_ok = False

    try:
        response = requests.get(FRONTEND_URL, timeout=5)
        log_test("Frontend Connectivity", response.status_code == 200, f"Status: {response.status_code}")
        frontend_ok = response.status_code == 200
    except requests.RequestException as e:
        log_test("Frontend Connectivity", False, f"Error: {e}")
        frontend_ok = False
        
    return backend_ok and frontend_ok

def test_complete_workflow():
    """Tests the complete AutoML workflow from upload to training"""
    print("\\n🔄 Testing Complete AutoML Workflow")
    print("-" * 40)
    
    # Create unique test data
    test_file, test_filename = create_unique_test_data()
    session_id = None
    
    try:
        # 1. Upload Data
        with open(test_file, 'rb') as f:
            files = {'file': (test_filename, f, 'text/csv')}
            response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
            
        if response.status_code == 200 and 'session_id' in response.json():
            session_id = response.json()['session_id']
            columns = response.json().get('columns', [])
            log_test("Data Upload", True, f"Session: {session_id}, Columns: {len(columns)}")
        else:
            log_test("Data Upload", False, f"Status: {response.status_code}")
            return False

        # 2. Model Suggestions
        payload = {"target_column": "performance_score"}
        response = requests.post(f"{BACKEND_URL}/api/suggest-models/{session_id}", json=payload)
        
        if response.status_code == 200:
            suggestions = response.json().get('suggestions', {})
            recommended = suggestions.get('recommended_models', [])
            log_test("Model Suggestions", True, f"Recommended: {recommended[:3]}")
        else:
            log_test("Model Suggestions", False, f"Status: {response.status_code}")
            return False

        # 3. Model Training
        payload = {"target_column": "performance_score", "selected_models": ["linear_regression", "random_forest"]}
        response = requests.post(f"{BACKEND_URL}/api/train-model/{session_id}", json=payload)
        
        if response.status_code == 200:
            results = response.json().get('results', {})
            trained_models = list(results.get('results', {}).keys())
            log_test("Model Training", True, f"Trained: {trained_models}")
        else:
            log_test("Model Training", False, f"Status: {response.status_code}, Error: {response.text[:100]}")
            return False

        # 4. Chart Generation
        payload = {"session_id": session_id, "chart_types": ["correlation", "distribution"]}
        response = requests.post(f"{BACKEND_URL}/api/generate-charts", json=payload)
        
        if response.status_code == 200:
            charts = response.json().get('charts', {})
            chart_count = charts.get('chart_count', 0)
            log_test("Chart Generation", chart_count > 0, f"Generated {chart_count} charts")
        else:
            log_test("Chart Generation", False, f"Status: {response.status_code}")
            return False

        return True
        
    except Exception as e:
        log_test("Workflow Exception", False, f"Error: {e}")
        return False
    finally:
        # Clean up test file
        if os.path.exists(test_file):
            os.remove(test_file)

def test_error_handling():
    """Tests various error scenarios"""
    print("\\n⚠️  Testing Error Handling")
    print("-" * 40)
    
    # Test invalid file upload
    try:
        invalid_content = b"This is not a valid CSV file"
        files = {'file': ('invalid.txt', invalid_content, 'text/plain')}
        response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
        log_test("Invalid File Upload", response.status_code == 400, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Invalid File Upload", False, f"Exception: {e}")

    # Test invalid session for suggestions
    try:
        payload = {"target_column": "performance_score"}
        response = requests.post(f"{BACKEND_URL}/api/suggest-models/invalid_session", json=payload)
        log_test("Invalid Session Suggestions", response.status_code == 404, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Invalid Session Suggestions", False, f"Exception: {e}")

# --- Main Test Runner ---
if __name__ == "__main__":
    print("🚀 AutoML Final Comprehensive Testing Suite 🚀")
    print("=" * 60)
    
    # Check server connectivity
    if not test_server_connectivity():
        print("\\n❌ Servers not running. Please start both backend and frontend.")
        exit(1)
    
    # Test complete workflow
    workflow_success = test_complete_workflow()
    
    # Test error handling
    test_error_handling()
    
    print("\\n" + "=" * 60)
    if workflow_success:
        print("🎉 All critical tests passed! AutoML system is fully functional.")
    else:
        print("❌ Some critical tests failed. Check the logs above.")
    
    print("✅ Testing complete.")
