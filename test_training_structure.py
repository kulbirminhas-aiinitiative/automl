#!/usr/bin/env python3
"""
Test training endpoint specifically to verify the response structure
"""

import requests
import json

def test_training_endpoint():
    """Test the training endpoint and log the response structure"""
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Training Endpoint Structure")
    print("=" * 50)
    
    # First upload a file to get a session
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    session_id = response.json()['session_id']
    print(f"✅ Session created: {session_id}")
    
    # Test training a single model
    print("\n📊 Testing single model training...")
    training_payload = {
        "target_column": "department",
        "selected_models": ["random_forest"]
    }
    
    response = requests.post(
        f"{base_url}/api/train-model/{session_id}",
        json=training_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Training successful!")
        print("📋 Response structure:")
        print(json.dumps(result, indent=2))
        
        # Check if we have the expected fields
        if 'results' in result:
            results = result['results']
            if 'random_forest' in results:
                model_result = results['random_forest']
                print(f"\n🎯 Model result structure:")
                print(f"   - model: {model_result.get('model', 'N/A')}")
                print(f"   - training_time: {model_result.get('training_time', 'N/A')}")
                print(f"   - metrics keys: {list(model_result.get('metrics', {}).keys())}")
        
    else:
        print(f"❌ Training failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_training_endpoint()
