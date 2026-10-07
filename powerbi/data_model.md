# Power BI Data Model Specification

## Star Schema Design
The data model uses a Star Schema for optimal Power BI performance.

### Fact Tables
- **FactLoanPerformance**: Monthly snapshot of loan balances and delinquency.
- **FactCashFlow**: Scheduled vs Actual payments, recoveries.
- **FactECL**: Loan-level Expected Credit Loss outputs (PD, LGD, EAD, ECL).
- **FactWaterfall**: Tranche-level cash allocation and shortfalls.
- **FactStress**: Scenario-based ECL outputs.

### Dimension Tables
- **DimLoan**: Loan-level attributes (Original Principal, Interest Rate, LTV, DTI).
- **DimCustomer**: Customer attributes (Age, Income, Employment, Credit Score).
- **DimPool**: Securitisation Pool attributes.
- **DimTranche**: Tranche structure (AAA, AA, A, BBB, Equity) and attachment points.
- **DimDate**: Standard Date dimension for time intelligence.
- **DimGeography**: State and City mappings for concentration risk.
- **DimScenario**: Stress Testing scenarios (BASE, MILD, MODERATE, SEVERE, CRISIS).
