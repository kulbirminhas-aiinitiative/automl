#!/usr/bin/env python3
"""
Test the chart generation functionality
"""

import requests
import json

def test_chart_generation():
    """Test the chart generation endpoint"""
    base_url = "http://localhost:8000"
    
    print("📊 Testing Chart Generation")
    print("=" * 30)
    
    # First upload a file
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    session_id = response.json()['session_id']
    print(f"✅ Session created: {session_id}")
    
    # Test chart generation
    print("\n📈 Testing chart generation...")
    chart_payload = {
        "session_id": session_id,
        "target_column": "department",
        "chart_types": ["histogram", "correlation", "distribution"]
    }
    
    response = requests.post(
        f"{base_url}/api/generate-charts",
        json=chart_payload,
        headers={"Content-Type": "application/json"}
    )
    
    print(f"Status code: {response.status_code}")
    print(f"Response: {response.text[:500]}...")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Chart generation successful!")
        print(f"Charts generated: {list(result.get('charts', {}).keys())}")
    else:
        print(f"❌ Chart generation failed: {response.status_code}")
        print(f"Error: {response.text}")

if __name__ == "__main__":
    test_chart_generation()
