"""
SQLAlchemy ORM models for OmniSupply platform.
These models map to database tables for persistent storage.
"""

from datetime import datetime
from decimal import Decimal
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Text, Index, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

Base = declarative_base()


class OrderDB(Base):
    """Order table"""
    __tablename__ = 'orders'

    id = Column(Integer, primary_key=True)
    order_id = Column(String(100), unique=True, nullable=False, index=True)
    order_date = Column(DateTime, nullable=False, index=True)
    ship_mode = Column(String(50))
    segment = Column(String(50), index=True)
    country = Column(String(100))
    city = Column(String(100))
    state = Column(String(100))
    postal_code = Column(String(20))
    region = Column(String(50), index=True)
    category = Column(String(100), index=True)
    sub_category = Column(String(100))
    product_id = Column(String(100), index=True)
    cost_price = Column(Numeric(12, 2))
    list_price = Column(Numeric(12, 2))
    quantity = Column(Integer)
    discount_percent = Column(Numeric(5, 2))
    discount = Column(Numeric(12, 2))
    sale_price = Column(Numeric(12, 2))
    profit = Column(Numeric(12, 2))
    is_returned = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_order_date_category', 'order_date', 'category'),
        Index('idx_product_category', 'product_id', 'category'),
    )


class ShipmentDB(Base):
    """Shipment table"""
    __tablename__ = 'shipments'

    id = Column(Integer, primary_key=True)
    shipment_id = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(String(100), index=True)
    origin_port = Column(String(100))
    destination_port = Column(String(100))
    carrier = Column(String(100), index=True)
    shipment_date = Column(DateTime, nullable=False, index=True)
    expected_delivery = Column(DateTime, nullable=False)
    actual_delivery = Column(DateTime, nullable=True)
    quantity = Column(Integer)
    weight_kg = Column(Numeric(12, 2))
    freight_cost = Column(Numeric(12, 2))
    insurance_cost = Column(Numeric(12, 2))
    customs_cost = Column(Numeric(12, 2))
    status = Column(String(50), index=True)
    delay_reason = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_shipment_status_date', 'status', 'shipment_date'),
        Index('idx_carrier_status', 'carrier', 'status'),
    )


class InventoryDB(Base):
    """Inventory table"""
    __tablename__ = 'inventory'

    id = Column(Integer, primary_key=True)
    sku = Column(String(100), unique=True, nullable=False, index=True)
    product_id = Column(String(100), index=True)
    product_name = Column(String(255))
    category = Column(String(100), index=True)
    warehouse_location = Column(String(100), index=True)
    stock_quantity = Column(Integer, nullable=False)
    reorder_level = Column(Integer)
    reorder_quantity = Column(Integer)
    unit_cost = Column(Numeric(12, 2))
    last_restock_date = Column(DateTime)
    lead_time_days = Column(Integer)
    supplier_id = Column(String(100), index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_stock_quantity', 'stock_quantity'),
        Index('idx_category_warehouse', 'category', 'warehouse_location'),
    )


class FinancialTransactionDB(Base):
    """Financial transaction table"""
    __tablename__ = 'financial_transactions'

    id = Column(Integer, primary_key=True)
    transaction_id = Column(String(100), unique=True, nullable=False, index=True)
    transaction_date = Column(DateTime, nullable=False, index=True)
    transaction_type = Column(String(50), nullable=False, index=True)
    category = Column(String(100), index=True)
    subcategory = Column(String(100))
    amount = Column(Numeric(15, 2), nullable=False)
    currency = Column(String(10), default='USD')
    cost_center = Column(String(100))
    business_unit = Column(String(100))
    payment_method = Column(String(50))
    vendor_id = Column(String(100), index=True)
    notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        Index('idx_date_type', 'transaction_date', 'transaction_type'),
        Index('idx_type_category', 'transaction_type', 'category'),
    )


class AgentExecutionLog(Base):
    """Track agent executions for observability"""
    __tablename__ = 'agent_executions'

    id = Column(Integer, primary_key=True)
    session_id = Column(String(100), index=True)
    agent_name = Column(String(100), nullable=False, index=True)
    query = Column(Text, nullable=False)
    execution_start = Column(DateTime, default=datetime.utcnow, index=True)
    execution_end = Column(DateTime)
    duration_ms = Column(Integer)
    success = Column(Integer, default=1)  # 1=success, 0=failure
    error_message = Column(Text, nullable=True)
    tokens_used = Column(Integer)
    cost_usd = Column(Numeric(10, 4))
    result_summary = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_agent_date', 'agent_name', 'execution_start'),
        Index('idx_session', 'session_id'),
    )


class ReportArchive(Base):
    """Store generated reports for retrieval"""
    __tablename__ = 'report_archive'

    id = Column(Integer, primary_key=True)
    report_id = Column(String(100), unique=True, nullable=False, index=True)
    report_type = Column(String(50), nullable=False, index=True)
    generated_at = Column(DateTime, default=datetime.utcnow, index=True)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    agents_used = Column(Text)  # JSON array of agent names
    report_content = Column(Text)  # Markdown or HTML
    insights_count = Column(Integer)
    recommendations_count = Column(Integer)
    kpis_json = Column(Text)  # JSON of key metrics
    created_by = Column(String(100))  # User or 'system'
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_type_date', 'report_type', 'generated_at'),
    )


class AlertLog(Base):
    """Track alerts sent to stakeholders"""
    __tablename__ = 'alert_log'

    id = Column(Integer, primary_key=True)
    alert_id = Column(String(100), unique=True, nullable=False, index=True)
    alert_type = Column(String(50), nullable=False, index=True)
    severity = Column(String(20), nullable=False, index=True)  # INFO, WARNING, CRITICAL
    title = Column(String(255))
    description = Column(Text)
    affected_entities = Column(Text)  # JSON array
    stakeholders = Column(Text)  # JSON array of emails
    sent_at = Column(DateTime, default=datetime.utcnow, index=True)
    acknowledged_at = Column(DateTime, nullable=True)
    acknowledged_by = Column(String(100))
    resolution_notes = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)

    __table_args__ = (
        Index('idx_severity_sent', 'severity', 'sent_at'),
        Index('idx_type_severity', 'alert_type', 'severity'),
    )
