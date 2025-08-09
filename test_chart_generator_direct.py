#!/usr/bin/env python3
"""
Test chart generator directly to isolate the issue
"""

import sys
import os
sys.path.append('/Users/kulbirminhas/Documents/Repo/projects/automl/backend')

import pandas as pd
from utils.chart_generator import ChartGenerator

def test_chart_generator_directly():
    """Test the chart generator with sample data"""
    print("🧪 Testing Chart Generator Directly")
    print("=" * 40)
    
    try:
        # Load sample data
        df = pd.read_csv('/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv')
        print(f"✅ Sample data loaded: {df.shape}")
        print(f"Columns: {list(df.columns)}")
        print(f"Data types:\n{df.dtypes}")
        
        # Initialize chart generator
        chart_gen = ChartGenerator()
        print("✅ Chart generator initialized")
        
        # Test chart generation
        print("\n📊 Testing chart generation...")
        charts = chart_gen.generate_charts(df, chart_types=["correlation"])
        
        print(f"Charts result type: {type(charts)}")
        print(f"Charts keys: {list(charts.keys())}")
        
        if 'error' in charts:
            print(f"❌ Error in chart generation: {charts['error']}")
            return False
        
        if 'charts' in charts:
            print(f"Generated chart types: {list(charts['charts'].keys())}")
            
            if 'correlation' in charts['charts']:
                corr_chart = charts['charts']['correlation']
                print(f"Correlation chart keys: {list(corr_chart.keys())}")
                
                if 'heatmap' in corr_chart:
                    print("✅ Heatmap generated successfully!")
                else:
                    print("⚠️ No heatmap in correlation chart")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_chart_generator_directly()
