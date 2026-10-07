-- 03_views.sql
-- Create advanced views utilizing window functions and CTEs

-- 1. Vintage Analysis View
CREATE VIEW view_vintage_analysis AS
SELECT 
    DATE_TRUNC('month', l.origination_date) AS vintage_month,
    p.report_date,
    SUM(l.original_principal) as origination_volume,
    SUM(p.balance) as remaining_balance,
    SUM(CASE WHEN p.delinquency_days > 90 THEN p.balance ELSE 0 END) as default_balance,
    SUM(CASE WHEN p.delinquency_days > 90 THEN p.balance ELSE 0 END) / NULLIF(SUM(l.original_principal), 0) AS cumulative_default_rate
FROM loans l
JOIN loan_performance p ON l.loan_id = p.loan_id
GROUP BY 1, 2;

-- 2. Rolling Risk View
CREATE VIEW view_rolling_risk AS
WITH MonthlyRisk AS (
    SELECT 
        report_date,
        pool_id,
        SUM(p.balance) as pool_balance,
        SUM(CASE WHEN p.delinquency_days > 30 THEN p.balance ELSE 0 END) as delinq_30_balance
    FROM loan_performance p
    JOIN loans l ON p.loan_id = l.loan_id
    GROUP BY 1, 2
)
SELECT 
    *,
    delinq_30_balance / NULLIF(pool_balance, 0) as delinq_rate,
    AVG(delinq_30_balance / NULLIF(pool_balance, 0)) OVER (
        PARTITION BY pool_id 
        ORDER BY report_date 
        ROWS BETWEEN 2 PRECEDING AND CURRENT ROW
    ) as rolling_3m_delinq_rate
FROM MonthlyRisk;

-- 3. Concentration Analysis
CREATE VIEW view_concentration_analysis AS
SELECT 
    l.pool_id,
    c.state,
    SUM(l.current_balance) as state_balance,
    SUM(l.current_balance) / SUM(SUM(l.current_balance)) OVER (PARTITION BY l.pool_id) as state_concentration_pct
FROM loans l
JOIN customers c ON l.customer_id = c.customer_id
WHERE l.current_balance > 0
GROUP BY 1, 2;
