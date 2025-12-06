# OmniSupply Database Schema Reference

**Database**: PostgreSQL 15
**Schema**: `omnisupply`

This document provides the **authoritative reference** for all database tables and columns. All agents must use this schema information to generate accurate SQL queries.

---

## 📋 Complete Table Schemas

### 1. `orders` Table

**Purpose**: Customer orders with product, pricing, and delivery information

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key (auto-increment) | ✓ PK |
| `order_id` | VARCHAR(100) | Unique order identifier | ✓ UNIQUE |
| `order_date` | DATETIME | Order placement date | ✓ |
| `customer_id` | VARCHAR(100) | Customer identifier | ✓ |
| `product_id` | VARCHAR(100) | Product SKU | ✓ |
| `category` | VARCHAR(100) | Product category | ✓ |
| `sub_category` | VARCHAR(100) | Product subcategory | |
| `sale_price` | NUMERIC(12,2) | Unit sale price | |
| `profit` | NUMERIC(12,2) | Profit per unit | |
| `quantity` | INTEGER | Order quantity | |
| `discount_percent` | NUMERIC(5,2) | Discount percentage (0-100) | |
| `revenue` | NUMERIC(15,2) | Total revenue (calculated) | |
| `is_returned` | **BOOLEAN** | Return status | ✓ |
| `shipping_mode` | VARCHAR(50) | Shipping method | |
| `segment` | VARCHAR(50) | Customer segment | ✓ |
| `region` | VARCHAR(100) | Geographic region | ✓ |
| `state` | VARCHAR(100) | State/province | |
| `city` | VARCHAR(100) | City | |
| `postal_code` | VARCHAR(20) | Postal code | |
| `expected_delivery` | DATETIME | Expected delivery date | |
| `actual_delivery` | DATETIME | Actual delivery date | |
| `created_at` | DATETIME | Record creation timestamp | |
| `updated_at` | DATETIME | Last update timestamp | |

**Indexes**:
- Primary: `id`
- Unique: `order_id`
- Single: `order_date`, `customer_id`, `product_id`, `category`, `is_returned`, `segment`, `region`
- Composite: `(order_date, category)`, `(region, category)`

---

### 2. `shipments` Table

**Purpose**: Shipment tracking and delivery information

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key (auto-increment) | ✓ PK |
| `shipment_id` | VARCHAR(100) | Unique shipment identifier | ✓ UNIQUE |
| `order_id` | VARCHAR(100) | Related order ID | ✓ |
| `carrier` | VARCHAR(100) | Shipping carrier name | ✓ |
| `shipment_date` | DATETIME | Shipment dispatch date | ✓ |
| `expected_delivery` | DATETIME | Expected delivery date | |
| `actual_delivery` | DATETIME | Actual delivery date | |
| `status` | VARCHAR(50) | Current shipment status | ✓ |
| `origin_location` | VARCHAR(200) | Origin address | |
| `destination_location` | VARCHAR(200) | Destination address | |
| `freight_cost` | NUMERIC(10,2) | Shipping cost | |
| `insurance_cost` | NUMERIC(10,2) | Insurance cost | |
| `is_late` | BOOLEAN | Late delivery flag | |
| `late_reason` | TEXT | Reason for delay | |
| `created_at` | DATETIME | Record creation timestamp | |
| `updated_at` | DATETIME | Last update timestamp | |

**Indexes**:
- Primary: `id`
- Unique: `shipment_id`
- Single: `order_id`, `carrier`, `shipment_date`, `status`
- Composite: `(shipment_date, status)`, `(carrier, status)`

---

### 3. `inventory` Table

**Purpose**: Product inventory and warehouse management

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key (auto-increment) | ✓ PK |
| `sku` | VARCHAR(100) | Stock keeping unit (unique) | ✓ UNIQUE |
| `product_id` | VARCHAR(100) | Product identifier | ✓ |
| `product_name` | VARCHAR(200) | Product name | |
| `category` | VARCHAR(100) | Product category | ✓ |
| `stock_quantity` | INTEGER | Current stock level | ✓ |
| `reorder_level` | INTEGER | Reorder threshold | |
| `reorder_quantity` | INTEGER | Quantity to reorder | |
| `unit_cost` | NUMERIC(12,2) | Cost per unit | |
| `last_restock_date` | DATETIME | Last restock date | |
| `lead_time_days` | INTEGER | Supplier lead time (days) | |
| `supplier_id` | VARCHAR(100) | Supplier identifier | ✓ |
| `warehouse_location` | VARCHAR(200) | Storage location | |
| `created_at` | DATETIME | Record creation timestamp | |
| `updated_at` | DATETIME | Last update timestamp | |

**Indexes**:
- Primary: `id`
- Unique: `sku`
- Single: `product_id`, `category`, `stock_quantity`, `supplier_id`
- Composite: `(category, warehouse_location)`

---

### 4. `financial_transactions` Table

**Purpose**: Financial transactions including revenue, expenses, and COGS

