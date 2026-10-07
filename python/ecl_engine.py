import pandas as pd
import numpy as np

def build_ecl_engine():
    print("Calculating ECL...")
    
    loans = pd.read_csv('../data/raw/loans.csv')
    pd_preds = pd.read_csv('../data/outputs/pd_predictions.csv')
    lgd_preds = pd.read_csv('../data/outputs/lgd_predictions.csv')
    ead_preds = pd.read_csv('../data/outputs/ead_predictions.csv')
    
    df = loans.merge(pd_preds, on='loan_id')
    df = df.merge(lgd_preds, on='loan_id')
    df = df.merge(ead_preds, on='loan_id')
    
    # IFRS 9 Stage Classification
    # Stage 1: Current
    # Stage 2: 30-89 DPD or SICR (Significant Increase in Credit Risk -> drop in score > 50)
    # Stage 3: 90+ DPD or Defaulted
    
    def assign_stage(row):
        if row['default_flag'] == 1 or row['delinquency_days'] >= 90:
            return 3
        elif row['delinquency_days'] >= 30 or (row['credit_score_at_origination'] - row['current_credit_score'] > 50):
            return 2
        else:
            return 1
            
    df['stage'] = df.apply(assign_stage, axis=1)
    
    # PD Mapping based on Stage
    # Stage 1: 12-month PD
    # Stage 2/3: Lifetime PD (Approx: 12m PD * remaining life / 12)
    # Stage 3: PD is effectively 100% (already defaulted)
    
    df['rem_life_years'] = np.clip(df['term_months'] / 12, 1, 30)
    
    df['final_pd'] = np.where(df['stage'] == 3, 1.0,
                     np.where(df['stage'] == 2, np.clip(df['pd_estimate'] * df['rem_life_years'], 0, 0.99),
                     df['pd_estimate']))
                     
    # Discount Factor Approximation (mid-point of remaining life)
    df['discount_factor'] = 1 / ((1 + df['interest_rate']) ** (df['rem_life_years'] / 2))
    
    # Calculate ECL
    df['ecl'] = (df['final_pd'] * df['lgd_estimate'] * df['ead_estimate'] * df['discount_factor']).round(2)
    
    # Reporting format
    output = df[['loan_id', 'stage', 'final_pd', 'lgd_estimate', 'ead_estimate', 'discount_factor', 'ecl', 'pool_id']]
    output = output.rename(columns={'final_pd': 'pd'})
    
    output.to_csv('../data/outputs/ecl_output.csv', index=False)
    
    # Aggregations for reporting
    pool_agg = output.groupby('pool_id').agg({'ecl': 'sum', 'ead_estimate': 'sum'}).reset_index()
    pool_agg['ecl_coverage'] = (pool_agg['ecl'] / pool_agg['ead_estimate']).round(4)
    pool_agg.to_csv('../data/outputs/ecl_pool_summary.csv', index=False)
    
    print("ECL calculation complete.")

if __name__ == '__main__':
    build_ecl_engine()
