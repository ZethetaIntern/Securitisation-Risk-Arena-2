import pandas as pd
import numpy as np

def run_waterfall():
    print("Executing Waterfall Engine...")
    
    tranches = pd.read_csv('../data/outputs/tranche_risk_output.csv')
    
    # We will simulate a single period cash flow distribution for simplicity,
    # or just use the pool metrics to allocate expected losses and cash.
    # We know the total expected loss by tranche. Let's calculate the cash flows.
    
    pool_balance = tranches['total_balance'].iloc[0] if len(tranches) > 0 else 0
    total_ecl = tranches['total_ecl'].iloc[0] if len(tranches) > 0 else 0
    
    # Let's say available cash = pool_balance - total_ecl + interest
    # We will approximate available cash to distribute
    # Then we distribute to senior tranches first.
    
    results = []
    
    for pool_id, group in tranches.groupby('pool_id'):
        group = group.sort_values('seniority')
        
        pool_bal = group['total_balance'].iloc[0]
        pool_loss = group['total_ecl'].iloc[0]
        
        available_cash = pool_bal - pool_loss
        
        allocated_cash = 0
        
        for _, t in group.iterrows():
            tranche_principal = t['tranche_balance']
            
            # They should receive tranche_principal - tranche_expected_loss
            expected_receipt = tranche_principal - t['tranche_expected_loss']
            
            if available_cash >= expected_receipt:
                cash_to_tranche = expected_receipt
            else:
                cash_to_tranche = available_cash
                
            available_cash -= cash_to_tranche
            allocated_cash += cash_to_tranche
            
            results.append({
                'pool_id': pool_id,
                'tranche_name': t['tranche_name'],
                'tranche_balance': tranche_principal,
                'tranche_expected_loss': t['tranche_expected_loss'],
                'allocated_cash': cash_to_tranche,
                'shortfall': expected_receipt - cash_to_tranche
            })
            
    res_df = pd.DataFrame(results)
    res_df.to_csv('../data/outputs/waterfall_output.csv', index=False)
    
    # Reconciliation test
    print("Running Waterfall Reconciliation Test...")
    reconciliation_errors = 0
    for pool_id, group in res_df.groupby('pool_id'):
        pool_data = tranches[tranches['pool_id'] == pool_id].iloc[0]
        total_cash_avail = pool_data['total_balance'] - pool_data['total_ecl']
        total_cash_alloc = group['allocated_cash'].sum()
        
        if not np.isclose(total_cash_alloc, min(total_cash_avail, group['tranche_balance'].sum() - group['tranche_expected_loss'].sum())):
            print(f"Reconciliation Failed for Pool {pool_id}")
            reconciliation_errors += 1
            
    if reconciliation_errors == 0:
        print("Waterfall Reconciliation Passed.")
    
    print("Waterfall Engine Complete.")

if __name__ == '__main__':
    run_waterfall()
