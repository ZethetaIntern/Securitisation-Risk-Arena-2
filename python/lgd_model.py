import pandas as pd
import numpy as np
import yaml

def build_lgd_model():
    print("Calculating LGD...")
    with open('../config/assumptions.yaml', 'r') as f:
        assumptions = yaml.safe_load(f)
        
    base_lgd = assumptions['lgd_base_rate']
    collateral_haircut = assumptions['lgd_collateral_haircut']
    recovery_costs = assumptions['recovery_costs_pct']
    
    loans = pd.read_csv('../data/raw/loans.csv')
    
    # LGD = Max(0, 1 - (Collateral * (1 - Haircut) * (1 - Recovery Costs) / EAD))
    # We will approximate EAD with current_balance to calculate a static LGD, 
    # but more formally we just map it. If unsecured (Personal, Credit Card), LGD is high.
    
    def calculate_lgd(row):
        if row['loan_type'] in ['Personal', 'Credit Card']:
            # Unsecured
            lgd = 0.85 
        else:
            # Secured
            if row['current_balance'] > 0:
                recovery_val = row['collateral_value'] * (1 - collateral_haircut) * (1 - recovery_costs)
                lgd = max(0.0, 1 - (recovery_val / row['current_balance']))
            else:
                lgd = base_lgd
        return min(lgd, 1.0)
        
    loans['lgd_estimate'] = loans.apply(calculate_lgd, axis=1)
    
    # Adjust slightly for delinquency (worse condition = lower recovery)
    loans['lgd_estimate'] = np.where(loans['delinquency_days'] > 90, 
                                     np.clip(loans['lgd_estimate'] * 1.1, 0, 1),
                                     loans['lgd_estimate'])
                                     
    loans[['loan_id', 'lgd_estimate']].to_csv('../data/outputs/lgd_predictions.csv', index=False)
    print("LGD predictions saved.")

if __name__ == '__main__':
    build_lgd_model()
