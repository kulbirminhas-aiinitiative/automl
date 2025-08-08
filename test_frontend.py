#!/usr/bin/env python3
"""
Frontend Testing Script for AutoML Application
Simulates user interactions with the web interface using Selenium
"""

try:
    from selenium import webdriver
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait, Select
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.options import Options
    SELENIUM_AVAILABLE = True
except ImportError:
    SELENIUM_AVAILABLE = False

import time
import os
import pandas as pd
from pathlib import Path

class AutoMLFrontendTester:
    def __init__(self, frontend_url="http://localhost:3003", headless=False):
        self.frontend_url = frontend_url
        self.headless = headless
        self.driver = None
        
        if not SELENIUM_AVAILABLE:
            print("⚠️  Selenium not available. Install with: pip install selenium")
            print("💡 This script will provide manual testing instructions instead.")
    
    def setup_driver(self):
        """Setup Chrome WebDriver"""
        if not SELENIUM_AVAILABLE:
            return False
            
        try:
            chrome_options = Options()
            if self.headless:
                chrome_options.add_argument("--headless")
            chrome_options.add_argument("--no-sandbox")
            chrome_options.add_argument("--disable-dev-shm-usage")
            
            self.driver = webdriver.Chrome(options=chrome_options)
            return True
        except Exception as e:
            print(f"❌ Failed to setup Chrome driver: {e}")
            print("💡 Please install ChromeDriver: https://chromedriver.chromium.org/")
            return False
    
    def test_dataset_upload(self, dataset_path, target_column):
        """Test uploading a dataset through the web interface"""
        if not SELENIUM_AVAILABLE or not self.driver:
            self.manual_test_instructions(dataset_path, target_column)
            return False
            
        try:
            print(f"🌐 Opening AutoML application at {self.frontend_url}")
            self.driver.get(self.frontend_url)
            
            # Wait for page to load
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            print("📤 Testing file upload...")
            
            # Find file input
            file_input = self.driver.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(os.path.abspath(dataset_path))
            
            # Wait for upload to complete
            time.sleep(3)
            
            # Select target column
            print(f"🎯 Selecting target column: {target_column}")
            target_select = Select(self.driver.find_element(By.ID, "target-column"))
            target_select.select_by_value(target_column)
            
            # Click analyze button
            analyze_button = self.driver.find_element(By.ID, "analyze-button")
            analyze_button.click()
            
            # Wait for analysis to complete
            print("🤖 Waiting for AI analysis...")
            WebDriverWait(self.driver, 30).until(
                EC.presence_of_element_located((By.CLASS_NAME, "analysis-results"))
            )
            
            # Click train models button
            train_button = self.driver.find_element(By.ID, "train-button")
            train_button.click()
            
            # Wait for training to complete
            print("🚀 Waiting for model training...")
            WebDriverWait(self.driver, 60).until(
                EC.presence_of_element_located((By.CLASS_NAME, "training-results"))
            )
            
            print("✅ Frontend test completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Frontend test failed: {e}")
            return False
    
    def manual_test_instructions(self, dataset_path, target_column):
        """Provide manual testing instructions"""
        print(f"\n📋 Manual Testing Instructions for {os.path.basename(dataset_path)}")
        print("=" * 60)
        print(f"1. 🌐 Open your browser and go to: {self.frontend_url}")
        print(f"2. 📤 Upload the dataset file: {dataset_path}")
        print(f"3. 🎯 Select target column: {target_column}")
        print(f"4. 🤖 Click 'Analyze Data' and wait for AI insights")
        print(f"5. 🚀 Click 'Train Models' and wait for training to complete")
        print(f"6. 📊 Review the results and model performance")
        print(f"7. 🔮 Test predictions with sample data")
        print(f"8. 📈 View generated charts and visualizations")
        print("=" * 60)
        
        # Show dataset preview
        if os.path.exists(dataset_path):
            df = pd.read_csv(dataset_path)
            print(f"\n📊 Dataset Preview ({os.path.basename(dataset_path)}):")
            print(f"   📏 Shape: {df.shape}")
            print(f"   📋 Columns: {list(df.columns)}")
            print(f"   🎯 Target: {target_column}")
            print(f"   📝 Sample data:")
            print(df.head(3).to_string(index=False))
    
    def close(self):
        """Close the browser"""
        if self.driver:
            self.driver.quit()


def run_frontend_tests():
    """Run frontend tests for multiple datasets"""
    # Test datasets
    test_datasets = [
        {
            "name": "Boston Housing",
            "path": "data/boston.csv",
            "target": "MEDV"
        },
        {
            "name": "Synthetic Regression",
            "path": "data/synthetic_regression.csv",
            "target": "target"
        },
        {
            "name": "Wine Classification",
            "path": "data/wine_classification.csv",
            "target": "target"
        },
        {
            "name": "Customer Churn",
            "path": "data/customer_churn.csv",
            "target": "churn"
        }
    ]
    
    print("🖥️  AutoML Frontend Testing Suite")
    print("=" * 50)
    
    tester = AutoMLFrontendTester()
    
    if SELENIUM_AVAILABLE:
        if tester.setup_driver():
            print("✅ Browser automation enabled")
        else:
            print("⚠️  Browser automation disabled - using manual instructions")
    
    for i, dataset in enumerate(test_datasets, 1):
        print(f"\n🧪 Frontend Test {i}/{len(test_datasets)}: {dataset['name']}")
        
        if os.path.exists(dataset['path']):
            tester.test_dataset_upload(dataset['path'], dataset['target'])
        else:
            print(f"⚠️  Dataset not found: {dataset['path']}")
            print("💡 Run 'python download_test_datasets.py' first")
        
        print("-" * 50)
        
        if SELENIUM_AVAILABLE and tester.driver:
            input("Press Enter to continue to next test...")
    
    tester.close()
    print("\n🏁 All frontend tests completed!")


if __name__ == "__main__":
    run_frontend_tests()
