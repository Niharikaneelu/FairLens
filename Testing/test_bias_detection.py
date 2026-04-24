"""
FairLens Bias Detection Testing Script
Run this after Member 1's backend is ready

Tests all 3 datasets and captures results
"""

import requests
import pandas as pd
import json
from datetime import datetime
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
BASE_DIR = os.path.dirname(SCRIPT_DIR)  # Go up one level to "FairLens Team Drive"

# Configure this URL from Member 1's backend
API_URL = "http://localhost:5000/api/analyze"  # UPDATE THIS

def test_dataset(csv_filename, dataset_name):
    """Test a single dataset and return results"""
    print(f"\n{'='*60}")
    print(f"Testing: {dataset_name}")
    print(f"{'='*60}")
    
    try:
        # Build full path relative to script location
        csv_path = os.path.join(BASE_DIR, "Datasets", csv_filename)
        print(f"Loading: {csv_path}")
        
        # Read CSV to show preview
        df = pd.read_csv(csv_path)
        print(f"\nDataset shape: {df.shape}")
        print(f"\nColumns: {list(df.columns)}")
        print(f"\nPreview (first 5 rows):")
        print(df.head())
        
        # Show ground truth statistics
        if 'hired' in df.columns:
            target_col = 'hired'
        elif 'approved' in df.columns:
            target_col = 'approved'
        elif 'accepted' in df.columns:
            target_col = 'accepted'
        else:
            target_col = None
        
        if target_col:
            print(f"\n{target_col.capitalize()} Distribution:")
            print(df[target_col].value_counts())
            
            # Gender breakdown
            if 'gender' in df.columns:
                print(f"\n{target_col} by Gender:")
                print(df.groupby('gender')[target_col].mean())
        
        # Send to API (uncomment when backend is ready)
        # with open(csv_path, 'rb') as f:
        #     files = {'file': f}
        #     response = requests.post(API_URL, files=files)
        #     result = response.json()
        #     print(f"\nAPI Response:")
        #     print(json.dumps(result, indent=2))
        #     return result
        
        print("\n[SKIP] API not connected yet - testing data loading only")
        print("[INFO] Datasets loaded successfully - ready for API testing")
        return {"status": "data_verified", "dataset": dataset_name}
        
    except Exception as e:
        print(f"\n[ERROR] {str(e)}")
        return {"status": "error", "error": str(e)}

def validate_bias_detection():
    """Validate that bias detection works correctly"""
    print("\n" + "="*60)
    print("BIAS DETECTION VALIDATION")
    print("="*60)
    
    test_cases = [
        {
            "name": "HR Hiring (Gender Bias Expected)",
            "file": "Datasets/hr_hiring_demo.csv",
            "expected_bias": ["gender"],
            "description": "Males hired at higher rate than females with similar qualifications"
        },
        {
            "name": "Loan Approval (Gender + Name Bias Expected)",
            "file": "Datasets/loan_approval_demo.csv",
            "expected_bias": ["gender", "name"],
            "description": "Males and Western names approved more often"
        },
        {
            "name": "College Admissions (Multiple Biases)",
            "file": "Datasets/college_admissions_demo.csv",
            "expected_bias": ["gender", "legacy", "name"],
            "description": "Legacy status, gender, and ethnic names affect acceptance"
        }
    ]
    
    results = []
    for test in test_cases:
        print(f"\n\nTest Case: {test['name']}")
        print(f"Description: {test['description']}")
        print(f"Expected Bias Types: {test['expected_bias']}")
        
        result = test_dataset(test['file'], test['name'])
        result['expected_bias'] = test['expected_bias']
        results.append(result)
    
    return results

def generate_test_report(results):
    """Generate test results summary"""
    print("\n\n" + "="*60)
    print("TEST SUMMARY REPORT")
    print("="*60)
    print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nTotal Tests: {len(results)}")
    
    for i, result in enumerate(results, 1):
        print(f"\n{i}. {result.get('dataset', 'Unknown')}")
        print(f"   Status: {result.get('status', 'Unknown')}")
        if 'expected_bias' in result:
            print(f"   Expected: {result['expected_bias']}")
    
    print("\n\n" + "="*60)
    print("NEXT STEPS:")
    print("="*60)
    print("1. Get API endpoint from Member 1")
    print("2. Update API_URL in this script")
    print("3. Uncomment the API call section")
    print("4. Run: python test_bias_detection.py")
    print("5. Capture screenshots of outputs")
    print("6. Fill in expected_vs_actual.xlsx")

if __name__ == "__main__":
    results = validate_bias_detection()
    generate_test_report(results)
