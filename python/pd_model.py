import pandas as pd
import numpy as np
import json
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.preprocessing import StandardScaler

def build_pd_model():
    print("Building PD Model...")
    loans = pd.read_csv('../data/raw/loans.csv')
    customers = pd.read_csv('../data/raw/customers.csv')
    
    # Merge for features
    df = loans.merge(customers[['customer_id', 'income', 'employment_years']], on='customer_id', how='left')
    
    # Features: ltv, dti, credit_score_at_origination, interest_rate, income, employment_years
    features = ['ltv', 'dti', 'credit_score_at_origination', 'interest_rate', 'income', 'employment_years']
    target = 'default_flag'
    
    # Drop rows with missing values in features
    df = df.dropna(subset=features + [target])
    
    X = df[features]
    y = df[target]
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    model = LogisticRegression(max_iter=1000, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    metrics = {
        'roc_auc': roc_auc_score(y_test, y_prob),
        'precision': precision_score(y_test, y_pred),
        'recall': recall_score(y_test, y_pred),
        'f1': f1_score(y_test, y_pred),
        'confusion_matrix': confusion_matrix(y_test, y_pred).tolist(),
        'coefficients': dict(zip(features, model.coef_[0].tolist())),
        'intercept': model.intercept_[0]
    }
    
    with open('../data/outputs/pd_model_metrics.json', 'w') as f:
        json.dump(metrics, f, indent=4)
        
    print("PD Model Metrics:")
    print(json.dumps(metrics, indent=2))
    
    # Generate predictions for all loans to use in ECL
    X_all_scaled = scaler.transform(X)
    df['pd_estimate'] = model.predict_proba(X_all_scaled)[:, 1]
    
    # Save predictions
    df[['loan_id', 'pd_estimate']].to_csv('../data/outputs/pd_predictions.csv', index=False)
    print("PD predictions saved.")

if __name__ == '__main__':
    build_pd_model()
