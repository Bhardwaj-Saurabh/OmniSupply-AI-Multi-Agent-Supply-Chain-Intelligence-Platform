"""
Finance Insight Agent - Capability Analysis
===========================================

This script analyzes all 4 supply chain datasets to determine:
1. Available financial metrics (revenue, costs, profits, discounts)
2. P&L components we can calculate (gross profit, operating expenses, net profit)
3. Expense categories and patterns
4. Cashflow-related data (orders, payments, dates)
5. Time-series data for forecasting
"""

import os
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

# Define data directory
import pathlib
script_dir = pathlib.Path(__file__).parent.absolute()
data_dir = script_dir.parent / 'data'

# Read CSV files with encoding handling
def read_csv_with_encoding(file_path):
    """Try to read CSV with different encodings"""
    encodings = ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    for encoding in encodings:
        try:
            df = pd.read_csv(file_path, encoding=encoding)
            return df
        except UnicodeDecodeError:
            continue
    raise ValueError(f"Could not read {file_path} with any encoding")

# Load all datasets
print("Loading datasets...")
dataco_df = read_csv_with_encoding(os.path.join(data_dir, 'DataCoSupplyChainDataset.csv'))
dynamic_logistics_df = read_csv_with_encoding(os.path.join(data_dir, 'dynamic_supply_chain_logistics_dataset.csv'))
supply_chain_df = read_csv_with_encoding(os.path.join(data_dir, 'supply_chain_data.csv'))
retail_sales_df = pd.read_excel(os.path.join(data_dir, 'Retail-Supply-Chain-Sales-Dataset.xlsx'))

print("\n" + "="*100)
print("FINANCE INSIGHT AGENT - COMPREHENSIVE CAPABILITY ANALYSIS")
print("="*100)

# ============================================================================
# PART 1: FINANCIAL METRICS INVENTORY
# ============================================================================
print("\n\n" + "="*100)
print("PART 1: AVAILABLE FINANCIAL METRICS ACROSS ALL 4 DATASETS")
print("="*100)

print("\n\n1. DATACO SUPPLY CHAIN DATASET (180,519 rows)")
print("-"*100)

# Extract financial columns
dataco_financial_cols = {
    'Revenue/Sales': [],
    'Costs/Expenses': [],
    'Profit/Margin': [],
    'Discounts': [],
    'Payment/Transaction': [],
    'Pricing': []
}

for col in dataco_df.columns:
    col_lower = col.lower()
    if any(x in col_lower for x in ['sales', 'revenue']):
        dataco_financial_cols['Revenue/Sales'].append(col)
    if any(x in col_lower for x in ['cost', 'expense']):
        dataco_financial_cols['Costs/Expenses'].append(col)
    if any(x in col_lower for x in ['profit', 'benefit', 'margin']):
        dataco_financial_cols['Profit/Margin'].append(col)
    if any(x in col_lower for x in ['discount']):
        dataco_financial_cols['Discounts'].append(col)
    if any(x in col_lower for x in ['payment', 'type']) and col == 'Type':
        dataco_financial_cols['Payment/Transaction'].append(col)
    if any(x in col_lower for x in ['price']):
        dataco_financial_cols['Pricing'].append(col)

for category, cols in dataco_financial_cols.items():
    print(f"\n  {category}:")
    for col in cols:
        sample_val = dataco_df[col].iloc[0] if len(cols) > 0 and col in dataco_df.columns else None
        print(f"    - {col}: {sample_val}")

# Analyze payment types
print("\n  Payment Type Distribution:")
if 'Type' in dataco_df.columns:
    payment_dist = dataco_df['Type'].value_counts()
    for ptype, count in payment_dist.items():
        print(f"    - {ptype}: {count:,} ({count/len(dataco_df)*100:.1f}%)")

# Calculate some key metrics
print("\n  Key Financial Statistics:")
if 'Sales' in dataco_df.columns:
    print(f"    - Total Sales: ${dataco_df['Sales'].sum():,.2f}")
    print(f"    - Average Sales per Order: ${dataco_df['Sales'].mean():,.2f}")
    print(f"    - Min Sales: ${dataco_df['Sales'].min():,.2f}")
    print(f"    - Max Sales: ${dataco_df['Sales'].max():,.2f}")

if 'Order Profit Per Order' in dataco_df.columns:
    print(f"    - Total Profit: ${dataco_df['Order Profit Per Order'].sum():,.2f}")
    print(f"    - Average Profit per Order: ${dataco_df['Order Profit Per Order'].mean():,.2f}")

if 'Sales' in dataco_df.columns and 'Order Profit Per Order' in dataco_df.columns:
    profit_margin = (dataco_df['Order Profit Per Order'].sum() / dataco_df['Sales'].sum()) * 100
    print(f"    - Overall Profit Margin: {profit_margin:.2f}%")

# ============================================================================
print("\n\n2. RETAIL SUPPLY CHAIN SALES DATASET (9,994 rows)")
print("-"*100)

retail_financial_cols = {
    'Revenue/Sales': [],
    'Costs/Expenses': [],
    'Profit/Margin': [],
    'Discounts': [],
    'Quantity': []
}

for col in retail_sales_df.columns:
    col_lower = col.lower()
    if any(x in col_lower for x in ['sales', 'revenue']):
        retail_financial_cols['Revenue/Sales'].append(col)
    if any(x in col_lower for x in ['cost']):
        retail_financial_cols['Costs/Expenses'].append(col)
    if any(x in col_lower for x in ['profit']):
        retail_financial_cols['Profit/Margin'].append(col)
    if any(x in col_lower for x in ['discount']):
        retail_financial_cols['Discounts'].append(col)
    if any(x in col_lower for x in ['quantity']):
        retail_financial_cols['Quantity'].append(col)

