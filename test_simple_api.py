#!/usr/bin/env python3
"""
Simple API Test Script
Tests just the upload functionality without complex orchestration
"""

import requests
import pandas as pd
import json

def test_simple_upload():
    """Test simple upload and basic response"""
    print("🧪 Simple AutoML API Test")
    print("=" * 40)
    
    datasets_to_test = [
        "data/synthetic_regression.csv",
        "data/iris_classification.csv",
        "data/boston.csv"
    ]
    
    for dataset_path in datasets_to_test:
        print(f"\n📤 Testing: {dataset_path}")
        
        try:
            # Test upload
            with open(dataset_path, 'rb') as f:
                files = {'file': (dataset_path.split('/')[-1], f, 'text/csv')}
                response = requests.post('http://127.0.0.1:8080/api/upload-data', files=files)
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Upload successful")
                print(f"📊 Shape: {result['shape']}")
                print(f"📋 Columns: {len(result['columns'])} columns")
                print(f"🎯 Sample columns: {result['columns'][:3]}")
                
                # Test session retrieval
                session_id = result['session_id']
                session_response = requests.get(f'http://127.0.0.1:8080/api/session/{session_id}')
                
                if session_response.status_code == 200:
                    print("✅ Session retrieval successful")
                else:
                    print(f"❌ Session retrieval failed: {session_response.status_code}")
                
            else:
                print(f"❌ Upload failed: {response.status_code}")
                print(response.text)
                
        except Exception as e:
            print(f"❌ Error: {e}")
        
        print("-" * 40)

if __name__ == "__main__":
    test_simple_upload()
