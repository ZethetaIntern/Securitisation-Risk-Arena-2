import pandas as pd
import os

def check_data_quality():
    reports = []
    
    # Check customers
    cust = pd.read_csv('../data/raw/customers.csv')
    reports.append({'table': 'customers', 'check': 'Row Count', 'status': 'PASS' if len(cust) >= 49000 else 'FAIL', 'details': f'{len(cust)} rows'})
    reports.append({'table': 'customers', 'check': 'Unique IDs', 'status': 'PASS' if cust['customer_id'].is_unique else 'FAIL', 'details': f'{cust.customer_id.nunique()} unique'})
    reports.append({'table': 'customers', 'check': 'Null Count', 'status': 'PASS' if cust.isnull().sum().sum() == 0 else 'FAIL', 'details': f'{cust.isnull().sum().sum()} nulls'})
    
    # Check loans
    loans = pd.read_csv('../data/raw/loans.csv')
    reports.append({'table': 'loans', 'check': 'Row Count', 'status': 'PASS' if len(loans) >= 50000 else 'FAIL', 'details': f'{len(loans)} rows'})
    reports.append({'table': 'loans', 'check': 'Unique IDs', 'status': 'PASS' if loans['loan_id'].is_unique else 'FAIL', 'details': f'{loans.loan_id.nunique()} unique'})
    reports.append({'table': 'loans', 'check': 'LTV Logic', 'status': 'PASS' if (loans['ltv'] >= 0).all() else 'FAIL', 'details': 'LTV >= 0 check'})
    reports.append({'table': 'loans', 'check': 'Interest Rate Logic', 'status': 'PASS' if (loans['interest_rate'] > 0).all() else 'FAIL', 'details': 'Interest > 0 check'})
    
    # Check relationships
    valid_customers = loans['customer_id'].isin(cust['customer_id']).all()
    reports.append({'table': 'loans_customers_fk', 'check': 'Referential Integrity', 'status': 'PASS' if valid_customers else 'FAIL', 'details': 'All loans have valid customer'})
    
    # Check perf
    perf = pd.read_csv('../data/raw/loan_performance.csv')
    reports.append({'table': 'loan_performance', 'check': 'Row Count', 'status': 'PASS' if len(perf) > len(loans) else 'FAIL', 'details': f'{len(perf)} rows'})
    
    report_df = pd.DataFrame(reports)
    report_df.to_csv('../data/outputs/data_quality_report.csv', index=False)
    
    # Create markdown report
    with open('../data/outputs/data_quality_report.md', 'w') as f:
        f.write('# Data Quality Report\n\n')
        f.write(report_df.to_markdown(index=False))
        
    print(report_df)
    
    if (report_df['status'] == 'FAIL').any():
        print("\nWARNING: Some data quality checks failed.")
        return False
    else:
        print("\nAll data quality checks passed!")
        return True

if __name__ == '__main__':
    check_data_quality()