for category, cols in retail_financial_cols.items():
    print(f"\n  {category}:")
    for col in cols:
        sample_val = retail_sales_df[col].iloc[0] if len(cols) > 0 and col in retail_sales_df.columns else None
        print(f"    - {col}: {sample_val}")

# Calculate metrics
print("\n  Key Financial Statistics:")
if 'Sales' in retail_sales_df.columns:
    print(f"    - Total Sales: ${retail_sales_df['Sales'].sum():,.2f}")
    print(f"    - Average Sales per Transaction: ${retail_sales_df['Sales'].mean():,.2f}")

if 'Profit' in retail_sales_df.columns:
    print(f"    - Total Profit: ${retail_sales_df['Profit'].sum():,.2f}")
    print(f"    - Average Profit per Transaction: ${retail_sales_df['Profit'].mean():,.2f}")
    print(f"    - Negative Profit Transactions: {len(retail_sales_df[retail_sales_df['Profit'] < 0]):,} ({len(retail_sales_df[retail_sales_df['Profit'] < 0])/len(retail_sales_df)*100:.1f}%)")

if 'Sales' in retail_sales_df.columns and 'Profit' in retail_sales_df.columns:
    profit_margin = (retail_sales_df['Profit'].sum() / retail_sales_df['Sales'].sum()) * 100
    print(f"    - Overall Profit Margin: {profit_margin:.2f}%")

if 'Discount' in retail_sales_df.columns:
    print(f"    - Average Discount: {retail_sales_df['Discount'].mean()*100:.2f}%")
    print(f"    - Transactions with Discount: {len(retail_sales_df[retail_sales_df['Discount'] > 0]):,} ({len(retail_sales_df[retail_sales_df['Discount'] > 0])/len(retail_sales_df)*100:.1f}%)")

# ============================================================================
print("\n\n3. SUPPLY CHAIN DATA (100 rows)")
print("-"*100)

supply_financial_cols = {
    'Revenue/Sales': [],
    'Costs/Expenses': [],
    'Pricing': []
}

for col in supply_chain_df.columns:
    col_lower = col.lower()
    if any(x in col_lower for x in ['revenue', 'sold']):
        supply_financial_cols['Revenue/Sales'].append(col)
    if any(x in col_lower for x in ['cost']):
        supply_financial_cols['Costs/Expenses'].append(col)
    if any(x in col_lower for x in ['price']):
        supply_financial_cols['Pricing'].append(col)

for category, cols in supply_financial_cols.items():
    print(f"\n  {category}:")
    for col in cols:
        sample_val = supply_chain_df[col].iloc[0] if len(cols) > 0 and col in supply_chain_df.columns else None
        print(f"    - {col}: {sample_val}")

print("\n  Key Financial Statistics:")
if 'Revenue generated' in supply_chain_df.columns:
    print(f"    - Total Revenue: ${supply_chain_df['Revenue generated'].sum():,.2f}")
    print(f"    - Average Revenue per Product: ${supply_chain_df['Revenue generated'].mean():,.2f}")

if 'Manufacturing costs' in supply_chain_df.columns:
    print(f"    - Total Manufacturing Costs: ${supply_chain_df['Manufacturing costs'].sum():,.2f}")
    print(f"    - Average Manufacturing Cost: ${supply_chain_df['Manufacturing costs'].mean():,.2f}")

if 'Shipping costs' in supply_chain_df.columns:
    print(f"    - Total Shipping Costs: ${supply_chain_df['Shipping costs'].sum():,.2f}")
    print(f"    - Average Shipping Cost: ${supply_chain_df['Shipping costs'].mean():,.2f}")

if 'Costs' in supply_chain_df.columns:
    print(f"    - Total Costs: ${supply_chain_df['Costs'].sum():,.2f}")

# Calculate gross profit
if 'Revenue generated' in supply_chain_df.columns and 'Manufacturing costs' in supply_chain_df.columns:
    gross_profit = supply_chain_df['Revenue generated'].sum() - supply_chain_df['Manufacturing costs'].sum()
    gross_margin = (gross_profit / supply_chain_df['Revenue generated'].sum()) * 100
    print(f"    - Gross Profit: ${gross_profit:,.2f}")
    print(f"    - Gross Margin: {gross_margin:.2f}%")

# ============================================================================
print("\n\n4. DYNAMIC LOGISTICS DATASET (32,065 rows)")
print("-"*100)
print("  Note: This dataset focuses on logistics operations, limited financial data")
print("  - Fuel consumption rates (operational cost proxy)")
print("  - Warehouse inventory levels (working capital indicator)")
print("  - No direct revenue/profit data")

# ============================================================================
# PART 2: P&L STATEMENT COMPONENTS
# ============================================================================
print("\n\n" + "="*100)
print("PART 2: P&L (Profit & Loss) STATEMENT COMPONENTS WE CAN BUILD")
print("="*100)

print("\n\nBased on available data, here's what P&L components we can construct:")

