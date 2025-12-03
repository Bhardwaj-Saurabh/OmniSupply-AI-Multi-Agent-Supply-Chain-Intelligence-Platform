# Finance Data Columns - Quick Reference Guide

This document provides a comprehensive list of all financial columns available across the 4 supply chain datasets for building the Finance Insight Agent.

---

## Dataset 1: DataCo Supply Chain Dataset (180,519 rows)

### Revenue & Sales Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Sales` | float64 | 327.75 | Total sales amount per order |
| `Sales per customer` | float64 | 314.64 | Average sales per customer |
| `Order Item Total` | float64 | 327.75 | Line item total (quantity × price) |

### Profit Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Benefit per order` | float64 | 91.25 | Profit/benefit per order |
| `Order Profit Per Order` | float64 | 91.25 | Profit amount per order |
| `Order Item Profit Ratio` | float64 | 0.29 | Profit margin percentage (0-1) |

### Pricing Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Product Price` | float64 | 327.75 | Product list price |
| `Order Item Product Price` | float64 | 327.75 | Price of item in order |

### Discount Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Order Item Discount` | float64 | 13.11 | Discount amount in dollars |
| `Order Item Discount Rate` | float64 | 0.04 | Discount rate percentage (0-1) |

### Payment & Transaction Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Type` | object | DEBIT | Payment type (DEBIT, CASH, TRANSFER, PAYMENT) |

### Quantity Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Order Item Quantity` | int64 | 4 | Quantity of items ordered |

### Time-Series Columns (for Cashflow Forecasting)
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `order date (DateOrders)` | object | 2/3/2018 22:56 | Order placement date/time |
| `shipping date (DateOrders)` | object | 2/3/2018 22:56 | Shipping date/time |
| `Days for shipping (real)` | int64 | 3 | Actual days to ship |
| `Days for shipment (scheduled)` | int64 | 4 | Scheduled days to ship |

### Categorical Dimensions (for Analysis)
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Category Name` | object | Sporting Goods | Product category |
| `Department Name` | object | Fan Shop | Department |
| `Customer Segment` | object | Consumer | Customer segment |
| `Order Region` | object | West | Geographic region |
| `Order State` | object | California | State/province |
| `Order Country` | object | United States | Country |
| `Shipping Mode` | object | Standard Class | Shipping method |
| `Delivery Status` | object | Advance shipping | Delivery performance |

### Risk Indicators
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Late_delivery_risk` | int64 | 0 | Late delivery risk flag (0/1) |

---

## Dataset 2: Retail Supply Chain Sales Dataset (9,994 rows)

### Revenue & Sales Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Sales` | float64 | 261.96 | Sales amount per transaction |

### Profit Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Profit` | float64 | 41.9136 | Profit per transaction (can be negative) |

### Discount Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Discount` | float64 | 0.0 | Discount rate (0.0 to 1.0) |

### Quantity Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Quantity` | int64 | 2 | Quantity of items sold |

### Time-Series Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Order Date` | datetime64 | 2016-08-11 | Order date |
| `Ship Date` | datetime64 | 2016-11-11 | Ship date |

### Categorical Dimensions
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Category` | object | Furniture | Product category |
| `Sub-Category` | object | Bookcases | Product sub-category |
| `Segment` | object | Consumer | Customer segment (Consumer, Corporate, Home Office) |
| `Ship Mode` | object | Second Class | Shipping mode |
| `Country` | object | United States | Country |
| `City` | object | Henderson | City |
| `State` | object | Kentucky | State |
| `Region` | object | South | Region |

### Return Indicator
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Returned` | object | Not | Return status (Not, Yes) |

---

## Dataset 3: Supply Chain Data (100 rows)

### Revenue & Sales Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Revenue generated` | float64 | 8661.996792 | Total revenue per product |
| `Number of products sold` | int64 | 802 | Units sold |

### Cost Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Manufacturing costs` | float64 | 46.279879 | Manufacturing cost per unit |
| `Shipping costs` | float64 | 2.956572 | Shipping cost per unit |
| `Costs` | float64 | 187.752075 | Total costs (comprehensive) |

### Pricing Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Price` | float64 | 69.808006 | Product price |

### Inventory Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Stock levels` | int64 | 58 | Current stock level |
| `Availability` | int64 | 55 | Product availability |

### Lead Time Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Lead times` | int64 | 7 | Lead time in days |
| `Lead time` | int64 | 29 | Another lead time metric |
| `Manufacturing lead time` | int64 | 29 | Manufacturing lead time |
| `Shipping times` | int64 | 10 | Shipping time in days |

### Order & Production Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Order quantities` | int64 | 96 | Order quantity |
| `Production volumes` | int64 | 215 | Production volume |

### Quality Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Defect rates` | float64 | 0.226410 | Product defect rate |
| `Inspection results` | object | Pending | Inspection status (Pending, Pass, Fail) |

