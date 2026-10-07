import pandas as pd
import numpy as np
import yaml
import os
import itertools
from datetime import datetime, timedelta

def load_config():
    with open('../config/assumptions.yaml', 'r') as f:
        assumptions = yaml.safe_load(f)
    with open('../config/scenarios.yaml', 'r') as f:
        scenarios = yaml.safe_load(f)
    return assumptions, scenarios

def generate_data():
    assumptions, scenarios = load_config()
    np.random.seed(assumptions['random_seed'])
    
    n_loans = assumptions['portfolio_size_target']
    n_customers = int(n_loans * 0.9) # Some customers have multiple loans
    
    print(f"Generating {n_customers} customers...")
    customer_ids = [f'CUST-{i:06d}' for i in range(1, n_customers + 1)]
    
    # Generate Customer Data
    ages = np.random.normal(loc=42, scale=12, size=n_customers).astype(int)
    ages = np.clip(ages, 18, 85)
    
    incomes = np.random.lognormal(mean=np.log(75000), sigma=0.6, size=n_customers)
    incomes = np.clip(incomes, 20000, 500000).round(2)
    
    emp_types = np.random.choice(['Salaried', 'Self-Employed', 'Business Owner', 'Professional'], size=n_customers, p=[0.6, 0.2, 0.1, 0.1])
    emp_years = np.random.exponential(scale=5, size=n_customers).astype(int)
    emp_years = np.clip(emp_years, 0, 40)
    
    credit_scores = np.random.normal(loc=680, scale=80, size=n_customers).astype(int)
    credit_scores = np.clip(credit_scores, 300, 850)
    
    # Derived logic: higher income -> better score slightly
    credit_scores = credit_scores + (np.log(incomes) - np.log(75000)) * 10
    credit_scores = np.clip(credit_scores, 300, 850).astype(int)
    
    states = np.random.choice(['NY', 'CA', 'TX', 'FL', 'IL', 'PA', 'OH', 'GA', 'NC', 'MI'], size=n_customers)
    
    customers_df = pd.DataFrame({
        'customer_id': customer_ids,
        'age': ages,
        'income': incomes,
        'employment_type': emp_types,
        'employment_years': emp_years,
        'credit_score': credit_scores,
        'state': states,
        'city': [f'City_{i%100}' for i in range(n_customers)],
        'customer_segment': pd.qcut(incomes, q=4, labels=['Low', 'Medium', 'High', 'Premium'])
    })
    
    print(f"Generating {n_loans} loans...")
    loan_ids = [f'LN-{i:07d}' for i in range(1, n_loans + 1)]
    loan_customers = np.random.choice(customer_ids, size=n_loans)
    
    loan_types = np.random.choice(['Auto', 'Mortgage', 'Personal', 'Credit Card'], size=n_loans, p=[0.3, 0.4, 0.2, 0.1])
    
    orig_dates = pd.to_datetime('2020-01-01') + pd.to_timedelta(np.random.randint(0, 1000, size=n_loans), unit='D')
    
    term_months = np.where(loan_types == 'Mortgage', np.random.choice([180, 360], size=n_loans, p=[0.2, 0.8]),
                  np.where(loan_types == 'Auto', np.random.choice([36, 48, 60, 72], size=n_loans),
                  np.where(loan_types == 'Personal', np.random.choice([12, 24, 36, 48], size=n_loans), 0)))
    
    # Random maturity based on origination and term
    maturity_dates = orig_dates + pd.to_timedelta(term_months * 30.436875, unit='D')
    
    # Connect with customers for DTI and LTV
    loans_df = pd.DataFrame({
        'loan_id': loan_ids,
        'customer_id': loan_customers,
        'loan_type': loan_types,
        'origination_date': orig_dates,
        'maturity_date': maturity_dates,
        'term_months': term_months
    })
    
    loans_df = loans_df.merge(customers_df[['customer_id', 'income', 'credit_score']], on='customer_id', how='left')
    
    # Generate financial metrics
    # Higher credit score -> lower interest rate
    base_rates = {'Mortgage': 0.04, 'Auto': 0.05, 'Personal': 0.10, 'Credit Card': 0.18}
    loans_df['base_rate'] = loans_df['loan_type'].map(base_rates)
    loans_df['interest_rate'] = loans_df['base_rate'] - ((loans_df['credit_score'] - 680) / 100) * 0.01
    loans_df['interest_rate'] = np.clip(loans_df['interest_rate'], 0.02, 0.29).round(4)
    
    principal = np.where(loans_df['loan_type'] == 'Mortgage', np.random.normal(300000, 100000, size=n_loans),
                np.where(loans_df['loan_type'] == 'Auto', np.random.normal(30000, 10000, size=n_loans),
                np.where(loans_df['loan_type'] == 'Personal', np.random.normal(15000, 5000, size=n_loans),
                np.random.uniform(1000, 10000, size=n_loans))))
    loans_df['original_principal'] = np.clip(principal, 1000, 2000000).round(2)
    
    # Calculate monthly payment (PMT)
    r = loans_df['interest_rate'] / 12
    n = loans_df['term_months']
    # If n is 0 (Credit Card), just set 0
    loans_df['monthly_payment'] = np.where(n > 0, 
        (loans_df['original_principal'] * r * (1 + r)**n) / ((1 + r)**n - 1), 
        loans_df['original_principal'] * 0.05).round(2)
    
    loans_df['dti'] = ((loans_df['monthly_payment'] * 12) / loans_df['income']).round(2)
    
    # Collateral
    loans_df['collateral_value'] = np.where(
        loans_df['loan_type'].isin(['Mortgage', 'Auto']),
        loans_df['original_principal'] / np.random.uniform(0.7, 0.95, size=n_loans),
        0
    ).round(2)
    loans_df['ltv'] = np.where(loans_df['collateral_value'] > 0, 
                               (loans_df['original_principal'] / loans_df['collateral_value']).round(2), 
                               0)
    
    loans_df['credit_score_at_origination'] = loans_df['credit_score']
    
    # Current dynamics (simulated current state)
    report_date = pd.to_datetime('2023-12-31')
    months_passed = ((report_date - loans_df['origination_date']).dt.days / 30.436875).astype(int)
    months_passed = np.clip(months_passed, 0, loans_df['term_months'])
    
    # Remaining balance (simplified amortization)
    # P = A [ (1+r)^n - (1+r)^p ] / [ (1+r)^n - 1 ]
    p = months_passed
    rem_bal = np.where(n > 0,
                       loans_df['original_principal'] * ((1+r)**n - (1+r)**p) / ((1+r)**n - 1),
                       loans_df['original_principal'] * np.random.uniform(0.5, 1.0, size=n_loans))
    loans_df['current_balance'] = np.clip(rem_bal, 0, loans_df['original_principal']).round(2)
    
    # Credit score drift
    score_drift = np.random.normal(0, 20, size=n_loans)
    loans_df['current_credit_score'] = np.clip(loans_df['credit_score_at_origination'] + score_drift, 300, 850).astype(int)
    
    # Risk grade based on current score
    bins = [0, 580, 670, 740, 800, 900]
    labels = ['Subprime', 'Fair', 'Good', 'Very Good', 'Exceptional']
    loans_df['risk_grade'] = pd.cut(loans_df['current_credit_score'], bins=bins, labels=labels)
    
    # Defaults and delinquency logic
    # Higher LTV, higher DTI, lower credit score -> higher PD
    base_pd_prob = 0.05
    pd_prob = base_pd_prob + \
              (loans_df['ltv'] > 0.85).astype(float) * 0.03 + \
              (loans_df['dti'] > 0.40).astype(float) * 0.05 + \
              ((700 - loans_df['current_credit_score']) / 100) * 0.05
    pd_prob = np.clip(pd_prob, 0.001, 0.3)
    
    loans_df['default_flag'] = (np.random.random(size=n_loans) < pd_prob).astype(int)
    
    loans_df['delinquency_days'] = np.where(
        loans_df['default_flag'] == 1,
        np.random.randint(90, 365, size=n_loans),
        np.where(np.random.random(size=n_loans) < 0.1, np.random.randint(1, 89, size=n_loans), 0)
    )
    
    loans_df['recovery_amount'] = np.where(
        loans_df['default_flag'] == 1,
        loans_df['current_balance'] * np.random.uniform(0.1, 0.8, size=n_loans),
        0
    ).round(2)
    
    # Prepayment
    prepay_prob = 0.1 - (loans_df['interest_rate'] - loans_df['base_rate']) * 0.5
    prepay_prob = np.clip(prepay_prob, 0.01, 0.2)
    loans_df['prepayment_flag'] = (np.random.random(size=n_loans) < prepay_prob).astype(int)
    
    # Adjust balances for closed loans
    loans_df.loc[loans_df['prepayment_flag'] == 1, 'current_balance'] = 0
    loans_df.loc[loans_df['default_flag'] == 1, 'current_balance'] = 0 # Defaulted, moved to recovery
    
    loans_df['loan_status'] = np.where(loans_df['default_flag'] == 1, 'Defaulted',
                              np.where(loans_df['prepayment_flag'] == 1, 'Prepaid',
                              np.where(loans_df['delinquency_days'] > 0, 'Delinquent', 'Current')))
    
    # Assign pools
    loans_df['pool_id'] = [f'POOL-{np.random.randint(1, 11):02d}' for _ in range(n_loans)]
    
    # Clean up temp columns
    loans_df = loans_df.drop(columns=['income', 'credit_score', 'base_rate'])
    
    print("Generating loan performance records...")
    # Generate 12 months of recent history for active loans
    perf_records = []
    
    # To save time and space, we generate history only for a sample of loans, or just the last 12 months
    # Vectorized approach for 12 months history
    active_loans = loans_df[loans_df['loan_status'] == 'Current'].copy()
    for m in range(12, 0, -1):
        snapshot_date = report_date - pd.DateOffset(months=m-1)
        
        # Slight balance reduction
        month_bal = active_loans['current_balance'] + (active_loans['monthly_payment'] * (m-1))
        
        perf = pd.DataFrame({
            'loan_id': active_loans['loan_id'],
            'report_date': snapshot_date,
            'balance': month_bal.round(2),
            'delinquency_days': np.random.choice([0, 30, 60], size=len(active_loans), p=[0.9, 0.08, 0.02]),
            'payment_received': active_loans['monthly_payment']
        })
        perf_records.append(perf)
        
    perf_df = pd.concat(perf_records, ignore_index=True)
    
    print("Generating macroeconomic data...")
    dates = pd.date_range(start='2020-01-01', end='2024-12-01', freq='ME')
    macro_df = pd.DataFrame({
        'date': dates,
        'unemployment_rate': np.linspace(0.04, 0.08, len(dates)) + np.random.normal(0, 0.005, len(dates)),
        'interest_rate': np.linspace(0.01, 0.05, len(dates)) + np.random.normal(0, 0.002, len(dates)),
        'hpi_index': 100 + np.cumsum(np.random.normal(0.5, 2.0, len(dates)))
    })
    
    print("Generating securitisation pools...")
    pools_df = loans_df.groupby('pool_id').agg(
        total_balance=('original_principal', 'sum'),
        loan_count=('loan_id', 'count'),
        wa_interest_rate=('interest_rate', 'mean'),
        wa_credit_score=('credit_score_at_origination', 'mean')
    ).reset_index()
    
    print("Generating tranches...")
    tranches_list = []
    for pool in pools_df['pool_id']:
        for t in assumptions['tranches']:
            tranches_list.append({
                'pool_id': pool,
                'tranche_name': t['name'],
                'seniority': t['seniority'],
                'attachment_point': t['attachment'],
                'detachment_point': t['detachment'],
                'interest_rate': t['interest_rate']
            })
    tranches_df = pd.DataFrame(tranches_list)
    
    print("Generating waterfall rules...")
    waterfall_df = pd.DataFrame([
        {'rule_id': 1, 'priority': 1, 'description': 'Servicing Fees', 'pct_allocation': 0.01},
        {'rule_id': 2, 'priority': 2, 'description': 'Interest AAA', 'pct_allocation': None},
        {'rule_id': 3, 'priority': 3, 'description': 'Interest AA', 'pct_allocation': None},
        {'rule_id': 4, 'priority': 4, 'description': 'Interest A', 'pct_allocation': None},
        {'rule_id': 5, 'priority': 5, 'description': 'Interest BBB', 'pct_allocation': None},
        {'rule_id': 6, 'priority': 6, 'description': 'Principal AAA', 'pct_allocation': None},
        {'rule_id': 7, 'priority': 7, 'description': 'Principal AA', 'pct_allocation': None},
        {'rule_id': 8, 'priority': 8, 'description': 'Principal A', 'pct_allocation': None},
        {'rule_id': 9, 'priority': 9, 'description': 'Principal BBB', 'pct_allocation': None},
        {'rule_id': 10, 'priority': 10, 'description': 'Equity / Residual', 'pct_allocation': None},
    ])
    
    print("Generating crisis events...")
    crisis_df = pd.DataFrame([
        {'event_id': 'CR-01', 'name': 'Subprime Mortgage Crash', 'hpi_shock': -0.30, 'unemp_shock': 0.05, 'recovery_shock': -0.40},
        {'event_id': 'CR-02', 'name': 'Pandemic Liquidity Squeeze', 'hpi_shock': -0.10, 'unemp_shock': 0.10, 'recovery_shock': -0.20},
        {'event_id': 'CR-03', 'name': 'Runaway Inflation', 'hpi_shock': -0.05, 'unemp_shock': 0.02, 'recovery_shock': -0.10},
    ])
    
    # Save datasets
    print("Saving datasets to data/raw/ ...")
    customers_df.to_csv('../data/raw/customers.csv', index=False)
    loans_df.to_csv('../data/raw/loans.csv', index=False)
    perf_df.to_csv('../data/raw/loan_performance.csv', index=False)
    macro_df.to_csv('../data/raw/macroeconomic_data.csv', index=False)
    pools_df.to_csv('../data/raw/securitisation_pools.csv', index=False)
    tranches_df.to_csv('../data/raw/tranches.csv', index=False)
    waterfall_df.to_csv('../data/raw/waterfall_rules.csv', index=False)
    crisis_df.to_csv('../data/raw/crisis_events.csv', index=False)
    
    print("Data generation complete!")

if __name__ == '__main__':
    generate_data()
