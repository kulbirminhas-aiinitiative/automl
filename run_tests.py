#!/usr/bin/env python3
"""
Master AutoML Testing Suite
Runs comprehensive tests of the AutoML application including:
- Dataset downloads
- API backend testing
- Frontend workflow testing
- Performance benchmarking
"""

import subprocess
import sys
import time
import os
import requests
from pathlib import Path

class AutoMLTestRunner:
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.data_dir = self.base_dir / "data"
        self.frontend_url = "http://localhost:3003"
        self.backend_url = "http://127.0.0.1:8080"
        
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        print("🔍 Checking dependencies...")
        
        missing_deps = []
        
        # Check Python packages
        required_packages = ["requests", "pandas", "numpy", "scikit-learn"]
        for package in required_packages:
            try:
                __import__(package)
                print(f"  ✅ {package}")
            except ImportError:
                print(f"  ❌ {package}")
                missing_deps.append(package)
        
        # Check optional packages
        optional_packages = ["selenium"]
        for package in optional_packages:
            try:
                __import__(package)
                print(f"  ✅ {package} (optional)")
            except ImportError:
                print(f"  ⚠️  {package} (optional - for browser automation)")
        
        if missing_deps:
            print(f"\n❌ Missing required packages: {', '.join(missing_deps)}")
            print("💡 Install with: pip install " + " ".join(missing_deps))
            return False
        
        print("✅ All required dependencies available")
        return True
    
    def check_servers(self):
        """Check if frontend and backend servers are running"""
        print("\n🌐 Checking servers...")
        
        # Check backend
        try:
            response = requests.get(self.backend_url, timeout=5)
            if response.status_code == 200:
                print("  ✅ Backend API running")
                backend_ok = True
            else:
                print(f"  ❌ Backend API returned status {response.status_code}")
                backend_ok = False
        except requests.exceptions.RequestException:
            print("  ❌ Backend API not accessible")
            backend_ok = False
        
        # Check frontend
        try:
            response = requests.get(self.frontend_url, timeout=5)
            if response.status_code == 200:
                print("  ✅ Frontend running")
                frontend_ok = True
            else:
                print(f"  ❌ Frontend returned status {response.status_code}")
                frontend_ok = False
        except requests.exceptions.RequestException:
            print("  ❌ Frontend not accessible")
            frontend_ok = False
        
        if not backend_ok:
            print("\n🚀 To start backend:")
            print("  cd backend && uvicorn main:app --reload --host 127.0.0.1 --port 8080")
        
        if not frontend_ok:
            print("\n🚀 To start frontend:")
            print("  npm run dev -- --port 3003")
        
        return backend_ok and frontend_ok
    
    def run_script(self, script_name, description):
        """Run a Python script and return success status"""
        script_path = self.base_dir / script_name
        
        if not script_path.exists():
            print(f"❌ Script not found: {script_path}")
            return False
        
        print(f"\n🚀 Running {description}...")
        print(f"📁 Script: {script_name}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(script_path)],
                cwd=self.base_dir,
                capture_output=True,
                text=True,
                timeout=300  # 5 minute timeout
            )
            
            if result.returncode == 0:
                print(f"✅ {description} completed successfully")
                if result.stdout:
                    print("📄 Output:")
                    print(result.stdout)
                return True
            else:
                print(f"❌ {description} failed with exit code {result.returncode}")
                if result.stderr:
                    print("⚠️  Error output:")
                    print(result.stderr)
                return False
                
        except subprocess.TimeoutExpired:
            print(f"⏰ {description} timed out after 5 minutes")
            return False
        except Exception as e:
            print(f"❌ Error running {description}: {e}")
            return False
    
    def run_dataset_download(self):
        """Download test datasets"""
        return self.run_script("download_test_datasets.py", "Dataset Download")
    
    def run_api_tests(self):
        """Run API backend tests"""
        return self.run_script("test_automl_api.py", "API Backend Tests")
    
    def run_frontend_tests(self):
        """Run frontend tests"""
        print("\n🖥️  Frontend Testing")
        print("=" * 40)
        print("The frontend tests can be run in two modes:")
        print("1. 🤖 Automated (requires Selenium)")
        print("2. 📋 Manual (step-by-step instructions)")
        
        choice = input("\nChoose testing mode (1=automated, 2=manual, s=skip): ").strip().lower()
        
        if choice in ['s', 'skip']:
            print("⏭️  Skipping frontend tests")
            return True
        elif choice in ['1', 'automated']:
            return self.run_script("test_frontend.py", "Frontend Automated Tests")
        else:
            return self.run_script("test_frontend.py", "Frontend Manual Tests")
    
    def show_test_summary(self):
        """Show summary of available datasets and tests"""
        print("\n📊 Test Summary")
        print("=" * 40)
        
        # Count datasets
        if self.data_dir.exists():
            csv_files = list(self.data_dir.glob("*.csv"))
            print(f"📁 Available datasets: {len(csv_files)}")
            for csv_file in csv_files[:5]:  # Show first 5
                try:
                    import pandas as pd
                    df = pd.read_csv(csv_file)
                    print(f"  📊 {csv_file.name}: {df.shape[0]} rows × {df.shape[1]} columns")
                except:
                    print(f"  📊 {csv_file.name}: available")
            
            if len(csv_files) > 5:
                print(f"  ... and {len(csv_files) - 5} more")
        else:
            print("📁 No datasets found")
        
        # Show URLs
        print(f"\n🌐 Application URLs:")
        print(f"  Frontend: {self.frontend_url}")
        print(f"  Backend API: {self.backend_url}")
        print(f"  API Docs: {self.backend_url}/docs")
    
    def run_comprehensive_tests(self):
        """Run the complete testing suite"""
        print("🧪 AutoML Comprehensive Testing Suite")
        print("=" * 60)
        print("This will test the complete AutoML application workflow")
        print("including data upload, AI analysis, model training, and predictions.")
        
        # Step 1: Check dependencies
        if not self.check_dependencies():
            return False
        
        # Step 2: Check servers
        if not self.check_servers():
            print("\n⚠️  Servers not running. Please start them first.")
            return False
        
        # Step 3: Download datasets
        print("\n" + "="*60)
        datasets_ok = self.run_dataset_download()
        
        # Step 4: Run API tests
        print("\n" + "="*60)
        api_ok = self.run_api_tests() if datasets_ok else False
        
        # Step 5: Run frontend tests
        print("\n" + "="*60)
        frontend_ok = self.run_frontend_tests() if api_ok else False
        
        # Step 6: Show summary
        print("\n" + "="*60)
        self.show_test_summary()
        
        # Final results
        print("\n🏁 Testing Results")
        print("=" * 40)
        print(f"📦 Dataset Download: {'✅ Pass' if datasets_ok else '❌ Fail'}")
        print(f"🔧 API Backend Tests: {'✅ Pass' if api_ok else '❌ Fail'}")
        print(f"🖥️  Frontend Tests: {'✅ Pass' if frontend_ok else '❌ Fail'}")
        
        overall_success = datasets_ok and api_ok and frontend_ok
        print(f"\n🎯 Overall Result: {'✅ SUCCESS' if overall_success else '❌ SOME TESTS FAILED'}")
        
        if overall_success:
            print("\n🎉 AutoML application is fully functional!")
            print("You can now use it for real machine learning projects.")
        else:
            print("\n🔧 Some tests failed. Check the output above for details.")
        
        return overall_success


def main():
    """Main entry point"""
    runner = AutoMLTestRunner()
    
    if len(sys.argv) > 1:
        command = sys.argv[1].lower()
        
        if command == "deps":
            runner.check_dependencies()
        elif command == "servers":
            runner.check_servers()
        elif command == "datasets":
            runner.run_dataset_download()
        elif command == "api":
            runner.run_api_tests()
        elif command == "frontend":
            runner.run_frontend_tests()
        elif command == "summary":
            runner.show_test_summary()
        else:
            print("Usage: python run_tests.py [deps|servers|datasets|api|frontend|summary]")
    else:
        # Run comprehensive tests
        runner.run_comprehensive_tests()


if __name__ == "__main__":
    main()