pl_components = {
    "1. REVENUE": {
        "sources": [
            "DataCo: 'Sales' column (180K+ transactions)",
            "DataCo: 'Sales per customer' column",
            "Retail: 'Sales' column (9,994 transactions)",
            "Supply Chain: 'Revenue generated' column"
        ],
        "calculations": [
            "Total Revenue = SUM(Sales)",
            "Revenue by Product Category",
            "Revenue by Customer Segment",
            "Revenue by Region/Geography",
            "Revenue by Time Period (daily/weekly/monthly)"
        ],
        "status": "✅ EXCELLENT - Multiple revenue sources available"
    },

    "2. COST OF GOODS SOLD (COGS)": {
        "sources": [
            "Supply Chain: 'Manufacturing costs' column",
            "Retail: Can derive from Sales - Profit",
            "DataCo: Can estimate from Sales and Profit data"
        ],
        "calculations": [
            "COGS = Sales - Gross Profit",
            "COGS by Product",
            "Cost per Unit",
            "Manufacturing Costs"
        ],
        "status": "✅ GOOD - Can be calculated or estimated"
    },

    "3. GROSS PROFIT": {
        "sources": [
            "DataCo: 'Benefit per order'",
            "DataCo: 'Order Profit Per Order'",
            "Retail: 'Profit' column",
            "Calculated: Revenue - COGS"
        ],
        "calculations": [
            "Gross Profit = Revenue - COGS",
            "Gross Margin % = (Gross Profit / Revenue) * 100",
            "Gross Profit by Product/Category",
            "Gross Profit Trends over Time"
        ],
        "status": "✅ EXCELLENT - Direct profit data available"
    },

    "4. OPERATING EXPENSES": {
        "sources": [
            "Supply Chain: 'Shipping costs'",
            "Supply Chain: 'Costs' column",
            "Dynamic Logistics: Fuel consumption (proxy for logistics costs)",
            "Retail: Implicit in Sales - Profit calculation"
        ],
        "calculations": [
            "Shipping/Logistics Costs",
            "Transportation Costs by Mode (Air, Rail, Road)",
            "Warehouse Operating Costs (proxy from inventory levels)",
            "Estimated based on order volume"
        ],
        "status": "⚠️ PARTIAL - Some operating costs available, others need estimation"
    },

    "5. DISCOUNTS & ALLOWANCES": {
        "sources": [
            "DataCo: 'Order Item Discount'",
            "DataCo: 'Order Item Discount Rate'",
            "Retail: 'Discount' column"
        ],
        "calculations": [
            "Total Discount Amount",
            "Average Discount Rate",
            "Discount Impact on Revenue",
            "Discount by Product Category/Customer Segment"
        ],
        "status": "✅ EXCELLENT - Detailed discount data"
    },

    "6. NET PROFIT": {
        "sources": [
            "Calculated: Gross Profit - Operating Expenses",
            "DataCo: 'Order Profit Per Order' (close proxy)"
        ],
        "calculations": [
            "Net Profit = Gross Profit - Operating Expenses - Discounts",
            "Net Margin % = (Net Profit / Revenue) * 100",
            "Net Profit by Product/Customer/Region",
            "Profit Trends over Time"
        ],
        "status": "✅ GOOD - Can be calculated with some assumptions"
    }
}

for component, details in pl_components.items():
    print(f"\n{component}")
    print("-" * 100)
    print(f"Status: {details['status']}")
    print(f"\nData Sources:")
    for source in details['sources']:
        print(f"  • {source}")
    print(f"\nPossible Calculations:")
    for calc in details['calculations']:
        print(f"  • {calc}")

# ============================================================================
# PART 3: EXPENSE CATEGORIZATION & ANALYSIS
# ============================================================================
print("\n\n" + "="*100)
print("PART 3: EXPENSE CATEGORIZATION AND PATTERN ANALYSIS CAPABILITIES")
print("="*100)

expense_categories = {
    "A. SHIPPING & LOGISTICS EXPENSES": {
        "data_sources": [
            "DataCo: 'Shipping Mode' (Standard, First Class, Same Day, Second Class)",
            "Supply Chain: 'Shipping costs' column",
            "Supply Chain: 'Transportation modes' (Road, Rail, Air)",
            "Dynamic Logistics: 'fuel_consumption_rate'"
        ],
        "analysis_capabilities": [
            "Breakdown by shipping mode (cost per mode)",
            "Trends in logistics costs over time",
            "Cost efficiency by transportation mode",
            "Fuel cost patterns and optimization opportunities"
        ],
        "patterns_detectable": [
            "Seasonal variations in shipping costs",
            "Cost spikes during peak periods",
            "Inefficient shipping routes",
            "Mode optimization opportunities (e.g., Air vs Road)"
        ]
    },

    "B. DISCOUNT & PROMOTIONAL EXPENSES": {
        "data_sources": [
            "DataCo: 'Order Item Discount' (dollar amounts)",
            "DataCo: 'Order Item Discount Rate' (percentages)",
            "Retail: 'Discount' column"
        ],
        "analysis_capabilities": [
            "Total discount spend per period",
            "Discount effectiveness (impact on sales volume)",
            "Discount by customer segment",
            "ROI of promotional campaigns"
        ],
        "patterns_detectable": [
            "Over-discounting trends",
            "Customer segments requiring heavy discounts",
            "Products with frequent discounting (margin erosion)",
            "Seasonal discount patterns"
        ]
    },

    "C. MANUFACTURING & PRODUCTION COSTS": {
        "data_sources": [
            "Supply Chain: 'Manufacturing costs'",
            "Supply Chain: 'Production volumes'",
            "Supply Chain: 'Manufacturing lead time'"
        ],
        "analysis_capabilities": [
            "Cost per unit produced",
            "Production efficiency metrics",
            "Cost variance analysis",
            "Impact of production volume on unit costs"
        ],
        "patterns_detectable": [
            "Economies of scale opportunities",
            "Cost increases over time",
            "Inefficient production batches",
            "Quality issues driving up costs (via defect rates)"
        ]
    },

    "D. INVENTORY CARRYING COSTS": {
        "data_sources": [
            "Supply Chain: 'Stock levels'",
            "Dynamic Logistics: 'warehouse_inventory_level'",
            "Calculated: Average inventory value"
        ],
        "analysis_capabilities": [
            "Inventory holding costs estimation",
            "Stockout costs (lost sales)",
            "Obsolescence risk by product age",
            "Optimal inventory levels"
        ],
        "patterns_detectable": [
            "Excess inventory (capital tied up)",
            "Frequent stockouts (opportunity cost)",
            "Slow-moving inventory",
            "Seasonal inventory patterns"
        ]
    },

    "E. CUSTOMER ACQUISITION & OPERATIONAL COSTS": {
        "data_sources": [
            "DataCo: 'Sales per customer'",
            "DataCo: Customer segments",
            "Retail: 'Segment' (Consumer, Corporate, Home Office)"
        ],
        "analysis_capabilities": [
            "Cost per customer segment",
            "Customer lifetime value estimation",
            "Segment profitability analysis",
            "Operational efficiency by segment"
        ],
        "patterns_detectable": [
            "High-cost, low-value customer segments",
            "Most profitable customer types",
            "Segments requiring high service costs",
            "Churn indicators (frequency of orders)"
        ]
    }
}

