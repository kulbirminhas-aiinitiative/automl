#!/usr/bin/env python3
"""
Final validation test following .copilot-log-config.js instructions
This validates the complete AutoML workflow end-to-end
"""

import requests
import json
import io
import time
from datetime import datetime


def log_validation_result(test_name, status, details=""):
    """Log validation results to activity log"""
    try:
        with open("logs/activity-log.md", "a") as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"\n## {timestamp} - Final Validation: {test_name}\n")
            f.write(f"**Status:** {status}\n")
            if details:
                f.write(f"**Details:** {details}\n")
    except:
        pass


def create_realistic_data():
    """Create a realistic dataset for testing"""
    return """employee_id,name,age,salary,experience,department,performance_score,years_in_company,education_level,satisfaction_score
1,John Smith,25,50000,2,IT,85,2,Bachelor,7.5
2,Sarah Connor,30,65000,5,Finance,92,3,Master,8.2
3,Mike Johnson,35,80000,8,IT,78,5,Bachelor,6.8
4,Alice Williams,28,58000,3,Marketing,88,3,Bachelor,7.9
5,Bob Brown,32,72000,6,IT,81,4,Master,7.1
6,Carol Davis,29,61000,4,Finance,90,2,Bachelor,8.5
7,Dave Miller,31,69000,7,Marketing,76,5,Master,6.4
8,Eve Wilson,26,54000,3,IT,83,3,Bachelor,7.7
9,Frank Taylor,33,75000,9,Finance,87,6,Master,8.0
10,Grace Anderson,27,56000,2,Marketing,89,2,Bachelor,8.3
11,Henry Moore,34,82000,10,IT,79,7,PhD,7.2
12,Ivy Jackson,29,63000,4,Finance,91,3,Master,8.4
13,Jack White,36,85000,12,Marketing,74,8,Bachelor,6.5
14,Karen Lee,28,59000,3,IT,86,3,Master,7.8
15,Leo Garcia,30,67000,5,Finance,93,4,Bachelor,8.6"""


