# scripts/validate_data.py
import pandas as pd
import numpy as np
import json
from datetime import datetime
import sys

def validate_migraine_dataset(file_path='data/raw/migraine_dataset.csv'):
    """Comprehensive data validation"""
    print("🔍 Starting Data Validation...")
    
    try:
        df = pd.read_csv(file_path)
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found!")
        sys.exit(1)
    
    validation_results = {
        'timestamp': datetime.now().isoformat(),
        'dataset_path': file_path,
        'total_records': len(df),
        'checks': {}
    }
    
    # Check 1: Required columns
    required_columns = [
        'age', 'gender', 'sleep_hours', 'sleep_quality', 'stress_level',
        'hydration', 'exercise', 'screen_time', 'caffeine_intake',
        'alcohol_intake', 'weather_changes', 'menstrual_cycle',
        'dehydration', 'bright_light', 'loud_noises', 'strong_smells',
        'missed_meals', 'specific_foods', 'physical_activity',
        'neck_pain', 'weather_pressure', 'humidity', 'temperature_change',
        'migraine_occurrence', 'migraine_severity'
    ]
    
    missing_cols = set(required_columns) - set(df.columns)
    validation_results['checks']['missing_columns'] = {
        'status': 'PASS' if not missing_cols else 'FAIL',
        'missing': list(missing_cols)
    }
    
    # Check 2: Missing values
    missing_counts = df.isnull().sum()
    validation_results['checks']['missing_values'] = {
        'status': 'PASS' if missing_counts.sum() == 0 else 'WARNING',
        'total_missing': int(missing_counts.sum()),
        'columns_with_missing': missing_counts[missing_counts > 0].to_dict()
    }
    
    # Check 3: Data types
    expected_dtypes = {
        'age': ['int64', 'float64'],
        'gender': ['int64'],
        'migraine_occurrence': ['int64'],
        'migraine_severity': ['int64', 'float64']
    }
    
    dtype_issues = []
    for col, expected in expected_dtypes.items():
        if col in df.columns and str(df[col].dtype) not in expected:
            dtype_issues.append(f"{col}: expected {expected}, got {df[col].dtype}")
    
    validation_results['checks']['data_types'] = {
        'status': 'PASS' if not dtype_issues else 'WARNING',
        'issues': dtype_issues
    }
    
    # Check 4: Value ranges
    range_checks = {
        'age': (0, 120),
        'gender': (0, 1),
        'sleep_hours': (0, 24),
        'sleep_quality': (1, 10),
        'stress_level': (1, 10),
        'migraine_occurrence': (0, 1),
        'migraine_severity': (0, 10)
    }
    
    range_issues = []
    for col, (min_val, max_val) in range_checks.items():
        if col in df.columns:
            out_of_range = ((df[col] < min_val) | (df[col] > max_val)).sum()
            if out_of_range > 0:
                range_issues.append(f"{col}: {out_of_range} values out of range [{min_val}, {max_val}]")
    
    validation_results['checks']['value_ranges'] = {
        'status': 'PASS' if not range_issues else 'FAIL',
        'issues': range_issues
    }
    
    # Check 5: Target variable distribution
    if 'migraine_occurrence' in df.columns:
        target_dist = df['migraine_occurrence'].value_counts()
        validation_results['checks']['target_distribution'] = {
            'status': 'PASS',
            'distribution': target_dist.to_dict(),
            'imbalance_ratio': float(target_dist.max() / target_dist.min())
        }
    
    # Check 6: Duplicate records
    duplicates = df.duplicated().sum()
    validation_results['checks']['duplicates'] = {
        'status': 'PASS' if duplicates == 0 else 'WARNING',
        'count': int(duplicates)
    }
    
    # Check 7: Statistical summary
    validation_results['statistics'] = {
        'numeric_summary': df.describe().to_dict(),
        'correlation_with_target': df.corr()['migraine_occurrence'].to_dict() if 'migraine_occurrence' in df.columns else {}
    }
    
    # Overall status
    failed_checks = sum(1 for check in validation_results['checks'].values() if check['status'] == 'FAIL')
    warning_checks = sum(1 for check in validation_results['checks'].values() if check['status'] == 'WARNING')
    
    validation_results['overall_status'] = 'PASS' if failed_checks == 0 else 'FAIL'
    validation_results['summary'] = {
        'total_checks': len(validation_results['checks']),
        'passed': len(validation_results['checks']) - failed_checks - warning_checks,
        'warnings': warning_checks,
        'failed': failed_checks
    }
    
    # Save results
    with open('reports/data_validation.json', 'w') as f:
        json.dump(validation_results, f, indent=2)
    
    # Generate HTML report
    generate_html_report(validation_results)
    
    # Print summary
    print("\n" + "="*80)
    print("📊 DATA VALIDATION SUMMARY")
    print("="*80)
    print(f"Total Records: {validation_results['total_records']}")
    print(f"Overall Status: {validation_results['overall_status']}")
    print(f"Passed: {validation_results['summary']['passed']}")
    print(f"Warnings: {validation_results['summary']['warnings']}")
    print(f"Failed: {validation_results['summary']['failed']}")
    print("="*80)
    
    if validation_results['overall_status'] == 'FAIL':
        print("\n❌ Validation FAILED! Please fix the issues above.")
        sys.exit(1)
    else:
        print("\n✅ Validation PASSED!")
        sys.exit(0)

def generate_html_report(results):
    """Generate HTML validation report"""
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Data Validation Report</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background: #4CAF50; color: white; padding: 20px; }}
            .fail {{ background: #f44336; color: white; padding: 20px; }}
            .check {{ margin: 10px 0; padding: 10px; border: 1px solid #ddd; }}
            .pass {{ border-left: 4px solid #4CAF50; }}
            .warning {{ border-left: 4px solid #ff9800; }}
            .fail-check {{ border-left: 4px solid #f44336; }}
        </style>
    </head>
    <body>
        <div class="{'header' if results['overall_status'] == 'PASS' else 'fail'}">
            <h1>Data Validation Report</h1>
            <p>Generated: {results['timestamp']}</p>
            <p>Status: {results['overall_status']}</p>
        </div>
        
        <h2>Summary</h2>
        <p>Total Records: {results['total_records']}</p>
        <p>Passed Checks: {results['summary']['passed']}</p>
        <p>Warnings: {results['summary']['warnings']}</p>
        <p>Failed Checks: {results['summary']['failed']}</p>
        
        <h2>Validation Checks</h2>
    """
    
    for check_name, check_result in results['checks'].items():
        status_class = check_result['status'].lower().replace('fail', 'fail-check')
        html += f"""
        <div class="check {status_class}">
            <h3>{check_name.replace('_', ' ').title()}</h3>
            <p>Status: {check_result['status']}</p>
            <pre>{json.dumps({k: v for k, v in check_result.items() if k != 'status'}, indent=2)}</pre>
        </div>
        """
    
    html += """
    </body>
    </html>
    """
    
    with open('reports/data_validation.html', 'w') as f:
        f.write(html)

if __name__ == "__main__":
    import os
    os.makedirs('reports', exist_ok=True)
    validate_migraine_dataset()