for category, details in expense_categories.items():
    print(f"\n{category}")
    print("-" * 100)
    print(f"\nData Sources:")
    for source in details['data_sources']:
        print(f"  • {source}")
    print(f"\nAnalysis Capabilities:")
    for capability in details['analysis_capabilities']:
        print(f"  • {capability}")
    print(f"\nPatterns We Can Detect:")
    for pattern in details['patterns_detectable']:
        print(f"  • {pattern}")

# ============================================================================
# PART 4: CASHFLOW FORECASTING CAPABILITIES
# ============================================================================
print("\n\n" + "="*100)
print("PART 4: CASHFLOW FORECASTING DATA & MODELS")
print("="*100)

cashflow_data = {
    "1. ORDER & TRANSACTION DATA": {
        "columns": [
            "DataCo: 'order date (DateOrders)' - 180K+ transactions",
            "DataCo: 'shipping date (DateOrders)' - delivery timing",
            "Retail: 'Order Date' and 'Ship Date'",
            "DataCo: 'Order Id' - unique transaction tracking"
        ],
        "time_coverage": "2015-2018 (DataCo), 2014-2017 (Retail)",
        "frequency": "Daily transaction data available",
        "use_for": [
            "Revenue forecasting by date",
            "Seasonal pattern detection",
            "Order volume trends",
            "Revenue recognition timing"
        ]
    },

    "2. PAYMENT DATA": {
        "columns": [
            "DataCo: 'Type' (DEBIT, CASH, TRANSFER, PAYMENT)"
        ],
        "categories": "4 payment types tracked",
        "use_for": [
            "Payment method mix analysis",
            "Cash collection patterns",
            "Days to payment estimation (DEBIT vs CASH)",
            "Working capital requirements"
        ]
    },

    "3. REVENUE STREAM DATA": {
        "columns": [
            "DataCo: 'Sales' - actual transaction amounts",
            "Retail: 'Sales' - retail transaction amounts",
            "Supply Chain: 'Revenue generated'",
            "DataCo: 'Sales per customer'"
        ],
        "granularity": "Order-level detail",
        "use_for": [
            "Cash inflow forecasting",
            "Revenue by time period",
            "Customer payment behavior",
            "Accounts Receivable estimation"
        ]
    },

    "4. COST & EXPENSE OUTFLOW DATA": {
        "columns": [
            "Supply Chain: 'Manufacturing costs'",
            "Supply Chain: 'Shipping costs'",
            "Supply Chain: 'Costs'",
            "DataCo: 'Order Item Discount' (cash outlay)"
        ],
        "use_for": [
            "Cash outflow forecasting",
            "Accounts Payable estimation",
            "Operating expense projections",
            "Discount impact on cash position"
        ]
    },

    "5. INVENTORY & WORKING CAPITAL DATA": {
        "columns": [
            "Supply Chain: 'Stock levels'",
            "Supply Chain: 'Number of products sold'",
            "Dynamic Logistics: 'warehouse_inventory_level'",
            "Retail: 'Quantity'"
        ],
        "use_for": [
            "Inventory investment forecasting",
            "Working capital requirements",
            "Cash tied up in inventory",
            "Inventory turnover patterns"
        ]
    },

    "6. TIMING & LEAD TIME DATA": {
        "columns": [
            "DataCo: 'Days for shipping (real)' vs 'Days for shipment (scheduled)'",
            "Supply Chain: 'Lead times'",
            "Supply Chain: 'Shipping times'",
            "Supply Chain: 'Manufacturing lead time'"
        ],
        "use_for": [
            "Cash conversion cycle calculation",
            "Days Sales Outstanding (DSO) estimation",
            "Days Inventory Outstanding (DIO)",
            "Days Payable Outstanding (DPO)"
        ]
    }
}

for data_type, details in cashflow_data.items():
    print(f"\n{data_type}")
    print("-" * 100)
    print(f"\nAvailable Columns:")
    for col in details['columns']:
        print(f"  • {col}")
    print(f"\nUse Cases for Cashflow Forecasting:")
    for use_case in details['use_for']:
        print(f"  • {use_case}")

# Cashflow forecast models
print("\n\nCASSHFLOW FORECAST MODELS WE CAN IMPLEMENT:")
print("-" * 100)

