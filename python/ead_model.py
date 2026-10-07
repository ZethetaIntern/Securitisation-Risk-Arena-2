import pandas as pd
import numpy as np
import yaml

def build_ead_model():
    print("Calculating EAD...")
    with open('../config/assumptions.yaml', 'r') as f:
        assumptions = yaml.safe_load(f)
        
    ead_factor = assumptions['ead_amortization_factor']
    
    loans = pd.read_csv('../data/raw/loans.csv')
    
    # EAD is generally current balance, but for credit cards it could be limit * CCF.
    # For simplicity in this synthetic model:
    # EAD = Current Balance * Amortization Factor + 1 month interest
    
    loans['ead_estimate'] = loans['current_balance'] * ead_factor + (loans['current_balance'] * (loans['interest_rate']/12))
    
    # Bound it to not exceed principal significantly
    loans['ead_estimate'] = np.clip(loans['ead_estimate'], 0, loans['original_principal'])
    
    loans[['loan_id', 'ead_estimate']].to_csv('../data/outputs/ead_predictions.csv', index=False)
    print("EAD predictions saved.")

if __name__ == '__main__':
    build_ead_model()