| Column | Type | Description | Indexed |
|--------|------|-------------|---------|
| `id` | INTEGER | Primary key (auto-increment) | ✓ PK |
| `transaction_id` | VARCHAR(100) | Unique transaction identifier | ✓ UNIQUE |
| `transaction_date` | DATETIME | Transaction date | ✓ |
| `transaction_type` | VARCHAR(50) | Type (Revenue, COGS, Operating Expense, etc.) | ✓ |
| `category` | VARCHAR(100) | Transaction category | ✓ |
| `subcategory` | VARCHAR(100) | Transaction subcategory | |
| `amount` | NUMERIC(15,2) | Transaction amount | |
| `currency` | VARCHAR(10) | Currency code (default: USD) | |
| `cost_center` | VARCHAR(100) | Cost center | |
| `business_unit` | VARCHAR(100) | Business unit | |
| `payment_method` | VARCHAR(50) | Payment method (**NOT payment_status**) | |
| `vendor_id` | VARCHAR(100) | Vendor/supplier identifier | ✓ |
| `notes` | TEXT | Additional notes | |
| `created_at` | DATETIME | Record creation timestamp | |
| `updated_at` | DATETIME | Last update timestamp | |

**Indexes**:
- Primary: `id`
- Unique: `transaction_id`
- Single: `transaction_date`, `transaction_type`, `category`, `vendor_id`
- Composite: `(transaction_date, transaction_type)`, `(transaction_type, category)`

**⚠️ IMPORTANT**: This table has `payment_method`, NOT `payment_status`!

---

## 🔍 Common Query Patterns

### Orders Analysis
```sql
-- Revenue by category
SELECT category, SUM(sale_price * quantity) as total_revenue
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category
ORDER BY total_revenue DESC;

-- Return rate analysis
SELECT
    category,
    COUNT(*) as total_orders,
    SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) as returned_orders,
    CAST(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as return_rate
FROM orders
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY category
HAVING CAST(SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) > 0;
```

### Financial Analysis
```sql
-- P&L summary
SELECT
    transaction_type,
    SUM(amount) as total_amount,
    COUNT(*) as transaction_count
FROM financial_transactions
WHERE transaction_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY transaction_type
ORDER BY total_amount DESC;

-- By payment method (NOT payment_status!)
SELECT
    payment_method,
    COUNT(*) as count,
    SUM(amount) as total
FROM financial_transactions
WHERE payment_method IS NOT NULL
GROUP BY payment_method;
```

### Inventory Status
```sql
-- Low stock items
SELECT sku, product_name, stock_quantity, reorder_level
FROM inventory
WHERE stock_quantity <= reorder_level
ORDER BY stock_quantity ASC;
```

### Shipment Performance
```sql
-- Late delivery analysis
SELECT
    carrier,
    COUNT(*) as total_shipments,
    SUM(CASE WHEN is_late THEN 1 ELSE 0 END) as late_shipments,
    CAST(SUM(CASE WHEN is_late THEN 1 ELSE 0 END) AS FLOAT) / COUNT(*) as late_rate
FROM shipments
WHERE shipment_date >= CURRENT_DATE - INTERVAL '30 days'
GROUP BY carrier;
```

---

## 📐 PostgreSQL Date Functions

Use these PostgreSQL-specific date functions:

```sql
-- Current time
CURRENT_DATE          -- Today's date
NOW()                 -- Current timestamp

-- Date arithmetic
CURRENT_DATE - INTERVAL '30 days'
order_date + INTERVAL '7 days'

-- Date formatting
TO_CHAR(order_date, 'YYYY-MM')           -- 2024-03
TO_CHAR(order_date, 'YYYY-MM-DD')        -- 2024-03-15

-- Date truncation
DATE_TRUNC('month', order_date)          -- First day of month
DATE_TRUNC('week', order_date)           -- First day of week

-- Date difference (in days)
EXTRACT(EPOCH FROM (actual_delivery - expected_delivery))/86400
```

---

## ⚠️ Common Mistakes to Avoid

### 1. ❌ Using non-existent columns
```sql
-- WRONG: payment_status doesn't exist
SELECT * FROM financial_transactions WHERE payment_status = 'completed';

-- RIGHT: Use payment_method
SELECT * FROM financial_transactions WHERE payment_method = 'Credit Card';
```

### 2. ❌ Direct SUM on boolean columns
```sql
-- WRONG: PostgreSQL doesn't support this
SELECT SUM(is_returned) FROM orders;

-- RIGHT: Use CASE WHEN
SELECT SUM(CASE WHEN is_returned THEN 1 ELSE 0 END) as returns FROM orders;
```

### 3. ❌ Using DuckDB-specific syntax
```sql
-- WRONG: interval syntax for DuckDB
WHERE order_date >= current_date - interval 30 day

-- RIGHT: PostgreSQL interval syntax
WHERE order_date >= CURRENT_DATE - INTERVAL '30 days'
```

---

## 🔄 Schema Maintenance

### Updating This Document

When the database schema changes:

1. Update the table definitions in [src/storage/sql/models.py](src/storage/sql/models.py)
2. Update this document (DATABASE_SCHEMA.md)
3. Update agent prompts in:
   - [src/agents/data_analyst.py](src/agents/data_analyst.py) (lines 181-185, 233-237)
   - [src/agents/finance_agent.py](src/agents/finance_agent.py) (any schema references)
   - [src/agents/risk_agent.py](src/agents/risk_agent.py) (any schema references)

### Verifying Schema Accuracy

```sql
-- Check actual columns in database
SELECT column_name, data_type
FROM information_schema.columns
WHERE table_schema = 'omnisupply'
  AND table_name = 'financial_transactions'
ORDER BY ordinal_position;
```

---

## 📊 Database Statistics

**Current record counts** (as of Dec 6, 2025):
- `orders`: 65,752 records
- `financial_transactions`: 351,010 records
- `shipments`: 100 records
- `inventory`: 100 records

**Total**: 416,962 records

---

**Last Updated**: December 6, 2025
**Schema Version**: 1.0
**Database**: PostgreSQL 15 (localhost:5432/omnisupply)
