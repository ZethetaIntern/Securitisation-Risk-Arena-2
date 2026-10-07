import pandas as pd
import numpy as np

def calculate_risk_scores():
    print("Calculating Risk Scores...")
    loans = pd.read_csv('../data/raw/loans.csv')
    ecl = pd.read_csv('../data/outputs/ecl_output.csv')
    
    df = loans.merge(ecl, on=['loan_id', 'pool_id'])
    
    # Components
    # Score 0-100 (100 = highest risk)
    # PD: 30%, LGD: 20%, LTV: 15%, DTI: 15%, Delinquency: 20%
    
    # Normalize components to 0-100
    pd_score = (df['pd'] / df['pd'].max() * 100).fillna(0)
    lgd_score = (df['lgd_estimate'] * 100).fillna(0)
    
    # LTV > 1 means higher risk. clip at 1.5
    ltv_clipped = np.clip(df['ltv'], 0, 1.5)
    ltv_score = (ltv_clipped / 1.5 * 100).fillna(0)
    
    dti_clipped = np.clip(df['dti'], 0, 0.6)
    dti_score = (dti_clipped / 0.6 * 100).fillna(0)
    
    delinq_clipped = np.clip(df['delinquency_days'], 0, 180)
    delinq_score = (delinq_clipped / 180 * 100).fillna(0)
    
    df['risk_score'] = (pd_score * 0.3 + lgd_score * 0.2 + ltv_score * 0.15 + dti_score * 0.15 + delinq_score * 0.2).round(1)
    
    def classify_risk(score):
        if score < 30: return 'LOW'
        if score < 50: return 'MODERATE'
        if score < 75: return 'HIGH'
        return 'CRITICAL'
        
    df['risk_classification'] = df['risk_score'].apply(classify_risk)
    
    output = df[['loan_id', 'pool_id', 'risk_score', 'risk_classification']]
    output.to_csv('../data/outputs/risk_scores.csv', index=False)
    print("Risk Scoring Complete.")

if __name__ == '__main__':
    calculate_risk_scores()
