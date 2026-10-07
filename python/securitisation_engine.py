import pandas as pd

def build_pools():
    print("Aggregating Securitisation Pools...")
    loans = pd.read_csv('../data/raw/loans.csv')
    ecl = pd.read_csv('../data/outputs/ecl_output.csv')
    
    # Merge
    df = loans.merge(ecl, on=['loan_id', 'pool_id'])
    
    # Aggregate to pool level
    pool_metrics = df.groupby('pool_id').agg(
        total_balance=('current_balance', 'sum'),
        loan_count=('loan_id', 'count'),
        wa_interest_rate=('interest_rate', lambda x: (x * df.loc[x.index, 'current_balance']).sum() / df.loc[x.index, 'current_balance'].sum() if df.loc[x.index, 'current_balance'].sum() > 0 else 0),
        wa_ltv=('ltv', lambda x: (x * df.loc[x.index, 'current_balance']).sum() / df.loc[x.index, 'current_balance'].sum() if df.loc[x.index, 'current_balance'].sum() > 0 else 0),
        wa_credit_score=('current_credit_score', lambda x: (x * df.loc[x.index, 'current_balance']).sum() / df.loc[x.index, 'current_balance'].sum() if df.loc[x.index, 'current_balance'].sum() > 0 else 0),
        total_ecl=('ecl', 'sum')
    ).reset_index()
    
    pool_metrics['ecl_coverage_pct'] = (pool_metrics['total_ecl'] / pool_metrics['total_balance']).round(4)
    
    pool_metrics.to_csv('../data/outputs/pool_risk_output.csv', index=False)
    print("Pool aggregation complete.")

if __name__ == '__main__':
    build_pools()
