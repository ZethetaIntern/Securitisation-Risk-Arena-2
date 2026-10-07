# Relationships

- DimDate[Date] 1:* FactLoanPerformance[ReportDate] (Active)
- DimLoan[LoanID] 1:* FactLoanPerformance[LoanID] (Active)
- DimCustomer[CustomerID] 1:* DimLoan[CustomerID] (Active)
- DimPool[PoolID] 1:* DimLoan[PoolID] (Active)
- DimPool[PoolID] 1:* DimTranche[PoolID] (Active)
- DimTranche[TrancheID] 1:* FactWaterfall[TrancheID] (Active)
- DimScenario[ScenarioID] 1:* FactStress[ScenarioID] (Active)
