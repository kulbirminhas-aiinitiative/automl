#!/usr/bin/env python3
"""
Dataset Downloader for AutoML Testing
Downloads various machine learning datasets for testing AutoML functionality
"""

import os
import pandas as pd
import numpy as np
from sklearn.datasets import make_regression, make_classification, load_diabetes, load_wine
import requests
from pathlib import Path

class DatasetDownloader:
    def __init__(self, data_dir="data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
    def download_from_url(self, url, filename, description="Dataset"):
        """Download a dataset from URL"""
        print(f"📥 Downloading {description}...")
        try:
            response = requests.get(url)
            response.raise_for_status()
            
            file_path = self.data_dir / filename
            with open(file_path, 'wb') as f:
                f.write(response.content)
            
            print(f"✅ {description} saved to {file_path}")
            return str(file_path)
        except Exception as e:
            print(f"❌ Failed to download {description}: {e}")
            return None
    
    def create_synthetic_regression_dataset(self):
        """Create a synthetic regression dataset"""
        print("🧪 Creating synthetic regression dataset...")
        
        # Generate synthetic data
        X, y = make_regression(
            n_samples=1000,
            n_features=10,
            n_informative=8,
            noise=0.1,
            random_state=42
        )
        
        # Create feature names
        feature_names = [f"feature_{i+1}" for i in range(X.shape[1])]
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # Save to CSV
        file_path = self.data_dir / "synthetic_regression.csv"
        df.to_csv(file_path, index=False)
        
        print(f"✅ Synthetic regression dataset created: {file_path}")
        print(f"   📊 Shape: {df.shape}")
        print(f"   🎯 Target: regression (continuous values)")
        
        return str(file_path)
    
    def create_synthetic_classification_dataset(self):
        """Create a synthetic classification dataset"""
        print("🧪 Creating synthetic classification dataset...")
        
        # Generate synthetic data
        X, y = make_classification(
            n_samples=1000,
            n_features=15,
            n_informative=10,
            n_redundant=3,
            n_classes=3,
            random_state=42
        )
        
        # Create feature names
        feature_names = [f"feature_{i+1}" for i in range(X.shape[1])]
        
        # Create DataFrame
        df = pd.DataFrame(X, columns=feature_names)
        df['target'] = y
        
        # Save to CSV
        file_path = self.data_dir / "synthetic_classification.csv"
        df.to_csv(file_path, index=False)
        
        print(f"✅ Synthetic classification dataset created: {file_path}")
        print(f"   📊 Shape: {df.shape}")
        print(f"   🎯 Target: classification (3 classes)")
        
        return str(file_path)
    
    def create_diabetes_dataset(self):
        """Create diabetes regression dataset from sklearn"""
        print("🏥 Creating diabetes regression dataset...")
        
        # Load diabetes dataset
        diabetes = load_diabetes()
        
        # Create DataFrame
        df = pd.DataFrame(diabetes.data, columns=diabetes.feature_names)
        df['target'] = diabetes.target
        
        # Save to CSV
        file_path = self.data_dir / "diabetes_regression.csv"
        df.to_csv(file_path, index=False)
        
        print(f"✅ Diabetes regression dataset created: {file_path}")
        print(f"   📊 Shape: {df.shape}")
        print(f"   🎯 Target: diabetes progression (regression)")
        
        return str(file_path)
    
    def create_wine_classification_dataset(self):
        """Create wine classification dataset from sklearn"""
        print("🍷 Creating wine classification dataset...")
        
        # Load wine dataset
        wine = load_wine()
        
        # Create DataFrame
        df = pd.DataFrame(wine.data, columns=wine.feature_names)
        df['target'] = wine.target
        
        # Save to CSV
        file_path = self.data_dir / "wine_classification.csv"
        df.to_csv(file_path, index=False)
        
        print(f"✅ Wine classification dataset created: {file_path}")
        print(f"   📊 Shape: {df.shape}")
        print(f"   🎯 Target: wine type classification (3 classes)")
        
        return str(file_path)
    
    def download_iris_dataset(self):
        """Download the classic Iris dataset"""
        print("🌸 Downloading Iris classification dataset...")
        
        url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/iris.csv"
        return self.download_from_url(url, "iris_classification.csv", "Iris dataset")
    
    def download_tips_dataset(self):
        """Download the tips regression dataset"""
        print("💰 Downloading Tips regression dataset...")
        
        url = "https://raw.githubusercontent.com/mwaskom/seaborn-data/master/tips.csv"
        return self.download_from_url(url, "tips_regression.csv", "Tips dataset")
    
    def download_titanic_dataset(self):
        """Download the Titanic survival dataset"""
        print("🚢 Downloading Titanic classification dataset...")
        
        url = "https://raw.githubusercontent.com/datasciencedojo/datasets/master/titanic.csv"
        return self.download_from_url(url, "titanic_classification.csv", "Titanic dataset")
    
    def create_customer_churn_dataset(self):
        """Create a synthetic customer churn dataset"""
        print("👥 Creating customer churn dataset...")
        
        np.random.seed(42)
        n_samples = 2000
        
        # Generate features
        data = {
            'age': np.random.randint(18, 70, n_samples),
            'tenure_months': np.random.randint(1, 72, n_samples),
            'monthly_charges': np.random.uniform(20, 120, n_samples),
            'total_charges': np.random.uniform(20, 8000, n_samples),
            'contract_type': np.random.choice(['Month-to-month', 'One year', 'Two year'], n_samples),
            'payment_method': np.random.choice(['Electronic check', 'Mailed check', 'Bank transfer', 'Credit card'], n_samples),
            'internet_service': np.random.choice(['DSL', 'Fiber optic', 'No'], n_samples),
            'phone_service': np.random.choice([0, 1], n_samples),
            'multiple_lines': np.random.choice([0, 1], n_samples),
            'online_security': np.random.choice([0, 1], n_samples),
            'tech_support': np.random.choice([0, 1], n_samples),
        }
        
        # Create target based on features (synthetic logic)
        churn_prob = (
            0.1 +  # base probability
            0.3 * (data['contract_type'] == 'Month-to-month').astype(int) +
            0.2 * (data['monthly_charges'] > 80) +
            0.1 * (data['tenure_months'] < 12) +
            0.2 * (data['tech_support'] == 0)
        )
        data['churn'] = np.random.binomial(1, np.clip(churn_prob, 0, 1), n_samples)
        
        # Create DataFrame
        df = pd.DataFrame(data)
        
        # Save to CSV
        file_path = self.data_dir / "customer_churn.csv"
        df.to_csv(file_path, index=False)
        
        print(f"✅ Customer churn dataset created: {file_path}")
        print(f"   📊 Shape: {df.shape}")
        print(f"   🎯 Target: churn prediction (binary classification)")
        
        return str(file_path)
    
    def download_all_datasets(self):
        """Download and create all test datasets"""
        print("📦 AutoML Testing Dataset Collection")
        print("=" * 50)
        
        datasets = []
        
        # Create synthetic datasets
        datasets.append(self.create_synthetic_regression_dataset())
        datasets.append(self.create_synthetic_classification_dataset())
        datasets.append(self.create_customer_churn_dataset())
        
        # Create sklearn datasets
        datasets.append(self.create_diabetes_dataset())
        datasets.append(self.create_wine_classification_dataset())
        
        # Download public datasets
        datasets.append(self.download_iris_dataset())
        datasets.append(self.download_tips_dataset())
        datasets.append(self.download_titanic_dataset())
        
        # Filter out failed downloads
        successful_datasets = [d for d in datasets if d is not None]
        
        print(f"\n✅ Successfully created/downloaded {len(successful_datasets)} datasets")
        print("📋 Available datasets for testing:")
        
        for dataset_path in successful_datasets:
            if os.path.exists(dataset_path):
                df = pd.read_csv(dataset_path)
                filename = os.path.basename(dataset_path)
                print(f"  📊 {filename}: {df.shape[0]} rows × {df.shape[1]} columns")
        
        return successful_datasets


def main():
    """Main function to download all datasets"""
    downloader = DatasetDownloader()
    datasets = downloader.download_all_datasets()
    
    print(f"\n🎯 Ready for AutoML testing with {len(datasets)} datasets!")
    print("Run 'python test_automl_api.py' to start automated testing.")


if __name__ == "__main__":
    main()
