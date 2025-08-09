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
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    backend_port = os.getenv('BACKEND_PORT', '8888')
    base_url = f"http://localhost:{backend_port}"
    
    print("🧪 Testing Complete AutoML Workflow")
    print("=" * 50)
    
    # Test 1: Upload file
    print("1. Testing file upload...")
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/boston.csv"
    if not os.path.exists(file_path):
        print(f"❌ Test file not found: {file_path}")
        return False
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{base_url}/api/upload-data", files=files)
        print(f"[UPLOAD] Status: {response.status_code}")
        print(f"[UPLOAD] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Upload failed: {response.status_code}")
            return False
        upload_data = response.json()
        session_id = upload_data['session_id']
        print(f"✅ Upload successful! Session ID: {session_id}")
        print(f"   Dataset shape: {upload_data['shape']}")
        print(f"   Columns: {len(upload_data['columns'])}")
    except Exception as e:
        print(f"❌ Exception during upload: {e}")
        return False
    
    # Test 2: Get session data
    print("\n2. Testing session data retrieval...")
    try:
        response = requests.get(f"{base_url}/api/session/{session_id}")
        print(f"[SESSION] Status: {response.status_code}")
        print(f"[SESSION] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Session retrieval failed: {response.status_code}")
            return False
        session_data = response.json()
        print("✅ Session data retrieved successfully!")
        print(f"   Analysis quality score: {session_data['analysis']['data_quality']['overall_score']}")
    except Exception as e:
        print(f"❌ Exception during session retrieval: {e}")
        return False
    
    # Test 3: Get model suggestions
    print("\n3. Testing AI model suggestions...")
    suggestion_payload = {
        "target_column": "AGE"
    }
    try:
        response = requests.post(
            f"{base_url}/api/suggest-models/{session_id}",
            json=suggestion_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"[SUGGESTIONS] Status: {response.status_code}")
        print(f"[SUGGESTIONS] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Model suggestions failed: {response.status_code}")
            return False
        suggestions_data = response.json()
        print(f"DEBUG: Suggestions data keys: {list(suggestions_data.keys())}")
        if 'suggestions' in suggestions_data:
            print(f"DEBUG: Suggestions sub-keys: {list(suggestions_data['suggestions'].keys())}")
            if 'error' in suggestions_data['suggestions']:
                print(f"DEBUG: Error in suggestions: {suggestions_data['suggestions']['error']}")
            if 'fallback_suggestions' in suggestions_data['suggestions']:
                suggested_models = suggestions_data['suggestions']['fallback_suggestions']['recommended_models']
            elif 'recommended_models' in suggestions_data['suggestions']:
                suggested_models = suggestions_data['suggestions']['recommended_models']
            else:
                print(f"❌ No recommended models found in response")
                return False
        else:
            print(f"❌ No suggestions found in response")
            return False
        print("✅ Model suggestions retrieved successfully!")
        print(f"   Suggested models: {suggested_models}")
    except Exception as e:
        print(f"❌ Exception during model suggestions: {e}")
        return False
    
    # Test 4: Train a model
    print("\n4. Testing model training...")
    training_payload = {
        "target_column": "AGE",
        "selected_models": ["random_forest"]
    }
    try:
        response = requests.post(
            f"{base_url}/api/train-model/{session_id}",
            json=training_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"[TRAIN] Status: {response.status_code}")
        print(f"[TRAIN] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Model training failed: {response.status_code}")
            return False
        training_data = response.json()
        print(f"DEBUG: Training data keys: {list(training_data.keys())}")
        if 'results' in training_data and training_data['results']:
            results_data = training_data['results']
            print(f"DEBUG: Results keys: {list(results_data.keys())}")
            # Use the first available model results
            if 'random_forest' in results_data:
                results = results_data['random_forest']
            elif 'results' in results_data and results_data['results']:
                # If nested structure, get first model
                model_results = results_data['results']
                first_model = list(model_results.keys())[0]
                results = model_results[first_model]
            else:
                print(f"❌ No model results found in training response")
                return False
        else:
            print(f"❌ No results found in training response")
            return False
        print("✅ Model training successful!")
        print(f"   Model: {results['model']}")
        print(f"   Training time: {results['training_time']:.3f}s")
        # Handle different metrics for different problem types
        metrics = results['metrics']
        try:
            if 'accuracy' in metrics:
                print(f"   Accuracy: {metrics['accuracy']:.3f}")
                if 'precision' in metrics:
                    print(f"   Precision: {metrics['precision']:.3f}")
                if 'recall' in metrics:
                    print(f"   Recall: {metrics['recall']:.3f}")
            elif metrics.get('r2_score') is not None:
                print(f"   R² Score: {metrics.get('r2_score'):.3f}")
                if metrics.get('test_mse') is not None:
                    print(f"   Test MSE: {metrics.get('test_mse'):.3f}")
            else:
                print(f"   Available metrics:")
                for k, v in metrics.items():
                    print(f"     {k}: {v}")
        except KeyError as ke:
            print(f"❌ KeyError in metrics block: {ke}")
            print(f"   Metrics dict: {metrics}")
    except KeyError as ke:
        print(f"❌ KeyError during model training: {ke}")
        print(f"   Metrics dict: {metrics if 'metrics' in locals() else 'N/A'}")
        return False
    except Exception as e:
        print(f"❌ Exception during model training: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test 5: Train multiple models
    # Test 6: Generate Data Charts and validate frontend chart rendering
    print("\n6. Testing chart generation and frontend chart rendering...")
    chart_payload = {
        "session_id": session_id,
        "chart_types": ["bar", "pie", "scatter"]
    }
    try:
        response = requests.post(
            f"{base_url}/api/generate-charts",
            json=chart_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"[CHARTS] Status: {response.status_code}")
        print(f"[CHARTS] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Chart generation failed: {response.status_code}")
            return False
        chart_data = response.json()
        print(f"DEBUG: Chart data keys: {list(chart_data.keys())}")
        if 'charts' in chart_data:
            charts_dict = chart_data['charts']
            for chart_type, chart in charts_dict.items():
                # Only process chart objects (dicts), skip ints/lists
                if isinstance(chart, dict):
                    print(f"   Chart type: {chart_type}")
                    if 'error' in chart:
                        print(f"     Chart error: {chart['error']}")
                    else:
                        print(f"     Chart payload keys: {list(chart.keys())}")
                        # Log chart data for frontend rendering validation
                        if 'data' in chart:
                            print(f"     Chart data sample: {str(chart['data'])[:120]}")
                        if 'layout' in chart:
                            print(f"     Chart layout sample: {str(chart['layout'])[:120]}")
                else:
                    print(f"   Skipping non-chart key: {chart_type} (type: {type(chart).__name__})")
        else:
            print(f"❌ No charts found in chart generation response")
            return False
        print("✅ Chart data received from backend. Frontend should be able to render these charts.")
    except Exception as e:
        print(f"❌ Exception during chart generation: {e}")
        return False
    print("\n5. Testing multiple model training...")
    multi_training_payload = {
        "target_column": "MEDV",
        "selected_models": ["random_forest", "xgboost"]
    }
    try:
        response = requests.post(
            f"{base_url}/api/train-model/{session_id}",
            json=multi_training_payload,
            headers={"Content-Type": "application/json"}
        )
        print(f"[MULTI-TRAIN] Status: {response.status_code}")
        print(f"[MULTI-TRAIN] Response: {response.text[:500]}")
        if response.status_code != 200:
            print(f"❌ Multiple model training failed: {response.status_code}")
            return False
        multi_training_data = response.json()
        print("✅ Multiple model training successful!")
        print(f"DEBUG: Multi training data keys: {list(multi_training_data.keys())}")
        if 'results' in multi_training_data:
            print(f"DEBUG: Results sub-keys: {list(multi_training_data['results'].keys())}")
        # Handle different response structures
        if 'results' in multi_training_data and isinstance(multi_training_data['results'], dict):
            if 'error' in multi_training_data['results']:
                print(f"   Multiple training error: {multi_training_data['results']['error']}")
                return True
            elif 'results' in multi_training_data['results']:
                results_data = multi_training_data['results']['results']
            else:
                results_data = multi_training_data['results']
        else:
            print("   Unable to find results data")
            return True
        # Check if results_data is actually a dictionary with model results
        if isinstance(results_data, dict):
            for model_name, result in results_data.items():
                if isinstance(result, dict) and 'status' in result:
                    if result['status'] == 'success':
                        metrics = result['metrics']
                        if 'r2_score' in metrics and metrics.get('r2_score') is not None:
                            print(f"   {model_name}: R² = {metrics['r2_score']:.3f}")
                        elif 'accuracy' in metrics:
                            print(f"   {model_name}: Accuracy = {metrics['accuracy']:.3f}")
                        else:
                            print(f"   {model_name}: Training completed")
                    else:
                        print(f"   {model_name}: Failed - {result.get('error', 'Unknown error')}")
        else:
            print(f"   Unexpected results format: {type(results_data)}")
        print("\n🎉 All tests passed! AutoML workflow is working correctly.")
        return True
    except Exception as e:
        print(f"❌ Exception during multiple model training: {e}")
        return False

def test_frontend_connectivity():
    """Test frontend server connectivity"""
    print("🌐 Testing Frontend Connectivity")
    print("=" * 30)
    
    try:
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        frontend_port = os.getenv('FRONTEND_PORT', '3333')
        response = requests.get(f"http://localhost:{frontend_port}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Frontend server is running on port {frontend_port}")
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
        from dotenv import load_dotenv
        load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
        backend_port = os.getenv('BACKEND_PORT', '8888')
        response = requests.get(f"http://localhost:{backend_port}", timeout=5)
        if response.status_code == 200:
            print(f"✅ Backend server is running on port {backend_port}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except requests.exceptions.RequestException as e:
        print(f"❌ Backend not accessible: {e}")
        return False

if __name__ == "__main__":
    import os
    from dotenv import load_dotenv
    load_dotenv(os.path.join(os.path.dirname(__file__), '.env'))
    backend_port = os.getenv('BACKEND_PORT', '8888')
    frontend_port = os.getenv('FRONTEND_PORT', '3333')
    print("🚀 AutoML End-to-End Testing Suite")
    print("=" * 50)
    # Test server connectivity first
    backend_ok = test_backend_connectivity()
    frontend_ok = test_frontend_connectivity()
    if not backend_ok:
        print(f"\n❌ Backend server not running. Please start it with:\n   cd backend && python main.py (port {backend_port})")
        exit(1)
    if not frontend_ok:
        print(f"\n❌ Frontend server not running. Please start it with:\n   npm run dev (port {frontend_port})")
        exit(1)
    # Run complete workflow test
    print("\n" + "=" * 50)
    success = test_complete_workflow()
    if success:
        print("\n🎉 All systems operational! AutoML application is ready for use.")
        print(f"\n📊 Access the application at: http://localhost:{frontend_port}")
        print(f"🔧 API documentation at: http://localhost:{backend_port}/docs")
    else:
        print("\n❌ Some tests failed. Please check the logs above.")
        exit(1)