forecast_models = {
    "1. TIME-SERIES FORECASTING MODELS": {
        "models": [
            "ARIMA (AutoRegressive Integrated Moving Average)",
            "SARIMA (Seasonal ARIMA) - for seasonal patterns",
            "Prophet (Facebook) - handles seasonality and holidays",
            "LSTM (Long Short-Term Memory) neural networks"
        ],
        "data_requirements": "Daily/weekly/monthly sales data (✅ Available)",
        "forecast_horizon": "1-12 months ahead",
        "accuracy_factors": [
            "3+ years of historical data available",
            "Seasonal patterns detectable",
            "Sufficient transaction volume"
        ]
    },

    "2. REGRESSION-BASED MODELS": {
        "models": [
            "Multiple Linear Regression",
            "Random Forest Regression",
            "Gradient Boosting (XGBoost, LightGBM)"
        ],
        "features_available": [
            "Historical sales",
            "Seasonality (month, quarter)",
            "Customer segment",
            "Product category",
            "Discount rates",
            "Shipping mode",
            "Geographic region"
        ],
        "forecast_type": "Conditional forecasts (what-if scenarios)"
    },

    "3. CASH CONVERSION CYCLE MODEL": {
        "components": [
            "Days Sales Outstanding (DSO) = AR / (Revenue / 365)",
            "Days Inventory Outstanding (DIO) = Inventory / (COGS / 365)",
            "Days Payable Outstanding (DPO) = AP / (COGS / 365)",
            "CCC = DSO + DIO - DPO"
        ],
        "data_available": [
            "✅ Revenue data (for DSO)",
            "✅ COGS (can estimate)",
            "⚠️ AR/AP (need to estimate based on payment types)",
            "✅ Inventory levels"
        ],
        "output": "Working capital requirements forecast"
    },

    "4. SCENARIO-BASED CASHFLOW MODELS": {
        "scenarios": [
            "Best case (high sales, low costs)",
            "Base case (expected performance)",
            "Worst case (low sales, high costs)"
        ],
        "variables": [
            "Sales growth rate assumptions",
            "Discount rate changes",
            "Cost inflation",
            "Payment term changes",
            "Seasonal fluctuations"
        ],
        "output": "Range of cashflow outcomes with probabilities"
    }
}

for model_type, details in forecast_models.items():
    print(f"\n{model_type}")
    print("  " + "-" * 96)
    for key, value in details.items():
        if isinstance(value, list):
            print(f"  {key.replace('_', ' ').title()}:")
            for item in value:
                print(f"    • {item}")
        else:
            print(f"  {key.replace('_', ' ').title()}: {value}")

# ============================================================================
# PART 5: SPECIFIC FINANCIAL KPIs & METRICS
# ============================================================================
print("\n\n" + "="*100)
print("PART 5: SPECIFIC FINANCIAL KPIs & METRICS WE CAN TRACK")
print("="*100)

kpi_categories = {
    "PROFITABILITY METRICS": [
        ("Gross Profit Margin", "(Revenue - COGS) / Revenue", "✅ DataCo, Retail"),
        ("Net Profit Margin", "Net Profit / Revenue", "✅ DataCo, Retail"),
        ("Operating Margin", "Operating Profit / Revenue", "⚠️ Can estimate"),
        ("Return on Sales (ROS)", "Net Profit / Sales", "✅ Available"),
        ("Profit per Order", "Total Profit / Number of Orders", "✅ DataCo: 'Order Profit Per Order'"),
        ("Profit by Product", "Profit grouped by Product Category", "✅ Available"),
        ("Profit by Customer Segment", "Profit by Consumer/Corporate", "✅ Retail data"),
        ("Profit by Region", "Profit by State/Country", "✅ Geographic data available")
    ],

    "REVENUE METRICS": [
        ("Total Revenue", "SUM(Sales)", "✅ All datasets"),
        ("Revenue Growth Rate", "(Current Period - Prior Period) / Prior Period", "✅ Time-series available"),
        ("Average Transaction Value", "Total Revenue / Number of Transactions", "✅ Calculable"),
        ("Revenue per Customer", "Total Revenue / Unique Customers", "✅ DataCo: 'Sales per customer'"),
        ("Revenue by Product Category", "Sales grouped by Category", "✅ Available"),
        ("Revenue by Channel", "Online vs Offline (if distinguishable)", "⚠️ Limited data"),
        ("Revenue Concentration", "Top 20% products/customers % of revenue", "✅ Can calculate")
    ],

    "COST & EXPENSE METRICS": [
        ("Cost of Goods Sold (COGS)", "Direct costs of production", "✅ Supply Chain data"),
        ("Shipping Cost Ratio", "Shipping Costs / Revenue", "✅ Available"),
        ("Discount Rate", "Total Discounts / Gross Sales", "✅ Discount data available"),
        ("Cost per Order", "Total Costs / Number of Orders", "✅ Calculable"),
        ("Manufacturing Cost per Unit", "Total Mfg Costs / Units Produced", "✅ Supply Chain data"),
        ("Logistics Cost per Mile/Unit", "Fuel + Transport / Distance", "⚠️ Partial data"),
        ("Operating Expense Ratio", "Operating Expenses / Revenue", "⚠️ Can estimate")
    ],

    "WORKING CAPITAL METRICS": [
        ("Days Sales Outstanding (DSO)", "AR / (Revenue / 365)", "⚠️ Can estimate AR"),
        ("Days Inventory Outstanding (DIO)", "Inventory / (COGS / 365)", "✅ Inventory data available"),
        ("Cash Conversion Cycle", "DSO + DIO - DPO", "⚠️ Need to estimate DPO"),
        ("Inventory Turnover", "COGS / Average Inventory", "✅ Can calculate"),
        ("Working Capital Ratio", "Current Assets / Current Liabilities", "⚠️ Limited balance sheet data")
    ],

    "EFFICIENCY METRICS": [
        ("Revenue per Employee", "Revenue / Headcount", "❌ No employee data"),
        ("Order Fulfillment Cost", "Fulfillment Costs / Orders", "✅ Shipping data"),
        ("Perfect Order Rate", "Orders delivered on time / Total Orders", "✅ Delivery status available"),
        ("Cost to Serve", "Total Supply Chain Cost / Units Sold", "✅ Can calculate"),
        ("Asset Turnover", "Revenue / Total Assets", "❌ No asset data")
    ],

    "DISCOUNT & PRICING METRICS": [
        ("Average Discount %", "AVG(Discount Rate)", "✅ DataCo, Retail"),
        ("Discount Impact on Profit", "Lost Profit due to Discounts", "✅ Can calculate"),
        ("Price Realization", "Actual Price / List Price", "✅ Can derive"),
        ("Discount by Segment", "Discount % by Customer Type", "✅ Segment data available"),
        ("Promotional ROI", "(Sales Increase - Discount Cost) / Discount Cost", "✅ Can calculate")
    ],

    "CUSTOMER METRICS": [
        ("Customer Lifetime Value (CLV)", "Average order value × frequency × lifespan", "✅ Can estimate"),
        ("Average Order Value (AOV)", "Total Revenue / Number of Orders", "✅ Available"),
        ("Repeat Purchase Rate", "Customers with >1 order / Total Customers", "✅ Customer ID available"),
        ("Revenue per Customer", "Revenue / Unique Customers", "✅ Available"),
        ("Customer Acquisition Cost", "Marketing Spend / New Customers", "❌ No marketing data")
    ]
}

