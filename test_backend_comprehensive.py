#!/usr/bin/env python3
"""
Backend-only comprehensive test suite for AutoML system
Tests all backend endpoints without requiring frontend
"""

import requests
import json
import csv
import io
import time
from datetime import datetime


def log_test_result(test_name, status, details=""):
    """Log test results to activity log"""
    try:
        with open("logs/activity-log.md", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n## {timestamp} - Backend Test: {test_name}\n")
            f.write(f"**Status:** {status}\n")
            if details:
                f.write(f"**Details:** {details}\n")
    except:
        pass


def create_test_data():
    """Create test CSV data"""
    return """name,age,salary,experience,department,performance_score,years_in_company
John,25,50000,2,IT,85,2
Sarah,30,65000,5,Finance,92,3
Mike,35,80000,8,IT,78,5
Alice,28,58000,3,Marketing,88,3
Bob,32,72000,6,IT,81,4
Carol,29,61000,4,Finance,90,2
Dave,31,69000,7,Marketing,76,5
Eve,26,54000,3,IT,83,3
Frank,33,75000,9,Finance,87,6
Grace,27,56000,2,Marketing,89,2"""


def test_backend_connectivity():
    """Test backend server connectivity"""
    try:
        response = requests.get("http://localhost:8888/")
        return response.status_code == 200, f"Status: {response.status_code}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def test_file_upload():
    """Test file upload functionality"""
    try:
        csv_data = create_test_data()
        files = {'file': ('test_data.csv', io.StringIO(csv_data), 'text/csv')}
        
        response = requests.post("http://localhost:8888/api/upload-data", files=files)
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Session: {data['session_id']}, Shape: {data['shape']}", data['session_id']
        else:
            return False, f"Status: {response.status_code}, Response: {response.text}", None
            
    except Exception as e:
        return False, f"Exception: {str(e)}", None


def test_model_suggestions(session_id):
    """Test model suggestions endpoint"""
    try:
        payload = {
            "target_column": "performance_score",
            "problem_type": "regression"
        }
        
        response = requests.post(
            f"http://localhost:8888/api/suggest-models/{session_id}",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Got {len(data['suggestions']['recommended_models'])} model suggestions"
        else:
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"


def test_model_training(session_id):
    """Test model training endpoint"""
    try:
        payload = {
            "target_column": "performance_score",
            "selected_models": ["linear_regression", "random_forest"],
            "train_config": {
                "test_size": 0.2,
                "random_state": 42
            }
        }
        
        response = requests.post(
            f"http://localhost:8888/api/train-model/{session_id}",
            json=payload
        )
        
        if response.status_code == 200:
            data = response.json()
            results = data['results']['results']
            success_count = sum(1 for model in results.values() if model.get('status') == 'success')
            return True, f"Training completed: {success_count} models successful"
        else:
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"


def test_chart_generation(session_id):
    """Test chart generation endpoint"""
    try:
        payload = {
            "session_id": session_id,
            "chart_types": ["correlation", "distribution"],
            "target_column": "performance_score"
        }
        
        response = requests.post("http://localhost:8888/api/generate-charts", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            return True, f"Generated {len(data.get('charts', []))} charts"
        else:
            return False, f"Status: {response.status_code}, Response: {response.text}"
            
    except Exception as e:
        return False, f"Exception: {str(e)}"


def test_error_handling():
    """Test error handling scenarios"""
    print("\n--- Testing Error Handling ---")
    error_tests_passed = 0
    
    # Test invalid session
    try:
        response = requests.post(
            "http://localhost:8888/api/suggest-models/invalid_session",
            json={"target_column": "performance_score", "problem_type": "regression"}
        )
        
        if response.status_code == 404:
            print("[PASS] Invalid session handling: Returns 404")
            log_test_result("Invalid Session Error", "PASS", "Returns 404 as expected")
            error_tests_passed += 1
        else:
            print(f"[FAIL] Invalid session handling: Expected 404, got {response.status_code}")
            log_test_result("Invalid Session Error", "FAIL", f"Expected 404, got {response.status_code}")
            
    except Exception as e:
        print(f"[FAIL] Invalid session test: {str(e)}")
        log_test_result("Invalid Session Error", "FAIL", str(e))
    
    # Test invalid file upload
    try:
        files = {'file': ('invalid.txt', io.StringIO("not,csv,data"), 'text/plain')}
        response = requests.post("http://localhost:8888/api/upload-data", files=files)
        
        if response.status_code == 400:
            print("[PASS] Invalid file handling: Returns 400")
            log_test_result("Invalid File Upload", "PASS", "Returns 400 as expected")
            error_tests_passed += 1
        else:
            print(f"[FAIL] Invalid file handling: Expected 400, got {response.status_code}")
            log_test_result("Invalid File Upload", "FAIL", f"Expected 400, got {response.status_code}")
            
    except Exception as e:
        print(f"[FAIL] Invalid file test: {str(e)}")
        log_test_result("Invalid File Upload", "FAIL", str(e))
    
    return error_tests_passed


def main():
    """Run comprehensive backend tests"""
    print("🚀 AutoML Backend Comprehensive Testing Suite 🚀")
    print("=" * 50)
    
    start_time = time.time()
    total_tests = 0
    passed_tests = 0
    
    # Test server connectivity
    print("\n--- Testing Backend Connectivity ---")
    total_tests += 1
    success, details = test_backend_connectivity()
    if success:
        print(f"[PASS] Backend Connectivity: {details}")
        log_test_result("Backend Connectivity", "PASS", details)
        passed_tests += 1
    else:
        print(f"[FAIL] Backend Connectivity: {details}")
        log_test_result("Backend Connectivity", "FAIL", details)
        print("❌ Backend not running. Please start the backend server.")
        return
    
    # Test file upload
    print("\n--- Testing File Upload ---")
    total_tests += 1
    success, details, session_id = test_file_upload()
    if success:
        print(f"[PASS] File Upload: {details}")
        log_test_result("File Upload", "PASS", details)
        passed_tests += 1
    else:
        print(f"[FAIL] File Upload: {details}")
        log_test_result("File Upload", "FAIL", details)
        return
    
    # Test model suggestions
    print("\n--- Testing Model Suggestions ---")
    total_tests += 1
    success, details = test_model_suggestions(session_id)
    if success:
        print(f"[PASS] Model Suggestions: {details}")
        log_test_result("Model Suggestions", "PASS", details)
        passed_tests += 1
    else:
        print(f"[FAIL] Model Suggestions: {details}")
        log_test_result("Model Suggestions", "FAIL", details)
    
    # Test model training
    print("\n--- Testing Model Training ---")
    total_tests += 1
    success, details = test_model_training(session_id)
    if success:
        print(f"[PASS] Model Training: {details}")
        log_test_result("Model Training", "PASS", details)
        passed_tests += 1
    else:
        print(f"[FAIL] Model Training: {details}")
        log_test_result("Model Training", "FAIL", details)
    
    # Test chart generation
    print("\n--- Testing Chart Generation ---")
    total_tests += 1
    success, details = test_chart_generation(session_id)
    if success:
        print(f"[PASS] Chart Generation: {details}")
        log_test_result("Chart Generation", "PASS", details)
        passed_tests += 1
    else:
        print(f"[FAIL] Chart Generation: {details}")
        log_test_result("Chart Generation", "FAIL", details)
    
    # Test error handling
    error_tests_passed = test_error_handling()
    total_tests += 2  # Invalid session + invalid file
    passed_tests += error_tests_passed
    
    # Final summary
    elapsed_time = time.time() - start_time
    print(f"\n🎯 Test Summary")
    print("=" * 30)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {total_tests - passed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    print(f"Execution Time: {elapsed_time:.2f}s")
    
    # Log final summary
    log_test_result(
        "Backend Test Suite Complete", 
        "SUMMARY", 
        f"Passed: {passed_tests}/{total_tests} ({(passed_tests/total_tests)*100:.1f}%) in {elapsed_time:.2f}s"
    )
    
    if passed_tests == total_tests:
        print("\n✅ All backend tests passed!")
        return 0
    else:
        print(f"\n❌ {total_tests - passed_tests} test(s) failed")
        return 1


if __name__ == "__main__":
    exit(main())
