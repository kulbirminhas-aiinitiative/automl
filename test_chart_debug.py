#!/usr/bin/env python3
"""
Test chart generation functionality step by step
"""

import requests
import json

def test_chart_generation_step_by_step():
    """Test chart generation with detailed error tracking"""
    base_url = "http://localhost:8000"
    
    print("🔍 Chart Generation Debug Test")
    print("=" * 40)
    
    # Step 1: Upload file
    print("1. Uploading test file...")
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload-data", files=files)
        
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            print(response.text)
            return False
        
        upload_data = response.json()
        session_id = upload_data['session_id']
        print(f"✅ Upload successful! Session: {session_id}")
        
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False
    
    # Step 2: Test chart generation
    print("\n2. Testing chart generation...")
    chart_payload = {
        "session_id": session_id,
        "target_column": "department",
        "chart_types": ["correlation"]
    }
    
    try:
        response = requests.post(
            f"{base_url}/api/generate-charts",
            json=chart_payload,
            headers={"Content-Type": "application/json"},
            timeout=30
        )
        
        print(f"Status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print("✅ Chart generation successful!")
            print(f"Response keys: {list(result.keys())}")
            
            if 'charts' in result:
                charts = result['charts']
                print(f"Charts structure: {type(charts)}")
                print(f"Chart keys: {list(charts.keys()) if isinstance(charts, dict) else 'Not a dict'}")
                
        elif response.status_code == 500:
            print("❌ Internal server error")
            print(f"Response: {response.text}")
            
        else:
            print(f"❌ Unexpected status: {response.status_code}")
            print(f"Response: {response.text}")
            
    except requests.exceptions.Timeout:
        print("❌ Request timed out (30s)")
        return False
    except Exception as e:
        print(f"❌ Request error: {e}")
        return False
    
    return response.status_code == 200

if __name__ == "__main__":
    test_chart_generation_step_by_step()