for category, metrics in kpi_categories.items():
    print(f"\n{category}")
    print("-" * 100)
    print(f"{'Metric':<35} {'Formula/Definition':<45} {'Data Availability':<20}")
    print("-" * 100)
    for metric_name, formula, availability in metrics:
        print(f"{metric_name:<35} {formula:<45} {availability:<20}")

# ============================================================================
# PART 6: USE CASES FOR FINANCE INSIGHT AGENT
# ============================================================================
print("\n\n" + "="*100)
print("PART 6: CONCRETE USE CASES FOR FINANCE INSIGHT AGENT")
print("="*100)

use_cases = {
    "USE CASE 1: Automated P&L Report Generation": {
        "description": "Generate weekly/monthly P&L statements automatically",
        "inputs": [
            "Date range selection",
            "Aggregation level (weekly/monthly/quarterly)"
        ],
        "process": [
            "1. Extract sales data for period",
            "2. Calculate COGS (from profit data)",
            "3. Calculate gross profit",
            "4. Sum operating expenses (shipping, discounts)",
            "5. Calculate net profit",
            "6. Generate formatted P&L statement"
        ],
        "outputs": [
            "P&L statement with revenue, costs, profit",
            "Period-over-period comparisons",
            "Variance analysis (actual vs prior period)",
            "Visualizations (charts, trend lines)"
        ],
        "sample_query": '"Generate a P&L report for Q1 2017"',
        "feasibility": "✅ HIGH - All data available"
    },

    "USE CASE 2: Expense Pattern Analysis & Anomaly Detection": {
        "description": "Identify unusual spending patterns and cost optimization opportunities",
        "inputs": [
            "Expense category (shipping, discounts, manufacturing)",
            "Time period",
            "Threshold for anomalies (e.g., >20% deviation)"
        ],
        "process": [
            "1. Group expenses by category and time",
            "2. Calculate baseline (mean, median)",
            "3. Detect outliers using statistical methods",
            "4. Analyze root causes (correlate with volume, region, etc.)",
            "5. Generate recommendations"
        ],
        "outputs": [
            "List of anomalous expense events",
            "Root cause analysis (e.g., 'Shipping costs spiked 35% in Dec due to Same Day deliveries')",
            "Cost-saving recommendations",
            "Trend visualizations"
        ],
        "sample_query": '"Show me unusual shipping costs in the last 6 months"',
        "feasibility": "✅ HIGH - Rich expense data"
    },

    "USE CASE 3: Discount Effectiveness Analysis": {
        "description": "Analyze which discounts drive sales vs erode margins",
        "inputs": [
            "Discount levels to analyze",
            "Product categories",
            "Time period"
        ],
        "process": [
            "1. Segment orders by discount level (0%, 1-10%, 11-20%, >20%)",
            "2. Calculate average order value by segment",
            "3. Calculate profit margin by segment",
            "4. Determine discount elasticity",
            "5. Identify optimal discount levels"
        ],
        "outputs": [
            "Discount ROI by level",
            "Products where discounts work vs don't work",
            "Recommended discount strategies",
            "Customer segments most responsive to discounts"
        ],
        "sample_query": '"Which discount levels maximize profit for Furniture category?"',
        "feasibility": "✅ EXCELLENT - Detailed discount data"
    },

    "USE CASE 4: Cashflow Forecasting (30/60/90 days)": {
        "description": "Predict cash inflows and outflows for next 3 months",
        "inputs": [
            "Historical sales data (12-36 months)",
            "Seasonality patterns",
            "Expected growth rate",
            "Known upcoming expenses"
        ],
        "process": [
            "1. Train time-series model on historical sales",
            "2. Generate revenue forecast",
            "3. Apply payment term assumptions (DSO)",
            "4. Forecast expenses based on historical ratios",
            "5. Calculate net cashflow by period",
            "6. Flag periods with negative cashflow"
        ],
        "outputs": [
            "30/60/90 day cashflow projections",
            "Expected cash balance by period",
            "Working capital requirements",
            "Risk alerts (potential cash shortfalls)",
            "Confidence intervals"
        ],
        "sample_query": '"What will our cashflow look like in the next 3 months?"',
        "feasibility": "✅ GOOD - Time-series data available, some assumptions needed"
    },

    "USE CASE 5: Profitability Analysis by Dimension": {
        "description": "Drill down into profit drivers across products, customers, regions",
        "inputs": [
            "Dimension to analyze (product, customer, region, segment)",
            "Time period",
            "Minimum order threshold"
        ],
        "process": [
            "1. Group profit data by selected dimension",
            "2. Calculate profit margin for each group",
            "3. Rank by profitability",
            "4. Identify top performers and loss-makers",
            "5. Analyze contributing factors"
        ],
        "outputs": [
            "Profit ranking by dimension",
            "Top 10 most/least profitable items",
            "Margin analysis",
            "Recommendations (e.g., 'Discontinue Product X', 'Focus on Region Y')"
        ],
        "sample_query": '"Which customer segments are most profitable?"',
        "feasibility": "✅ EXCELLENT - Rich dimensional data"
    },

    "USE CASE 6: Budget vs Actual Variance Analysis": {
        "description": "Compare actual financial performance against budget/forecast",
        "inputs": [
            "Budget/forecast data (could be generated from historical trends)",
            "Actual data for period",
            "Variance threshold for flagging"
        ],
        "process": [
            "1. Load budget and actual data",
            "2. Calculate variance ($ and %)",
            "3. Flag significant variances (e.g., >10%)",
            "4. Analyze root causes",
            "5. Generate commentary"
        ],
        "outputs": [
            "Variance report (budget vs actual)",
            "Favorable/unfavorable variance highlights",
            "Root cause analysis",
            "Recommendations for corrective action"
        ],
        "sample_query": '"How are we performing vs our revenue budget this quarter?"',
        "feasibility": "✅ GOOD - Need to create budget baseline, actual data available"
    },

    "USE CASE 7: Working Capital Optimization": {
        "description": "Identify opportunities to free up cash tied in operations",
        "inputs": [
            "Inventory levels",
            "Sales velocity",
            "Lead times",
            "Payment terms"
        ],
        "process": [
            "1. Calculate current DSO, DIO, DPO",
            "2. Identify slow-moving inventory",
            "3. Analyze payment term opportunities",
            "4. Simulate impact of changes",
            "5. Recommend specific actions"
        ],
        "outputs": [
            "Current cash conversion cycle metrics",
            "Excess inventory list",
            "Recommendations (e.g., 'Reduce inventory of Product X by 30%')",
            "Estimated cash release from changes"
        ],
        "sample_query": '"How can we reduce cash tied up in inventory?"',
        "feasibility": "✅ GOOD - Inventory and timing data available"
    },

    "USE CASE 8: Financial Impact of Supply Chain Risks": {
        "description": "Quantify financial impact of late deliveries, stockouts, etc.",
        "inputs": [
            "Late delivery data",
            "Stockout incidents",
            "Average order values",
            "Customer churn rates (if available)"
        ],
        "process": [
            "1. Identify supply chain failures (late deliveries)",
            "2. Link to financial impact (lost sales, penalties)",
            "3. Calculate total cost of failures",
            "4. Prioritize high-impact issues",
            "5. Estimate ROI of improvements"
        ],
        "outputs": [
            "Total financial impact of supply chain issues",
            "Cost per late delivery",
            "Revenue at risk from stockouts",
            "ROI of investing in reliability improvements"
        ],
        "sample_query": '"What do late deliveries cost us financially?"',
        "feasibility": "✅ EXCELLENT - Late delivery risk data available"
    }
}