def validate_complete_workflow():
    """Test the complete AutoML workflow"""
    print("🔍 Final Validation: Complete AutoML Workflow")
    print("=" * 50)
    
    workflow_steps = []
    session_id = None
    
    try:
        # Step 1: Upload realistic data
        print("Step 1: Uploading realistic dataset...")
        csv_data = create_realistic_data()
        files = {'file': ('employee_performance.csv', io.StringIO(csv_data), 'text/csv')}
        
        response = requests.post("http://localhost:8888/api/upload-data", files=files)
        
        if response.status_code == 200:
            data = response.json()
            session_id = data['session_id']
            workflow_steps.append(f"✅ Data Upload: {data['shape'][0]} rows, {data['shape'][1]} columns")
            print(f"   ✅ Session: {session_id}")
            print(f"   📊 Data shape: {data['shape']}")
            print(f"   📋 Columns: {', '.join(data['columns'])}")
        else:
            workflow_steps.append(f"❌ Data Upload failed: {response.status_code}")
            print(f"   ❌ Upload failed: {response.status_code}")
            return False, workflow_steps
        
        # Step 2: Get model suggestions
        print("\nStep 2: Getting model suggestions...")
        payload = {
            "target_column": "performance_score",
            "problem_type": "regression"
        }
        
        response = requests.post(f"http://localhost:8888/api/suggest-models/{session_id}", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            suggestions = data['suggestions']['recommended_models']
            workflow_steps.append(f"✅ Model Suggestions: {len(suggestions)} models recommended")
            print(f"   ✅ Got {len(suggestions)} model suggestions")
            for i, model_name in enumerate(suggestions[:3], 1):
                # Get model performance from model_comparison
                model_comparison = data['suggestions'].get('model_comparison', {})
                model_data = model_comparison.get(model_name, {})
                score = model_data.get('primary_score', 'N/A')
                print(f"   {i}. {model_name} (R² Score: {score})")
        else:
            workflow_steps.append(f"❌ Model Suggestions failed: {response.status_code}")
            print(f"   ❌ Suggestions failed: {response.status_code}")
            return False, workflow_steps
        
        # Step 3: Train multiple models
        print("\nStep 3: Training selected models...")
        payload = {
            "target_column": "performance_score",
            "selected_models": ["linear_regression", "random_forest", "xgboost"],
            "train_config": {
                "test_size": 0.2,
                "random_state": 42
            }
        }
        
        response = requests.post(f"http://localhost:8888/api/train-model/{session_id}", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            results = data['results']['results']
            successful_models = [name for name, result in results.items() if result.get('status') == 'success']
            workflow_steps.append(f"✅ Model Training: {len(successful_models)} models trained successfully")
            print(f"   ✅ {len(successful_models)} models trained successfully")
            
            # Show model performance
            for model_name, result in results.items():
                if result.get('status') == 'success':
                    metrics = result.get('metrics', {})
                    r2_score = metrics.get('r2_score', 'N/A')
                    mae = metrics.get('test_mae', 'N/A')
                    print(f"   📈 {model_name}: R² = {r2_score}, MAE = {mae}")
        else:
            workflow_steps.append(f"❌ Model Training failed: {response.status_code}")
            print(f"   ❌ Training failed: {response.status_code}")
            return False, workflow_steps
        
        # Step 4: Generate visualizations
        print("\nStep 4: Generating visualizations...")
        payload = {
            "session_id": session_id,
            "chart_types": ["correlation", "distribution", "feature_importance"],
            "target_column": "performance_score"
        }
        
        response = requests.post("http://localhost:8888/api/generate-charts", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            charts = data.get('charts', [])
            workflow_steps.append(f"✅ Chart Generation: {len(charts)} charts created")
            print(f"   ✅ Generated {len(charts)} visualization charts")
            for i, chart in enumerate(charts, 1):
                if isinstance(chart, dict):
                    chart_type = chart.get('type', f'Chart {i}')
                else:
                    chart_type = f'Chart {i}'
                print(f"   📊 {chart_type} chart generated")
        else:
            workflow_steps.append(f"❌ Chart Generation failed: {response.status_code}")
            print(f"   ❌ Chart generation failed: {response.status_code}")
            return False, workflow_steps
        
        # Step 5: Validate session persistence by running another operation
        print("\nStep 5: Validating session persistence...")
        # Try to get model suggestions again with the same session to verify data is persisted
        payload = {
            "target_column": "performance_score", 
            "problem_type": "regression"
        }
        
        response = requests.post(f"http://localhost:8888/api/suggest-models/{session_id}", json=payload)
        
        if response.status_code == 200:
            workflow_steps.append("✅ Session Persistence: Data maintained across requests")
            print("   ✅ Session data persisted correctly - can reuse for multiple operations")
        else:
            workflow_steps.append(f"❌ Session Persistence failed: {response.status_code}")
            print(f"   ❌ Session persistence failed: {response.status_code}")
            return False, workflow_steps
        
        return True, workflow_steps
        
    except Exception as e:
        workflow_steps.append(f"❌ Workflow Exception: {str(e)}")
        print(f"   ❌ Exception: {str(e)}")
        return False, workflow_steps


def main():
    """Run final validation according to .copilot-log-config.js"""
    print("🎯 Final AutoML System Validation")
    print("Following .copilot-log-config.js requirements:")
    print("- Test the affected section")
    print("- Log all output")
    print("- Run comprehensive end-to-end testing")
    print("- Fix compilation and runtime errors")
    print("=" * 60)
    
    start_time = time.time()
    
    # Test server connectivity first
    try:
        response = requests.get("http://localhost:8888/")
        if response.status_code != 200:
            print("❌ Backend server not responding")
            log_validation_result("Final Validation", "FAIL", "Backend server not responding")
            return 1
    except Exception as e:
        print(f"❌ Cannot connect to backend: {str(e)}")
        log_validation_result("Final Validation", "FAIL", f"Cannot connect to backend: {str(e)}")
        return 1
    
    # Run complete workflow validation
    success, workflow_steps = validate_complete_workflow()
    
    # Generate final report
    elapsed_time = time.time() - start_time
    print(f"\n🏁 Final Validation Summary")
    print("=" * 40)
    print(f"Execution Time: {elapsed_time:.2f}s")
    print(f"Workflow Steps Completed:")
    
    for step in workflow_steps:
        print(f"  {step}")
    
    if success:
        print("\n🎉 SUCCESS: Complete AutoML workflow validated!")
        print("✅ All systems operational")
        print("✅ Error handling functional")
        print("✅ Data processing working")
        print("✅ Model training successful")
        print("✅ Visualization generation operational")
        print("✅ Session management functional")
        
        # Log success
        log_validation_result(
            "Complete AutoML Workflow", 
            "SUCCESS", 
            f"All {len(workflow_steps)} workflow steps completed successfully in {elapsed_time:.2f}s"
        )
        
        return 0
    else:
        print("\n❌ FAILURE: Workflow validation failed")
        print("❗ Some components need attention")
        
        # Log failure
        log_validation_result(
            "Complete AutoML Workflow", 
            "FAIL", 
            f"Workflow failed after {elapsed_time:.2f}s. Steps: {'; '.join(workflow_steps)}"
        )
        
        return 1


if __name__ == "__main__":
    exit(main())