### Categorical Dimensions
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `Product type` | object | haircare | Product type (haircare, skincare, cosmetics) |
| `SKU` | object | SKU0 | Stock keeping unit |
| `Transportation modes` | object | Road | Transport mode (Road, Rail, Air) |
| `Routes` | object | Route B | Shipping route |
| `Location` | object | Mumbai | Location |
| `Shipping carriers` | object | Carrier B | Shipping carrier |
| `Supplier name` | object | Supplier 1 | Supplier name |
| `Customer demographics` | object | Non-binary | Customer demographics |

---

## Dataset 4: Dynamic Logistics Dataset (32,065 rows)

### Cost Proxy Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `fuel_consumption_rate` | float64 | 5.136512 | Fuel consumption rate (operational cost proxy) |

### Inventory Columns
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `warehouse_inventory_level` | float64 | 985.716862 | Warehouse inventory level |

### Operational Metrics (Indirect Financial Impact)
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `loading_unloading_time` | float64 | 4.951392 | Loading/unloading time (hours) |
| `handling_equipment_availability` | float64 | 0.481294 | Equipment availability (0-1) |
| `order_fulfillment_status` | float64 | 0.761166 | Fulfillment status score |
| `customs_clearance_time` | float64 | 0.502006 | Customs clearance time |

### Risk Indicators (Financial Impact)
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `route_risk_level` | float64 | 1.182116 | Route risk level |
| `disruption_likelihood_score` | float64 | 0.506152 | Disruption probability |
| `delay_probability` | float64 | 0.885291 | Delay probability |
| `risk_classification` | object | Moderate Risk | Risk category |
| `delivery_time_deviation` | float64 | 9.110682 | Delivery time variance |

### Time-Series Column
| Column Name | Data Type | Sample Value | Description |
|-------------|-----------|--------------|-------------|
| `timestamp` | datetime64 | 2021-01-01 00:00:00 | Timestamp of reading |

---

## Financial Calculations Possible

### P&L Statement Components

#### Revenue
```python
# Total Revenue
total_revenue = dataco_df['Sales'].sum()  # $36.7M
total_revenue += retail_df['Sales'].sum()  # +$2.3M
total_revenue += supply_chain_df['Revenue generated'].sum()  # +$577K

# Revenue by Period
monthly_revenue = dataco_df.groupby(pd.Grouper(key='order_date', freq='M'))['Sales'].sum()

# Revenue by Category
revenue_by_category = dataco_df.groupby('Category Name')['Sales'].sum()

# Revenue by Customer Segment
revenue_by_segment = retail_df.groupby('Segment')['Sales'].sum()
```

#### Cost of Goods Sold (COGS)
```python
# From Supply Chain dataset (direct)
total_mfg_costs = supply_chain_df['Manufacturing costs'].sum()

# Derived from profit data
cogs = dataco_df['Sales'] - dataco_df['Order Profit Per Order']

# From Retail dataset
cogs_retail = retail_df['Sales'] - retail_df['Profit']
```

#### Gross Profit
```python
# Direct measurement (DataCo)
gross_profit = dataco_df['Order Profit Per Order'].sum()  # $3.97M

# Direct measurement (Retail)
gross_profit_retail = retail_df['Profit'].sum()  # $286K

# Gross Margin
gross_margin = (gross_profit / total_revenue) * 100  # 10.78%
```

#### Operating Expenses
```python
# Shipping & Logistics
shipping_costs = supply_chain_df['Shipping costs'].sum()  # $555

# Discounts (expense)
discount_expense = dataco_df['Order Item Discount'].sum()

# Total Operating Costs
opex = supply_chain_df['Costs'].sum()  # $52,925

# Estimated OpEx as % of revenue
opex_ratio = opex / revenue_generated  # For budgeting
```

#### Net Profit
```python
# Net Profit = Gross Profit - Operating Expenses
net_profit = gross_profit - shipping_costs - discount_expense

# Net Margin
net_margin = (net_profit / total_revenue) * 100
```

### Expense Analysis

#### Shipping Cost Analysis
```python
# Cost by Shipping Mode
shipping_cost_by_mode = dataco_df.groupby('Shipping Mode')['Order Item Total'].mean()

# Fuel costs (proxy from logistics data)
fuel_costs = dynamic_logistics_df['fuel_consumption_rate'].sum()

# Transportation mode efficiency
transport_cost_by_mode = supply_chain_df.groupby('Transportation modes')['Shipping costs'].mean()
```

