import pandas as pd
import yaml

def run_stress_testing():
    print("Running Stress Testing Engine...")
    
    with open('../config/scenarios.yaml', 'r') as f:
        scenarios = yaml.safe_load(f)['scenarios']
        
    ecl_base = pd.read_csv('../data/outputs/ecl_output.csv')
    
    results = []
    
    for sc_name, sc_params in scenarios.items():
        pd_mult = sc_params['pd_multiplier']
        lgd_mult = sc_params['lgd_multiplier']
        
        # Apply stress
        sc_ecl = ecl_base.copy()
        sc_ecl['stressed_pd'] = sc_ecl['pd'] * pd_mult
        sc_ecl['stressed_pd'] = sc_ecl['stressed_pd'].clip(upper=1.0)
        
        sc_ecl['stressed_lgd'] = sc_ecl['lgd_estimate'] * lgd_mult
        sc_ecl['stressed_lgd'] = sc_ecl['stressed_lgd'].clip(upper=1.0)
        
        sc_ecl['stressed_ecl'] = (sc_ecl['stressed_pd'] * sc_ecl['stressed_lgd'] * 
                                  sc_ecl['ead_estimate'] * sc_ecl['discount_factor']).round(2)
                                  
        pool_stress = sc_ecl.groupby('pool_id')['stressed_ecl'].sum().reset_index()
        pool_stress['scenario'] = sc_name
        results.append(pool_stress)
        
    all_stress = pd.concat(results, ignore_index=True)
    
    # Pivot for easier reading
    stress_pivot = all_stress.pivot(index='pool_id', columns='scenario', values='stressed_ecl')
    
    # Monotonicity check
    print("Running Monotonicity Check...")
    monotonicity_passed = True
    for idx, row in stress_pivot.iterrows():
        if not (row['BASE'] <= row['MILD'] <= row['MODERATE'] <= row['SEVERE'] <= row['CRISIS']):
            print(f"Monotonicity failed for pool {idx}")
            monotonicity_passed = False
            
    if monotonicity_passed:
        print("Stress Monotonicity Check Passed.")
        
    all_stress.to_csv('../data/outputs/stress_test_output.csv', index=False)
    stress_pivot.to_csv('../data/outputs/stress_test_pivot.csv')
    print("Stress Testing Complete.")

if __name__ == '__main__':
    run_stress_testing()
