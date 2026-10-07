# Power BI Dashboard Specification

## 1. Executive Risk
- **Visuals:** KPIs for Total Principal, Average PD, Total ECL, Weighted Average LTV.
- **Interactions:** Month-over-Month trend lines for Delinquencies.

## 2. IFRS 9 Credit Risk
- **Visuals:** Stage 1, 2, and 3 distribution pie chart.
- **Fields:** DimLoan[RiskGrade], FactECL[Stage], FactECL[ECL].

## 3. Securitisation Pools
- **Visuals:** Matrix table showing Pool ID, Total Balance, WA Interest Rate, WA LTV.

## 4. Tranche Risk
- **Visuals:** Stacked Bar Chart for Tranche levels (AAA, AA, A, BBB, Equity) vs Expected Losses.

## 5. Waterfall
- **Visuals:** Waterfall Chart demonstrating cash allocations from Pool Balance down to Junior Tranches.

## 6. Stress Testing
- **Visuals:** Line chart comparing Base, Mild, Moderate, Severe, and Crisis scenarios.
- **Slicers:** Scenario Name.

## 7. Investor Reporting
- **Visuals:** Investor Risk-Adjusted Return metrics using advanced DAX.

## 8. Risk Arena
- **Visuals:** Gamified dashboard view showing dynamic Risk Scores out of 100 based on selected parameters.