for use_case_name, details in use_cases.items():
    print(f"\n{use_case_name}")
    print("="*100)
    print(f"\nDescription: {details['description']}")
    print(f"\nInputs:")
    for inp in details['inputs']:
        print(f"  • {inp}")
    print(f"\nProcess:")
    for step in details['process']:
        print(f"  {step}")
    print(f"\nOutputs:")
    for output in details['outputs']:
        print(f"  • {output}")
    print(f"\nSample User Query: {details['sample_query']}")
    print(f"\nFeasibility: {details['feasibility']}")

# ============================================================================
# SUMMARY MATRIX
# ============================================================================
print("\n\n" + "="*100)
print("SUMMARY: FINANCE INSIGHT AGENT CAPABILITY MATRIX")
print("="*100)

summary = """
╔═══════════════════════════════════════════╦═══════════════╦════════════════════════════════════════╗
║ CAPABILITY                                ║ STATUS        ║ DATA SOURCES                           ║
╠═══════════════════════════════════════════╬═══════════════╬════════════════════════════════════════╣
║ 1. AUTOMATIC P&L SUMMARIZATION            ║               ║                                        ║
║    • Revenue Reporting                    ║ ✅ EXCELLENT  ║ DataCo, Retail (180K+ transactions)    ║
║    • COGS Calculation                     ║ ✅ GOOD       ║ Derived from Sales - Profit            ║
║    • Gross Profit                         ║ ✅ EXCELLENT  ║ Direct profit columns available        ║
║    • Operating Expenses                   ║ ⚠️  PARTIAL   ║ Shipping costs, need estimation        ║
║    • Net Profit                           ║ ✅ GOOD       ║ Calculable with assumptions            ║
║    • Period Comparisons                   ║ ✅ EXCELLENT  ║ 3+ years time-series data              ║
╠═══════════════════════════════════════════╬═══════════════╬════════════════════════════════════════╣
║ 2. EXPENSE PATTERN ANALYSIS               ║               ║                                        ║
║    • Shipping/Logistics Costs             ║ ✅ EXCELLENT  ║ Shipping mode, costs, transportation   ║
║    • Discount Analysis                    ║ ✅ EXCELLENT  ║ Discount amounts and rates             ║
║    • Manufacturing Costs                  ║ ✅ GOOD       ║ Supply Chain dataset                   ║
║    • Inventory Costs                      ║ ✅ GOOD       ║ Stock levels, warehouse data           ║
║    • Anomaly Detection                    ║ ✅ EXCELLENT  ║ Rich historical data for baselines     ║
║    • Cost Optimization                    ║ ✅ EXCELLENT  ║ Multiple cost dimensions available     ║
╠═══════════════════════════════════════════╬═══════════════╬════════════════════════════════════════╣
║ 3. CASHFLOW FORECASTING                   ║               ║                                        ║
║    • Revenue Forecasting                  ║ ✅ EXCELLENT  ║ Daily transactions, 3+ years           ║
║    • Time-Series Models                   ║ ✅ EXCELLENT  ║ Sufficient historical data             ║
║    • Cash Inflow Timing                   ║ ⚠️  GOOD      ║ Payment types, need DSO assumptions    ║
║    • Cash Outflow Timing                  ║ ⚠️  GOOD      ║ Cost data, need DPO assumptions        ║
║    • Working Capital Forecast             ║ ✅ GOOD       ║ Inventory, sales velocity data         ║
║    • Scenario Modeling                    ║ ✅ EXCELLENT  ║ Rich feature set for what-if           ║
╠═══════════════════════════════════════════╬═══════════════╬════════════════════════════════════════╣
║ 4. FINANCIAL KPIs & METRICS               ║               ║                                        ║
║    • Profitability Metrics                ║ ✅ EXCELLENT  ║ All margin calculations possible       ║
║    • Revenue Metrics                      ║ ✅ EXCELLENT  ║ Comprehensive revenue data             ║
║    • Cost Metrics                         ║ ✅ GOOD       ║ Multiple cost categories               ║
║    • Working Capital Metrics              ║ ⚠️  GOOD      ║ Some balance sheet items missing       ║
║    • Efficiency Metrics                   ║ ✅ GOOD       ║ Delivery, cost per order data          ║
║    • Customer Metrics                     ║ ✅ EXCELLENT  ║ Customer-level transaction data        ║
╠═══════════════════════════════════════════╬═══════════════╬════════════════════════════════════════╣
║ 5. ADVANCED ANALYTICS                     ║               ║                                        ║
║    • Profitability by Dimension           ║ ✅ EXCELLENT  ║ Product, Customer, Region data         ║
║    • Discount Effectiveness               ║ ✅ EXCELLENT  ║ Detailed discount tracking             ║
║    • Trend Analysis                       ║ ✅ EXCELLENT  ║ Multi-year time-series                 ║
║    • Variance Analysis                    ║ ✅ EXCELLENT  ║ Rich comparison data                   ║
║    • Risk Impact Quantification           ║ ✅ EXCELLENT  ║ Late delivery, stockout data           ║
╚═══════════════════════════════════════════╩═══════════════╩════════════════════════════════════════╝

LEGEND:
✅ EXCELLENT : All required data available, high-quality implementation possible
✅ GOOD      : Core data available, some assumptions or estimates needed
⚠️  PARTIAL  : Limited data, significant estimation required
❌ LIMITED   : Insufficient data, major limitations
"""

