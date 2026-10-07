# MatRisk AI v 1.0 - Technical Report
**Classification:** Strictly Private and Confidential - Not for Circulation  
**Project:** MatRisk AI v 1.0 - Securitisation Risk Arena  

---

## 1. Executive Summary
The MatRisk AI v1.0 platform represents a comprehensive, end-to-end data analytics and financial engineering solution designed to evaluate securitisation pools under the IFRS-9 framework. By generating a synthetic, statistically correlated dataset of 55,000+ retail and commercial loans, this engine calculates Expected Credit Losses (ECL) utilizing a proprietary Machine Learning Probability of Default (PD) model. Furthermore, the system aggregates these exposures into securitised pools, tranches the risk into an explicit hierarchy (AAA down to Equity), and routes collections through a deterministic cash-flow waterfall. Finally, macroeconomic stress testing is applied to evaluate structural resilience, gamified via a Streamlit interface.

## 2. Historical Context: The 2008 Securitisation Crisis
To understand the necessity of the MatRisk AI platform, one must analyze the mechanics of the 2007-2008 Global Financial Crisis (GFC). During the GFC, subprime mortgages were pooled into Residential Mortgage-Backed Securities (RMBS) and further re-securitised into Collateralised Debt Obligations (CDOs). 
The fundamental flaw was the miscalculation of correlation among defaults. Rating agencies assumed that geographical diversification would prevent systemic defaults; thus, the Senior (AAA) tranches were deemed risk-free. However, when housing prices (HPI) declined nationally, Probability of Default (PD) and Loss Given Default (LGD) skyrocketed simultaneously across all pools. The Equity and Mezzanine tranches were quickly wiped out, and the supposedly "safe" AAA tranches absorbed unprecedented losses. MatRisk AI prevents this modeling oversight by explicitly linking HPI, unemployment, and interest rates to PD and LGD outputs in its stress-testing engine, ensuring that tail-risk scenarios (CRISIS) accurately reflect systemic collapses.

## 3. IFRS-9 Regulatory Framework & ECL Mathematics
Introduced by the International Accounting Standards Board (IASB), IFRS-9 requires institutions to recognize Expected Credit Losses (ECL) dynamically rather than waiting for an incurred loss. 

### 3.1 The ECL Equation
The core mathematical engine of MatRisk AI calculates ECL at the loan level using the following equation:
`ECL = PD × LGD × EAD × D`

Where:
*   **PD (Probability of Default):** The likelihood that a borrower will default over a given time horizon.
*   **LGD (Loss Given Default):** The percentage of exposure that will not be recovered post-default. Calculated as `1 - (Recovery Amount / EAD)`.
*   **EAD (Exposure at Default):** The predicted outstanding balance at the time of default.
*   **D (Discount Factor):** The time-value-of-money adjustment, calculated as `(1 + r)^-t`.

### 3.2 IFRS-9 Staging
MatRisk AI categorizes assets into three stages based on Significant Increase in Credit Risk (SICR):
*   **Stage 1 (Performing):** No SICR since origination. ECL is calculated using a 12-month PD.
*   **Stage 2 (Underperforming):** SICR detected (e.g., >30 DPD or >50 point drop in credit score). ECL utilizes Lifetime PD.
*   **Stage 3 (Impaired):** Objective evidence of impairment (>90 DPD). PD is effectively 100%, and ECL relies on LGD and EAD severity.

## 4. Machine Learning: Probability of Default (PD) Modeling
Unlike black-box models (e.g., Random Forests) which lack regulatory interpretability, MatRisk AI utilizes a Logistic Regression framework for the PD model.

### 4.1 Logistic Regression Mathematics
The model predicts the probability `p` that the target variable `y` (Default) equals 1. The log-odds are modeled as a linear combination of independent variables (LTV, DTI, Credit Score):

`ln( p / (1-p) ) = β_0 + β_1(LTV) + β_2(DTI) - β_3(CreditScore)`

This is transformed into a probability using the Sigmoid function:
`p = 1 / (1 + e^-(β_0 + βX))`

