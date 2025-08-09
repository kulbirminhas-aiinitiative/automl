#!/usr/bin/env python3
"""
Test the enhanced model suggestions with performance comparison
"""

import requests
import json

def test_enhanced_suggestions():
    """Test the enhanced model suggestions endpoint"""
    base_url = "http://localhost:8000"
    
    print("🎯 Testing Enhanced Model Suggestions")
    print("=" * 50)
    
    # First upload a file
    file_path = "/Users/kulbirminhas/Documents/Repo/projects/automl/sample_data.csv"
    with open(file_path, 'rb') as f:
        files = {'file': f}
        response = requests.post(f"{base_url}/api/upload-data", files=files)
    
    session_id = response.json()['session_id']
    print(f"✅ Session created: {session_id}")
    
    # Test enhanced suggestions
    print("\n🤖 Testing enhanced model suggestions...")
    suggestion_payload = {
        "target_column": "department"
    }
    
    response = requests.post(
        f"{base_url}/api/suggest-models/{session_id}",
        json=suggestion_payload,
        headers={"Content-Type": "application/json"}
    )
    
    if response.status_code == 200:
        result = response.json()
        print("✅ Enhanced suggestions successful!")
        print("\n📊 Response structure:")
        
        suggestions = result.get('suggestions', {})
        
        # Display basic info
        print(f"   Problem type: {suggestions.get('problem_type', 'N/A')}")
        print(f"   Recommended models: {suggestions.get('recommended_models', [])}")
        
        # Display model comparison results
        if 'model_comparison' in suggestions:
            print(f"\n🏆 Model Performance Comparison:")
            comparison = suggestions['model_comparison']
            
            for model_name, results in comparison.items():
                if results.get('status') == 'success':
                    score = results.get('primary_score', 0)
                    metric = results.get('primary_metric', 'score')
                    time = results.get('training_time', 0)
                    print(f"   {model_name}: {metric}={score:.3f}, time={time:.3f}s")
                else:
                    print(f"   {model_name}: {results.get('status', 'unknown')} - {results.get('error', '')}")
        
        # Display performance ranking
        if 'performance_ranking' in suggestions:
            print(f"\n🥇 Performance Ranking:")
            for i, model in enumerate(suggestions['performance_ranking'][:5], 1):
                print(f"   {i}. {model}")
        
        # Display reasoning
        if 'rule_based_suggestions' in suggestions and 'reasoning' in suggestions['rule_based_suggestions']:
            print(f"\n💡 AI Analysis:")
            for reason in suggestions['rule_based_suggestions']['reasoning']:
                print(f"   • {reason}")
                
    else:
        print(f"❌ Enhanced suggestions failed: {response.status_code}")
        print(response.text)

if __name__ == "__main__":
    test_enhanced_suggestions()
