import duckdb
import os

def build_sql_layer():
    print("Building SQL Analytical Layer via DuckDB...")
    db_path = '../data/processed/risk_arena.duckdb'
    if os.path.exists(db_path):
        os.remove(db_path)
    
    con = duckdb.connect(db_path)
    
    # 1. Load CSVs into tables
    print("Loading CSV files into DuckDB...")
    con.execute("CREATE TABLE customers AS SELECT * FROM read_csv_auto('../data/raw/customers.csv');")
    con.execute("CREATE TABLE loans AS SELECT * FROM read_csv_auto('../data/raw/loans.csv');")
    con.execute("CREATE TABLE loan_performance AS SELECT * FROM read_csv_auto('../data/raw/loan_performance.csv');")
    con.execute("CREATE TABLE macroeconomic_data AS SELECT * FROM read_csv_auto('../data/raw/macroeconomic_data.csv');")
    con.execute("CREATE TABLE securitisation_pools AS SELECT * FROM read_csv_auto('../data/raw/securitisation_pools.csv');")
    con.execute("CREATE TABLE tranches AS SELECT * FROM read_csv_auto('../data/raw/tranches.csv');")
    
    # 2. Execute external SQL scripts (if any)
    sql_files = sorted([f for f in os.listdir('../sql') if f.endswith('.sql')])
    for sql_file in sql_files:
        print(f"Executing {sql_file}...")
        with open(f'../sql/{sql_file}', 'r') as f:
            script = f.read()
            con.execute(script)
            
    con.close()
    print("SQL Analytical Layer built successfully.")

if __name__ == '__main__':
    build_sql_layer()