#### Discount Analysis
```python
# Total discount spend
total_discounts = dataco_df['Order Item Discount'].sum()

# Average discount rate
avg_discount_rate = dataco_df['Order Item Discount Rate'].mean()  # 4%

# Discount by customer segment
discount_by_segment = retail_df.groupby('Segment')['Discount'].mean()

# Discount effectiveness (volume vs margin)
discount_tiers = pd.cut(retail_df['Discount'], bins=[0, 0.1, 0.2, 0.3, 1.0])
effectiveness = retail_df.groupby(discount_tiers).agg({
    'Sales': 'sum',
    'Profit': 'sum',
    'Quantity': 'sum'
})
```

#### Manufacturing Cost Analysis
```python
# Cost per unit
cost_per_unit = supply_chain_df['Manufacturing costs'].mean()  # $47.27

# Cost efficiency
supply_chain_df['cost_efficiency'] = supply_chain_df['Revenue generated'] / supply_chain_df['Manufacturing costs']

# Production volume impact
production_analysis = supply_chain_df.groupby('Production volumes').agg({
    'Manufacturing costs': 'mean',
    'Revenue generated': 'sum'
})
```

#### Inventory Carrying Costs
```python
# Average inventory value
avg_inventory = supply_chain_df['Stock levels'].mean()

# Inventory turnover
inventory_turnover = total_cogs / avg_inventory

# Days Inventory Outstanding
dio = (avg_inventory / total_cogs) * 365

# Slow-moving inventory
slow_movers = supply_chain_df[supply_chain_df['Number of products sold'] < threshold]
```

### Cashflow Forecasting

#### Revenue Forecasting
```python
# Prepare time-series data
dataco_df['order_date'] = pd.to_datetime(dataco_df['order date (DateOrders)'])
daily_sales = dataco_df.groupby('order_date')['Sales'].sum()

# ARIMA model
from statsmodels.tsa.arima.model import ARIMA
model = ARIMA(daily_sales, order=(5,1,0))
forecast = model.fit().forecast(steps=90)

# Prophet model
from prophet import Prophet
df_prophet = daily_sales.reset_index()
df_prophet.columns = ['ds', 'y']
model = Prophet()
model.fit(df_prophet)
future = model.make_future_dataframe(periods=90)
forecast = model.predict(future)
```

#### Cash Conversion Cycle
```python
# Days Sales Outstanding (estimated)
payment_weights = {
    'CASH': 0,      # immediate
    'DEBIT': 30,    # 30 days
    'TRANSFER': 20, # 20 days
    'PAYMENT': 45   # 45 days
}
payment_dist = dataco_df['Type'].value_counts(normalize=True)
weighted_dso = sum(payment_weights[k] * payment_dist.get(k, 0) for k in payment_weights)

# Days Inventory Outstanding
dio = (supply_chain_df['Stock levels'].mean() / total_cogs) * 365

# Days Payable Outstanding (assumed)
dpo = 45  # Industry standard

# Cash Conversion Cycle
ccc = weighted_dso + dio - dpo
```

#### Working Capital Forecast
```python
# Inventory investment required
forecast_sales = revenue_forecast
forecast_cogs = forecast_sales * (1 - gross_margin)
forecast_inventory = forecast_cogs * (dio / 365)

# Accounts Receivable forecast
forecast_ar = forecast_sales * (weighted_dso / 365)

# Working capital requirement
working_capital = forecast_inventory + forecast_ar - forecast_ap
```

### Financial KPIs

#### Profitability KPIs
```python
# Gross Profit Margin
gross_margin = (dataco_df['Order Profit Per Order'].sum() / dataco_df['Sales'].sum()) * 100

# Net Profit Margin
net_margin = (net_profit / total_revenue) * 100

# Profit per Order
profit_per_order = dataco_df['Order Profit Per Order'].mean()

# Return on Sales
ros = (net_profit / total_revenue) * 100
```

#### Revenue KPIs
```python
# Revenue Growth Rate
revenue_current = dataco_df[dataco_df['order_date'] >= '2017-01-01']['Sales'].sum()
revenue_prior = dataco_df[dataco_df['order_date'] < '2017-01-01']['Sales'].sum()
revenue_growth = ((revenue_current - revenue_prior) / revenue_prior) * 100

# Average Transaction Value
avg_transaction = dataco_df['Sales'].mean()

# Revenue per Customer
revenue_per_customer = dataco_df.groupby('Customer Id')['Sales'].sum().mean()
```

#### Cost KPIs
```python
# Shipping Cost Ratio
shipping_cost_ratio = (total_shipping_costs / total_revenue) * 100

# Discount Rate
discount_rate = (total_discounts / (total_revenue + total_discounts)) * 100

# Cost per Order
cost_per_order = total_costs / total_orders
```

#### Efficiency KPIs
```python
# Order Fulfillment Cost
fulfillment_cost = shipping_costs / total_orders

# Perfect Order Rate
perfect_orders = len(dataco_df[dataco_df['Late_delivery_risk'] == 0])
perfect_order_rate = (perfect_orders / len(dataco_df)) * 100

# Cost to Serve
cost_to_serve = total_supply_chain_cost / total_units_sold
```

