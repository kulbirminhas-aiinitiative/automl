#!/usr/bin/env python3
"""
Comprehensive End-to-End Test for AutoML Frontend and Backend Integration
Tests the complete workflow: upload → analyze → suggestions → training → charts
"""

import requests
import json
import time
import os
from dotenv import load_dotenv

# --- Configuration ---
load_dotenv()
BACKEND_PORT = os.getenv('BACKEND_PORT', '8888')
FRONTEND_PORT = os.getenv('FRONTEND_PORT', '3333')
BACKEND_URL = f"http://localhost:{BACKEND_PORT}"
FRONTEND_URL = f"http://localhost:{FRONTEND_PORT}"
TEST_FILE_DIR = os.path.dirname(__file__)
VALID_CSV = os.path.join(TEST_FILE_DIR, "test_data_fresh.csv")
VALID_JSON = os.path.join(TEST_FILE_DIR, "sample_data.json")
INVALID_FILE = os.path.join(TEST_FILE_DIR, "invalid_file.txt")

# --- Test Logger ---
def log_test(name, status, message=""):
    print(f"[{'PASS' if status else 'FAIL'}] {name}: {message}")

# --- Test Functions ---

def test_server_connectivity():
    """Tests if backend and frontend servers are running."""
    print("\n--- Testing Server Connectivity ---")
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

def test_file_uploads():
    """Tests various file upload scenarios."""
    print("\n--- Testing File Uploads ---")
    session_id = None

    # 1. Test valid CSV upload
    try:
        with open(VALID_CSV, 'rb') as f:
            files = {'file': (os.path.basename(VALID_CSV), f, 'text/csv')}
            response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
            if response.status_code == 200 and 'session_id' in response.json():
                session_id = response.json()['session_id']
                log_test("Upload Valid CSV", True, f"Session ID: {session_id}")
            else:
                log_test("Upload Valid CSV", False, f"Status: {response.status_code}, Response: {response.text[:100]}")
    except Exception as e:
        log_test("Upload Valid CSV", False, f"Exception: {e}")

    # 2. Test valid JSON upload
    try:
        with open(VALID_JSON, 'w') as f:
            json.dump([{"a":1, "b":2}, {"a":3, "b":4}], f)
        with open(VALID_JSON, 'rb') as f:
            files = {'file': (os.path.basename(VALID_JSON), f, 'application/json')}
            response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
            log_test("Upload Valid JSON", response.status_code == 200, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Upload Valid JSON", False, f"Exception: {e}")
    finally:
        if os.path.exists(VALID_JSON):
            os.remove(VALID_JSON)

    # 3. Test invalid file type upload
    try:
        with open(INVALID_FILE, 'w') as f:
            f.write("this is not a valid file type")
        with open(INVALID_FILE, 'rb') as f:
            files = {'file': (os.path.basename(INVALID_FILE), f, 'text/plain')}
            response = requests.post(f"{BACKEND_URL}/api/upload-data", files=files)
            log_test("Upload Invalid File Type", response.status_code == 400, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Upload Invalid File Type", False, f"Exception: {e}")
    finally:
        if os.path.exists(INVALID_FILE):
            os.remove(INVALID_FILE)
            
    return session_id

def test_model_suggestions(session_id):
    """Tests model suggestion endpoint."""
    print("\n--- Testing Model Suggestions ---")
    if not session_id:
        log_test("Model Suggestions", False, "Skipping due to no session ID.")
        return

    # 1. Valid suggestion request
    try:
        payload = {"target_column": "performance_score"}
        response = requests.post(f"{BACKEND_URL}/api/suggest-models/{session_id}", json=payload)
        if response.status_code == 200 and 'suggestions' in response.json():
            log_test("Valid Model Suggestion", True, f"Recommended: {response.json()['suggestions'].get('recommended_models')}")
        else:
            log_test("Valid Model Suggestion", False, f"Status: {response.status_code}, Response: {response.text[:100]}")
    except Exception as e:
        log_test("Valid Model Suggestion", False, f"Exception: {e}")

    # 2. Invalid session ID
    try:
        payload = {"target_column": "performance_score"}
        response = requests.post(f"{BACKEND_URL}/api/suggest-models/invalid_session", json=payload)
        log_test("Suggestion with Invalid Session", response.status_code == 404, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Suggestion with Invalid Session", False, f"Exception: {e}")

def test_model_training(session_id):
    """Tests model training endpoint."""
    print("\n--- Testing Model Training ---")
    if not session_id:
        log_test("Model Training", False, "Skipping due to no session ID.")
        return

    # 1. Valid training request
    try:
        payload = {"target_column": "performance_score", "selected_models": ["linear_regression"]}
        response = requests.post(f"{BACKEND_URL}/api/train-model/{session_id}", json=payload)
        if response.status_code == 200 and 'results' in response.json():
            log_test("Valid Model Training", True, "Training completed.")
        else:
            log_test("Valid Model Training", False, f"Status: {response.status_code}, Response: {response.text[:100]}")
    except Exception as e:
        log_test("Valid Model Training", False, f"Exception: {e}")

    # 2. Invalid model name
    try:
        payload = {"target_column": "performance_score", "selected_models": ["invalid_model_name"]}
        response = requests.post(f"{BACKEND_URL}/api/train-model/{session_id}", json=payload)
        log_test("Training with Invalid Model", response.status_code == 400, f"Status: {response.status_code}")
    except Exception as e:
        log_test("Training with Invalid Model", False, f"Exception: {e}")

def test_chart_generation(session_id):
    """Tests chart generation endpoint."""
    print("\n--- Testing Chart Generation ---")
    if not session_id:
        log_test("Chart Generation", False, "Skipping due to no session ID.")
        return

    # 1. Valid chart request
    try:
        payload = {"session_id": session_id, "chart_types": ["correlation", "distribution"]}
        response = requests.post(f"{BACKEND_URL}/api/generate-charts", json=payload)
        if response.status_code == 200 and 'charts' in response.json():
            charts = response.json()['charts']
            chart_count = charts.get('chart_count', 0)
            log_test("Valid Chart Generation", chart_count > 0, f"Generated {chart_count} charts.")
        else:
            log_test("Valid Chart Generation", False, f"Status: {response.status_code}, Response: {response.text[:100]}")
    except Exception as e:
        log_test("Valid Chart Generation", False, f"Exception: {e}")

# --- Main Test Runner ---
if __name__ == "__main__":
    print("🚀 AutoML Comprehensive E2E Testing Suite 🚀")
    print("=" * 50)

    if not test_server_connectivity():
        print("\n❌ Servers not running. Please start both backend and frontend.")
        exit(1)

    session_id = test_file_uploads()
    test_model_suggestions(session_id)
    test_model_training(session_id)
    test_chart_generation(session_id)

    print("\n" + "=" * 50)
    print("✅ Testing complete.")

