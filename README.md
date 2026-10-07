# Securitisation Risk Arena

## Project Overview
An end-to-end Risk Analytics and Securitisation modeling platform built to demonstrate advanced SQL, Python, IFRS-9 ECL calculations, and Tranche Waterfall modeling. 

## Features
- **Data Generation:** 50,000+ realistic synthetic loans with structural correlation.
- **DuckDB SQL Layer:** Window functions, CTEs, and Vintage Analysis.
- **Risk Engine:** Logistic Regression PD, rule-based LGD/EAD, and IFRS 9 Staging.
- **Securitisation:** Pool level aggregation, AAA-Equity Tranching, and Waterfall Cash Flow distribution.
- **Stress Testing:** BASE to CRISIS scenario analysis.
- **Interactive UI:** Streamlit application with a Risk Arena and Crisis Lab gamification.

## How to Run
1. Activate Virtual Environment: `.\venv\Scripts\Activate.ps1`
2. Run the Full Pipeline: `cd python; python pipeline.py`
3. Run the Tests: `python run_tests.py`
4. Run the Streamlit Dashboard: `streamlit run app/app.py`
