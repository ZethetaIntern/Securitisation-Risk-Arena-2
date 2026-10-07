import pandas as pd
import yaml

def build_tranches():
    print("Calculating Tranche Risks...")
    tranches = pd.read_csv('../data/raw/tranches.csv')
    pools = pd.read_csv('../data/outputs/pool_risk_output.csv')
    
    # Merge pool balance and ECL to tranches
    df = tranches.merge(pools[['pool_id', 'total_balance', 'total_ecl']], on='pool_id')
    
    # Calculate tranche size and balance
    df['tranche_balance'] = df['total_balance'] * (df['detachment_point'] - df['attachment_point'])
    
    # Simple subordination mapping
    # Tranche losses: 
    # Loss applied from bottom up.
    # A tranche's loss is max(0, min(tranche_balance, total_ecl - pool_balance * attachment_point))
    
    df['subordination'] = df['attachment_point']
    
    def calculate_tranche_loss(row):
        pool_loss = row['total_ecl']
        attach_amt = row['total_balance'] * row['attachment_point']
        detach_amt = row['total_balance'] * row['detachment_point']
        
        # Loss reaches this tranche if pool_loss > attach_amt
        if pool_loss <= attach_amt:
            return 0.0
        elif pool_loss >= detach_amt:
            return row['tranche_balance']
        else:
            return pool_loss - attach_amt

    df['tranche_expected_loss'] = df.apply(calculate_tranche_loss, axis=1)
    df['tranche_loss_pct'] = (df['tranche_expected_loss'] / df['tranche_balance']).fillna(0).round(4)
    
    df.to_csv('../data/outputs/tranche_risk_output.csv', index=False)
    print("Tranche risk complete.")

if __name__ == '__main__':
    build_tranches()