---

## SQL Query Examples for Finance Agent

### P&L Report Query
```sql
SELECT
    DATE_TRUNC('month', order_date) as month,
    SUM(sales) as total_revenue,
    SUM(sales - order_profit_per_order) as cogs,
    SUM(order_profit_per_order) as gross_profit,
    SUM(order_item_discount) as discount_expense,
    SUM(order_profit_per_order) - SUM(order_item_discount) as net_profit,
    (SUM(order_profit_per_order) / SUM(sales)) * 100 as gross_margin,
    ((SUM(order_profit_per_order) - SUM(order_item_discount)) / SUM(sales)) * 100 as net_margin
FROM dataco_supply_chain
WHERE order_date >= '2017-01-01' AND order_date < '2017-04-01'
GROUP BY DATE_TRUNC('month', order_date)
ORDER BY month;
```

### Expense Anomaly Detection Query
```sql
WITH shipping_baseline AS (
    SELECT
        AVG(sales) as avg_sales,
        STDDEV(sales) as std_sales
    FROM dataco_supply_chain
    WHERE shipping_mode = 'Same Day'
)
SELECT
    order_date,
    shipping_mode,
    sales,
    (sales - avg_sales) / std_sales as z_score
FROM dataco_supply_chain, shipping_baseline
WHERE shipping_mode = 'Same Day'
  AND ABS((sales - avg_sales) / std_sales) > 2
ORDER BY ABS(z_score) DESC;
```

### Discount Effectiveness Query
```sql
SELECT
    CASE
        WHEN order_item_discount_rate = 0 THEN '0%'
        WHEN order_item_discount_rate <= 0.10 THEN '1-10%'
        WHEN order_item_discount_rate <= 0.20 THEN '11-20%'
        ELSE '>20%'
    END as discount_tier,
    COUNT(*) as order_count,
    AVG(sales) as avg_order_value,
    SUM(order_profit_per_order) as total_profit,
    AVG(order_item_profit_ratio) as avg_margin
FROM dataco_supply_chain
GROUP BY discount_tier
ORDER BY discount_tier;
```

### Cashflow Forecast Query
```sql
SELECT
    DATE_TRUNC('week', order_date) as week,
    SUM(sales) as revenue,
    -- Estimate cash collection based on payment type
    SUM(CASE
        WHEN type = 'CASH' THEN sales
        ELSE 0
    END) as immediate_cash,
    SUM(CASE
        WHEN type IN ('DEBIT', 'TRANSFER') THEN sales
        ELSE 0
    END) as delayed_cash_30days,
    SUM(CASE
        WHEN type = 'PAYMENT' THEN sales
        ELSE 0
    END) as delayed_cash_45days
FROM dataco_supply_chain
WHERE order_date >= CURRENT_DATE - INTERVAL '90 days'
GROUP BY week
ORDER BY week;
```

---

## Column Usage Summary

### For P&L Reporting:
- **Revenue:** `Sales`, `Sales per customer`, `Revenue generated`
- **COGS:** Derive from `Sales - Order Profit Per Order` or use `Manufacturing costs`
- **Gross Profit:** `Order Profit Per Order`, `Profit`, `Benefit per order`
- **Operating Expenses:** `Shipping costs`, `Costs`, `Order Item Discount`
- **Net Profit:** Calculate from above components

### For Expense Analysis:
- **Shipping:** `Shipping Mode`, `Shipping costs`, `fuel_consumption_rate`, `Transportation modes`
- **Discounts:** `Order Item Discount`, `Order Item Discount Rate`, `Discount`
- **Manufacturing:** `Manufacturing costs`, `Manufacturing lead time`, `Production volumes`
- **Inventory:** `Stock levels`, `warehouse_inventory_level`

### For Cashflow Forecasting:
- **Time-Series:** `order date (DateOrders)`, `Order Date`, `timestamp`
- **Payment Timing:** `Type`, `Days for shipping (real)`, `Days for shipment (scheduled)`
- **Revenue:** `Sales`, `Revenue generated`
- **Costs:** `Manufacturing costs`, `Shipping costs`, `Costs`
- **Inventory:** `Stock levels`, `Number of products sold`

### For Dimensional Analysis:
- **Product:** `Category Name`, `Product Name`, `SKU`, `Product type`, `Sub-Category`
- **Customer:** `Customer Segment`, `Segment`, `Customer demographics`, `Customer Id`
- **Geography:** `Order Region`, `Order State`, `Order Country`, `City`, `Location`
- **Time:** `order date (DateOrders)`, `Order Date`, `timestamp`

---

**Last Updated:** December 2, 2025
**Total Columns Documented:** 100+
**Datasets Covered:** 4
**Total Financial Metrics:** 50+
