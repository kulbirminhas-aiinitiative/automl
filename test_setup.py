#!/usr/bin/env python3
"""Test script for AutoML application setup with Boston housing dataset"""

import pandas as pd
import requests
import json

def main():
    print('🏠 Testing AutoML Application with Boston Housing Dataset')
    print('=' * 60)

    # Read the dataset
    df = pd.read_csv('data/boston.csv')
    print(f'📊 Dataset loaded: {df.shape[0]} rows, {df.shape[1]} columns')
    print(f'📋 Columns: {list(df.columns)}')
    print(f'🎯 Target variable: MEDV (Median home value)')
    print()

    # Show first few rows
    print('📝 Sample data:')
    print(df.head())
    print()

    # Basic dataset info
    print('📈 Dataset Summary:')
    print(f'• Target variable (MEDV) range: ${df["MEDV"].min():.1f}k - ${df["MEDV"].max():.1f}k')
    print(f'• Average home value: ${df["MEDV"].mean():.1f}k')
    print(f'• Missing values: {df.isnull().sum().sum()}')
    print()

    # Test API connectivity
    try:
        response = requests.get('http://127.0.0.1:8080/')
        if response.status_code == 200:
            print('✅ Backend API is accessible')
            api_status = response.json()
            print(f'📡 API Status: {api_status["message"]}')
            print(f'⏰ Server time: {api_status["timestamp"]}')
        else:
            print('❌ Backend API not responding properly')
    except Exception as e:
        print(f'❌ Failed to connect to backend: {e}')

    print()
    print('🚀 Ready for complete AutoML workflow testing!')
    print('📋 Next steps:')
    print('1. Upload boston.csv through the web interface at http://localhost:3003')
    print('2. Select MEDV as target variable')
    print('3. Run AI analysis and model training')
    print('4. View predictions and model performance')
    print()
    print('🌐 Frontend URL: http://localhost:3003')
    print('🔧 Backend API: http://127.0.0.1:8080')

if __name__ == "__main__":
    main()
