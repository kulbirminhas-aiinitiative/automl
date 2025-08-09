#!/usr/bin/env python3
"""
Test the complete chart generation workflow like the frontend would do it
"""

import requests
import json

def test_frontend_chart_workflow():
    """Test chart generation exactly like the frontend does it"""
    base_url = "http://localhost:8000"
    
    print("🎨 Testing Frontend Chart Workflow")
    print("=" * 40)
    
    # Step 1: Upload file
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    if response.status_code != 200:
        print(f"❌ Upload failed: {response.status_code}")
        return False
    
    upload_data = response.json()
    session_id = upload_data['session_id']
    print(f"✅ Upload successful! Session: {session_id}")
    
    # Step 2: Test chart generation exactly like frontend
    print("\n📊 Testing chart generation (frontend style)...")
    chart_payload = {
        "session_id": session_id,
        "target_column": "department"  # Using actual column from sample data
    }
    
    response = requests.post(
        f"{base_url}/api/generate-charts",
        headers={'Content-Type': 'application/json'},
        json=chart_payload
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Chart generation successful!")
        
        # Check response structure
        print(f"Response keys: {list(result.keys())}")
        
        if 'charts' in result:
            charts = result['charts']
            print(f"Charts structure: {type(charts)}")
            if isinstance(charts, dict):
                print(f"Chart types available: {list(charts.keys())}")
                
                # Check for actual chart data
                if 'charts' in charts:
                    actual_charts = charts['charts']
                    print(f"Actual chart types: {list(actual_charts.keys())}")
                    
                    # Check correlation chart details
                    if 'correlation' in actual_charts:
                        corr_chart = actual_charts['correlation']
                        print(f"Correlation chart has: {list(corr_chart.keys())}")
                        
                        if 'heatmap' in corr_chart:
                            heatmap = corr_chart['heatmap']
                            print(f"Heatmap keys: {list(heatmap.keys())}")
                            if 'data' in heatmap and len(heatmap['data']) > 0:
                                print("✅ Heatmap has data!")
                            else:
                                print("⚠️ Heatmap missing data")
                
        return True
    else:
        print(f"❌ Chart generation failed: {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error: {error_data}")
        except:
            print(f"Raw response: {response.text}")
        return False

if __name__ == "__main__":
    test_frontend_chart_workflow()
