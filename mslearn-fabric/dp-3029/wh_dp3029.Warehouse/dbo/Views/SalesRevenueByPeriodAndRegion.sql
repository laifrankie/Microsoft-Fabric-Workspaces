-- Auto Generated (Do not modify) 124EC0D5A8E4E2AFCF1EBEB2947B9D821A78AA5435A468A01724AB4AC618DD39
 
-- Step 1: Plan the view structure.
-- We need to show sales revenue data grouped by year, month, month name, and sales region.
-- "Sales region" is not a direct column, but can be interpreted as [CountryRegion] from [DimCustomer].
-- Revenue is the sum of [SalesTotal] from [FactSalesOrder].
-- We need to join [FactSalesOrder] to [DimDate] (for year, month, month name) and [DimCustomer] (for region).

-- Step 2: Write the CREATE VIEW statement in the dbo schema.
-- The view will be named [SalesRevenueByPeriodAndRegion] (since no such view exists in schema).
-- The view will select: Year, Month, MonthName, CountryRegion, SUM(SalesTotal) AS SalesRevenue.
-- Group by Year, Month, MonthName, CountryRegion.

CREATE VIEW [dbo].[SalesRevenueByPeriodAndRegion]
AS
SELECT
    d.[Year],
    d.[Month],
    d.[MonthName],
    c.[CountryRegion] AS [SalesRegion],
    SUM(f.[SalesTotal]) AS [SalesRevenue]
FROM
    [dbo].[FactSalesOrder] f
    INNER JOIN [dbo].[DimDate] d
        ON f.[SalesOrderDateKey] = d.[DateKey]
    INNER JOIN [dbo].[DimCustomer] c
        ON f.[CustomerKey] = c.[CustomerKey]
GROUP BY
    d.[Year],
    d.[Month],
    d.[MonthName],
    c.[CountryRegion];