By scaling the inputs using `StandardScaler` from `scikit-learn`, the coefficients `β` directly indicate feature importance, allowing risk managers to explicitly explain why a loan was flagged for high default risk.

## 5. Tranching and Waterfall Cash Flow Mechanics
Securitisation transforms illiquid loans into tradable securities. MatRisk AI groups loans into Pools and slices them into Tranches based on Seniority.

### 5.1 Attachment and Detachment Points
Each tranche is defined by an Attachment Point (the threshold where it begins absorbing losses) and a Detachment Point (the threshold where its principal is completely wiped out).
For example, a Mezzanine Tranche with Attachment = 5% and Detachment = 10% is fully protected by the 5% Equity tranche beneath it, but will be wiped out if pool losses exceed 10%.

### 5.2 The Waterfall Engine
The Python-based waterfall engine acts as a deterministic state machine. Available cash (Collections - Defaults) is routed top-down:
1. Servicing Fees
2. AAA Interest -> AAA Principal
3. AA Interest -> AA Principal
...down to the Equity/Residual tranche. Losses are routed bottom-up.

## 6. Architecture & Technology Stack
*   **Data Generation:** Python, Numpy, Pandas (Vectorized).
*   **Database:** DuckDB (OLAP schema execution, Window functions, CTEs).
*   **Machine Learning:** Scikit-Learn, MLflow (Experiment tracking).
*   **Dashboarding:** Power BI (DAX) & Streamlit (Gamified UI).
*   **CI/CD & DevOps:** Docker, GitHub Actions, Pytest.

---

## 7. References
1. International Accounting Standards Board (IASB). (2014). *IFRS 9 Financial Instruments*.
2. Basel Committee on Banking Supervision (BCBS). (2015). *Guidance on credit risk and accounting for expected credit losses*.
3. Hull, J. C. (2018). *Risk Management and Financial Institutions* (5th ed.). Wiley.
4. Fabozzi, F. J. (2001). *The Handbook of Mortgage-Backed Securities*. McGraw-Hill.
5. Merton, R. C. (1974). On the Pricing of Corporate Debt: The Risk Structure of Interest Rates. *Journal of Finance*, 29(2), 449-470.
6. Vasicek, O. A. (2002). The distribution of loan portfolio value. *Risk*, 15(12), 160-162.
7. Bluhm, C., Overbeck, L., & Wagner, C. (2010). *An Introduction to Credit Risk Modeling*. Chapman and Hall/CRC.
8. Gorton, G. (2008). The Panic of 2007. *Federal Reserve Bank of Kansas City*.
9. Schönbucher, P. J. (2003). *Credit Derivatives Pricing Models*. Wiley.
10. McNeil, A. J., Frey, R., & Embrechts, P. (2015). *Quantitative Risk Management*. Princeton University Press.
11. Altman, E. I. (1968). Financial Ratios, Discriminant Analysis and the Prediction of Corporate Bankruptcy. *Journal of Finance*.
12. Crouhy, M., Galai, D., & Mark, R. (2014). *The Essentials of Risk Management*. McGraw Hill.
13. Lando, D. (2003). *Credit Risk Modeling: Theory and Applications*. Princeton University Press.
14. Chobanov, G., & Sironko, P. (2006). Value at Risk and Expected Shortfall. *Journal of Risk Finance*.
15. Engelmann, B., & Rau-Bredow, H. (2006). *Basel II Risk Parameters*. Springer.
16. Gupton, A., Finger, C. C., & Bhatia, M. (1997). *CreditMetrics – Technical Document*. J.P. Morgan.
17. Pykhtin, M. (2004). Multi-factor adjustment. *Risk*, 17(3), 85-90.
18. Gordy, M. B. (2003). A risk-factor model foundation for ratings-based bank capital rules. *Journal of Financial Intermediation*.
19. Miu, P., & Ozdemir, B. (2006). Basel requirement of downturn LGD: Modeling and estimating PD & LGD correlations. *Journal of Credit Risk*.
20. Witzany, J. (2017). *Credit Risk Management and Modeling*. Springer.