print(summary)

# ============================================================================
# FINAL RECOMMENDATIONS
# ============================================================================
print("\n" + "="*100)
print("RECOMMENDATIONS FOR BUILDING FINANCE INSIGHT AGENT")
print("="*100)

recommendations = """
1. START WITH HIGH-CONFIDENCE FEATURES:
   ✅ Automated P&L reports (weekly/monthly)
   ✅ Discount effectiveness analysis
   ✅ Profitability analysis by product/customer/region
   ✅ Revenue forecasting using time-series models
   ✅ Expense anomaly detection

2. FEATURES REQUIRING SOME ASSUMPTIONS:
   ⚠️  Operating expense categorization (estimate from shipping + discounts)
   ⚠️  Cashflow timing (assume standard payment terms: DSO=30 days, DPO=45 days)
   ⚠️  COGS allocation (derive from Sales - Profit where not available)

3. DATA ENRICHMENT OPPORTUNITIES:
   • If possible, obtain:
     - Accounts Receivable aging data (improve cashflow forecasting)
     - Accounts Payable data (complete cash conversion cycle)
     - Operating expense breakdown (improve P&L accuracy)
     - Employee headcount (enable productivity metrics)

4. RECOMMENDED TECH STACK:
   • LLM: GPT-4 or Claude for natural language queries
   • Forecasting: Prophet (Facebook) or ARIMA for time-series
   • ML Models: XGBoost/LightGBM for regression-based forecasting
   • Visualization: Plotly for interactive charts
   • Database: PostgreSQL + TimescaleDB for time-series optimization

5. PHASED IMPLEMENTATION:
   Phase 1: Core P&L reporting + basic KPIs (4-6 weeks)
   Phase 2: Expense analysis + anomaly detection (4 weeks)
   Phase 3: Cashflow forecasting models (6-8 weeks)
   Phase 4: Advanced analytics + what-if scenarios (6 weeks)

6. KEY CHALLENGES TO ADDRESS:
   • Data quality: Handle missing values, outliers
   • Assumption transparency: Clearly document all estimation methods
   • Forecast accuracy: Establish confidence intervals and track prediction accuracy
   • User trust: Provide explainable AI - show how calculations are done

7. SUCCESS METRICS FOR FINANCE AGENT:
   • Forecast Accuracy: MAPE (Mean Absolute Percentage Error) < 10% for revenue
   • User Adoption: 80% of finance queries handled by agent
   • Time Savings: Reduce report generation time by 90%
   • Insight Quality: Generate 3+ actionable recommendations per report
   • Alert Accuracy: <5% false positive rate on expense anomalies
"""

print(recommendations)

print("\n" + "="*100)
print("✅ ANALYSIS COMPLETE")
print("="*100)
print("\nThis comprehensive analysis provides all the information needed to build")
print("a robust Finance Insight Agent with P&L, expense analysis, and cashflow capabilities.")
print("\nNext Steps:")
print("  1. Review this analysis with stakeholders")
print("  2. Prioritize features based on business value")
print("  3. Begin with Phase 1 implementation (core P&L)")
print("  4. Iterate based on user feedback")
print("\n" + "="*100)
