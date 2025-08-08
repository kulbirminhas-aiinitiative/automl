#!/usr/bin/env python3
"""
Comprehensive AutoML API Testing Script
Tests the complete AutoML workflow including data upload, analysis, and model training
"""

import requests
import pandas as pd
import json
import time
import os
from pathlib import Path
import sys

class AutoMLTester:
    def __init__(self, base_url="http://127.0.0.1:8080"):
        self.base_url = base_url
        self.session_id = None
        self.results = {}
        
    def check_api_health(self):
        """Check if the API is running"""
        try:
            response = requests.get(f"{self.base_url}/")
            if response.status_code == 200:
                print("✅ API is healthy and running")
                return True
            else:
                print(f"❌ API returned status code: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to API. Make sure the backend is running.")
            return False
        except Exception as e:
            print(f"❌ Error checking API health: {e}")
            return False
    
    def upload_dataset(self, file_path):
        """Upload a dataset file to the API"""
        print(f"\n📤 Uploading dataset: {file_path}")
        
        if not os.path.exists(file_path):
            print(f"❌ File not found: {file_path}")
            return False
        
        try:
            with open(file_path, 'rb') as file:
                files = {'file': (os.path.basename(file_path), file, 'text/csv')}
                response = requests.post(f"{self.base_url}/api/upload-data", files=files)
            
            if response.status_code == 200:
                result = response.json()
                self.session_id = result.get('session_id')
                print(f"✅ Dataset uploaded successfully")
                print(f"📊 Session ID: {self.session_id}")
                print(f"📋 Dataset shape: {result.get('shape', 'Unknown')}")
                print(f"📈 Columns: {result.get('columns', [])}")
                self.results['upload'] = result
                return True
            else:
                print(f"❌ Upload failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error uploading dataset: {e}")
            return False
    
    def analyze_dataset(self, target_column):
        """Request AI analysis of the dataset"""
        print(f"\n🤖 Requesting AI analysis with target: {target_column}")
        
        if not self.session_id:
            print("❌ No active session. Upload a dataset first.")
            return False
        
        try:
            # Use suggest-models endpoint which includes analysis
            response = requests.post(f"{self.base_url}/api/suggest-models/{self.session_id}?target_column={target_column}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ AI analysis completed")
                print(f"🎯 Target column: {result.get('target_column', 'Unknown')}")
                suggestions = result.get('suggestions', {})
                if isinstance(suggestions, dict):
                    print(f"💡 AI insights: {suggestions.get('reasoning', 'No insights available')}")
                self.results['analysis'] = result
                return True
            else:
                print(f"❌ Analysis failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during analysis: {e}")
            return False
    
    def train_models(self, model_configs=None):
        """Train ML models"""
        print(f"\n🚀 Starting model training")
        
        if not self.session_id:
            print("❌ No active session. Upload and analyze a dataset first.")
            return False
        
        try:
            # Get target column from analysis results
            target_column = None
            if 'analysis' in self.results:
                target_column = self.results['analysis'].get('target_column')
            
            if not target_column:
                print("❌ No target column specified. Run analysis first.")
                return False
            
            payload = {
                "target_column": target_column,
                "model_type": "auto"  # Let the API choose
            }
            
            response = requests.post(f"{self.base_url}/api/train-model/{self.session_id}", json=payload)
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Model training completed")
                
                # Display training results
                training_result = result.get('training_result', {})
                if training_result:
                    print(f"🏆 Model: {training_result.get('model_type', 'Unknown')}")
                    print(f"📊 Score: {training_result.get('score', 'N/A')}")
                
                self.results['training'] = result
                return True
            else:
                print(f"❌ Training failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error during training: {e}")
            return False
    
    def get_predictions(self, sample_data=None):
        """Get predictions from the best model"""
        print(f"\n🔮 Getting predictions")
        
        if not self.session_id:
            print("❌ No active session. Train models first.")
            return False
        
        try:
            # Just get session data which includes predictions
            response = requests.get(f"{self.base_url}/api/session/{self.session_id}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Session data retrieved")
                
                # Check if model was trained
                if 'training_result' in result:
                    training_result = result['training_result']
                    print(f"🎯 Model: {training_result.get('model_type', 'Unknown')}")
                    print(f"📊 Score: {training_result.get('score', 'N/A')}")
                
                self.results['predictions'] = result
                return True
            else:
                print(f"❌ Session retrieval failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error getting predictions: {e}")
            return False
    
    def generate_charts(self):
        """Generate visualization charts"""
        print(f"\n📊 Generating charts")
        
        if not self.session_id:
            print("❌ No active session.")
            return False
        
        try:
            response = requests.get(f"{self.base_url}/api/generate-charts/{self.session_id}")
            
            if response.status_code == 200:
                result = response.json()
                print("✅ Charts generated")
                charts = result.get('charts', [])
                print(f"📈 Generated {len(charts)} charts")
                for chart in charts:
                    print(f"  📊 {chart.get('title', 'Untitled Chart')}")
                self.results['charts'] = result
                return True
            else:
                print(f"❌ Chart generation failed with status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ Error generating charts: {e}")
            return False
    
    def run_complete_test(self, dataset_path, target_column):
        """Run the complete AutoML workflow test"""
        print("🧪 Starting Complete AutoML Workflow Test")
        print("=" * 60)
        
        # Step 1: Check API health
        if not self.check_api_health():
            return False
        
        # Step 2: Upload dataset
        if not self.upload_dataset(dataset_path):
            return False
        
        # Step 3: Analyze dataset
        if not self.analyze_dataset(target_column):
            return False
        
        # Step 4: Train models
        if not self.train_models():
            return False
        
        # Step 5: Get predictions
        if not self.get_predictions():
            return False
        
        # Step 6: Generate charts
        if not self.generate_charts():
            return False
        
        print("\n🎉 Complete AutoML workflow test completed successfully!")
        self.print_summary()
        return True
    
    def print_summary(self):
        """Print a summary of all test results"""
        print("\n📋 Test Summary")
        print("=" * 40)
        
        if 'upload' in self.results:
            upload = self.results['upload']
            print(f"📤 Dataset: {upload.get('shape', 'Unknown')} shape")
        
        if 'analysis' in self.results:
            analysis = self.results['analysis']
            print(f"🎯 Problem: {analysis.get('problem_type', 'Unknown')}")
        
        if 'training' in self.results:
            training = self.results['training']
            models = training.get('models', [])
            if models:
                best_score = max(model.get('score', 0) for model in models)
                print(f"🏆 Best Score: {best_score:.4f}")
        
        if 'predictions' in self.results:
            predictions = self.results['predictions']
            print(f"🔮 Best Model: {predictions.get('best_model', 'Unknown')}")
        
        if 'charts' in self.results:
            charts = self.results['charts']
            chart_count = len(charts.get('charts', []))
            print(f"📊 Charts: {chart_count} generated")


def main():
    """Main testing function"""
    # Initialize tester
    tester = AutoMLTester()
    
    # Test datasets
    test_datasets = [
        {
            "name": "Boston Housing",
            "path": "data/boston.csv",
            "target": "MEDV",
            "description": "Predict house prices in Boston"
        },
        {
            "name": "House Prices",
            "path": "data/train.csv",
            "target": "TARGET(PRICE_IN_LACS)",
            "description": "Predict house sale prices"
        }
    ]
    
    print("🤖 AutoML API Testing Suite")
    print("=" * 50)
    
    # Test each dataset
    for i, dataset in enumerate(test_datasets, 1):
        print(f"\n🧪 Test {i}/{len(test_datasets)}: {dataset['name']}")
        print(f"📝 Description: {dataset['description']}")
        
        if os.path.exists(dataset['path']):
            success = tester.run_complete_test(dataset['path'], dataset['target'])
            if success:
                print(f"✅ {dataset['name']} test completed successfully")
            else:
                print(f"❌ {dataset['name']} test failed")
        else:
            print(f"⚠️  Dataset not found: {dataset['path']}")
        
        print("-" * 50)
    
    print("\n🏁 All tests completed!")


if __name__ == "__main__":
    main()
