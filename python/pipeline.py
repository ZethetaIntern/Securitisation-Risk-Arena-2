import os
import subprocess
import sys

def run_script(script_name):
    print(f"\n{'='*50}\nRunning {script_name}...\n{'='*50}")
    result = subprocess.run([sys.executable, script_name], capture_output=True, text=True)
    if result.returncode != 0:
        print(f"Error in {script_name}:\n{result.stderr}")
        sys.exit(1)
    print(result.stdout)

def main():
    scripts = [
        'data_generator.py',
        'data_quality.py',
        'sql_builder.py',
        'pd_model.py',
        'lgd_model.py',
        'ead_model.py',
        'ecl_engine.py',
        'securitisation_engine.py',
        'tranche_engine.py',
        'waterfall_engine.py',
        'stress_engine.py',
        'risk_scoring.py'
    ]
    
    for script in scripts:
        run_script(script)
        
    print("\n\n" + "*"*50)
    print("PIPELINE EXECUTION COMPLETE!")
    print("*"*50)

if __name__ == '__main__':
    main()
