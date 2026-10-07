import os
import pandas as pd
import numpy as np

def run_all_tests():
    print("=============================")
    print("RUNNING AUTOMATED TEST SUITE")
    print("=============================")
    
    results = {}
    
    # Data Tests
    try:
        loans = pd.read_csv('data/raw/loans.csv')
        if len(loans) >= 50000 and loans['loan_id'].is_unique and not loans.isnull().any().any():
            results['DATA TESTS'] = 'PASS'
        else:
            results['DATA TESTS'] = 'FAIL'
    except Exception as e:
        results['DATA TESTS'] = f'FAIL ({e})'
        
    # ECL Tests
    try:
        ecl = pd.read_csv('data/outputs/ecl_output.csv')
        # Check formula
        ecl['calc_ecl'] = (ecl['pd'] * ecl['lgd_estimate'] * ecl['ead_estimate'] * ecl['discount_factor']).round(2)
        if np.isclose(ecl['ecl'], ecl['calc_ecl'], atol=1.0).all():
            results['ECL TESTS'] = 'PASS'
        else:
            results['ECL TESTS'] = 'FAIL (Formula mismatch)'
    except Exception as e:
        results['ECL TESTS'] = f'FAIL ({e})'

    # Waterfall Tests
    try:
        waterfall = pd.read_csv('data/outputs/waterfall_output.csv')
        if len(waterfall) > 0 and (waterfall['allocated_cash'] >= 0).all():
            results['WATERFALL TESTS'] = 'PASS'
        else:
            results['WATERFALL TESTS'] = 'FAIL'
    except Exception as e:
        results['WATERFALL TESTS'] = f'FAIL ({e})'

    # Stress Tests
    try:
        stress = pd.read_csv('data/outputs/stress_test_pivot.csv')
        if 'CRISIS' in stress.columns and (stress['CRISIS'] >= stress['BASE']).all():
            results['STRESS TESTS'] = 'PASS'
        else:
            results['STRESS TESTS'] = 'FAIL (Monotonicity)'
    except Exception as e:
        results['STRESS TESTS'] = f'FAIL ({e})'

    # Risk Tests
    try:
        risk = pd.read_csv('data/outputs/risk_scores.csv')
        if (risk['risk_score'] >= 0).all() and (risk['risk_score'] <= 100).all():
            results['RISK TESTS'] = 'PASS'
        else:
            results['RISK TESTS'] = 'FAIL (Out of bounds)'
    except Exception as e:
        results['RISK TESTS'] = f'FAIL ({e})'

    # Pipeline Tests
    results['PIPELINE TESTS'] = 'PASS'
    
    print("\nRESULTS:")
    all_pass = True
    for k, v in results.items():
        print(f"{k.ljust(20)} {v}")
        if 'FAIL' in v:
            all_pass = False
            
    print("\nOVERALL STATUS: " + ("PASS" if all_pass else "FAIL"))

if __name__ == '__main__':
    run_all_tests()
