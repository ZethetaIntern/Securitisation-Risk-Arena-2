# Securitisation Risk Arena - Interview Guide

## 30-Second Pitch
"I built an end-to-end Securitisation Risk Engine that simulates 50,000+ loans. It incorporates an IFRS 9-style Expected Credit Loss (ECL) model, calculates Pool and Tranche risks, and runs an automated Cash Flow Waterfall. The system uses Python for modelling, DuckDB for advanced SQL analytics, and Streamlit for interactive risk gamification and stress testing."

## 2-Minute Pitch
"The Securitisation Risk Arena is a full-stack risk analytics platform. I started by generating a highly realistic synthetic dataset of 50,000 loans with correlated macroeconomic variables. I built a robust SQL layer using DuckDB for high-performance aggregations and vintage analysis. Then, I implemented an IFRS 9-compliant risk engine in Python, predicting Probability of Default (PD) via Logistic Regression, alongside LGD and EAD frameworks. 

But I didn't stop at the loan level—I aggregated these into securitisation pools, defined a tranche hierarchy (AAA to Equity), and built a deterministic cash-flow waterfall engine. Finally, I wrapped this in an interactive Streamlit application where a user can act as a Portfolio Manager, simulating the 2008 Subprime Crisis to see how their tranche investments perform under stress."

## Explain IFRS 9 and ECL
Under IFRS 9, Expected Credit Loss (ECL) is calculated proactively rather than waiting for a default. It requires assigning loans to 3 stages:
- **Stage 1 (Performing):** 12-month PD is used.
- **Stage 2 (Underperforming - SICR):** Lifetime PD is used.
- **Stage 3 (Default):** PD is 100%.
**ECL = PD × LGD × EAD × Discount Factor**.

## Explain Waterfall
A cash flow waterfall dictates the strict order of payments in a securitisation. Senior tranches (AAA) get paid interest and principal first, while Equity/Junior tranches absorb the first losses. Our engine handles shortfalls and dynamically allocates available cash down the capital structure.

## Technical Questions
**Q: Why DuckDB over Pandas for certain analytics?**
A: DuckDB executes analytical queries (like window functions for rolling risk and cumulative vintage defaults) faster out-of-memory and integrates seamlessly with Python, demonstrating strong SQL capabilities.

**Q: How did you implement the PD model?**
A: I used Logistic Regression on scaled borrower variables (LTV, DTI, Credit Score). I favored LR over a Black-box model like XGBoost because credit risk modelling heavily values interpretability and coefficient analysis.
