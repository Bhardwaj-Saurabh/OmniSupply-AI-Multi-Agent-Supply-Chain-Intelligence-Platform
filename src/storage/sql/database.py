"""
Database connection and operations for OmniSupply platform.
Supports both DuckDB (for local/analytics) and PostgreSQL (for production).
"""

import os
from typing import List, Optional, Dict, Any
from contextlib import contextmanager
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import logging

from .models import Base, OrderDB, ShipmentDB, InventoryDB, FinancialTransactionDB
from ...data.models import Order, Shipment, InventoryItem, FinancialTransaction

logger = logging.getLogger(__name__)


class DatabaseClient:
    """Database client for OmniSupply"""

    def __init__(self, database_url: Optional[str] = None, echo: bool = False):
        """
        Initialize database connection.

        Args:
            database_url: Database connection string
                - DuckDB: "duckdb:///omnisupply.db" (local file)
                - PostgreSQL: "postgresql://user:pass@host:5432/dbname"
                - SQLite: "sqlite:///omnisupply.db"
            echo: Whether to log SQL statements
        """
        if database_url is None:
            # Default to DuckDB for analytics workloads
            database_url = os.getenv("DATABASE_URL", "duckdb:///data/omnisupply.db")

        logger.info(f"Initializing database: {database_url.split('://')[0]}")

        # Create engine
        if database_url.startswith("duckdb"):
            # DuckDB-specific settings
            self.engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"read_only": False}
            )
        elif database_url.startswith("sqlite"):
            # SQLite for testing
            self.engine = create_engine(
                database_url,
                echo=echo,
                connect_args={"check_same_thread": False},
                poolclass=StaticPool
            )
        else:
            # PostgreSQL or other
            connect_args = {}
            self.schema_name = None

            # For PostgreSQL, extract username and setup custom schema
            if database_url.startswith("postgresql"):
                # Extract username from connection string for schema authorization
                import re
                match = re.search(r'postgresql://([^:]+):', database_url)
                if match:
                    self.pg_username = match.group(1)
                    self.schema_name = "omnisupply"  # Our custom schema
                    # Set search_path to use our schema
                    connect_args["options"] = f"-c search_path={self.schema_name},public"
                    logger.info(f"PostgreSQL: Will use schema '{self.schema_name}' with user '{self.pg_username}'")
                else:
                    self.pg_username = None
                    logger.warning("Could not extract username from PostgreSQL URL")

            self.engine = create_engine(
                database_url,
                echo=echo,
                pool_pre_ping=True,
                pool_size=10,
                max_overflow=20,
                connect_args=connect_args
            )

        # Create session factory
        self.SessionLocal = sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=self.engine
        )

        # Initialize database schema for PostgreSQL
        if database_url.startswith("postgresql") and self.schema_name:
            self.init_postgres_schema()

        # Create tables
        self.create_tables()

    def init_postgres_schema(self):
        """Initialize PostgreSQL schema - create custom schema with proper authorization"""
        try:
            import psycopg2
            from psycopg2 import sql

            # Get connection parameters from engine URL
            url = self.engine.url

            # Connect using psycopg2 directly for schema creation
            conn = psycopg2.connect(
                host=url.host,
                port=url.port,
                database=url.database,
                user=url.username,
                password=url.password
            )
            cursor = conn.cursor()

            # Create schema with proper authorization (matching your working example)
            cursor.execute(
                sql.SQL("CREATE SCHEMA IF NOT EXISTS {} AUTHORIZATION {}").format(
                    sql.Identifier(self.schema_name),
                    sql.Identifier(self.pg_username)
                )
            )
            conn.commit()
            logger.info(f"✅ Created/confirmed schema '{self.schema_name}' with authorization '{self.pg_username}'")

            # Set search_path for this connection
            cursor.execute(
                sql.SQL("SET search_path TO {}, public").format(
                    sql.Identifier(self.schema_name)
                )
            )
            conn.commit()

            cursor.close()
            conn.close()

            # Now configure SQLAlchemy to use this schema
            Base.metadata.schema = self.schema_name
            logger.info(f"✅ Configured SQLAlchemy to use schema '{self.schema_name}'")

        except Exception as e:
            logger.error(f"❌ Failed to initialize PostgreSQL schema: {e}")
            raise

    def create_tables(self):
        """Create all tables"""
        logger.info("Creating database tables...")
        Base.metadata.create_all(bind=self.engine)
        logger.info("Tables created successfully")

    def drop_tables(self):
        """Drop all tables (use with caution!)"""
        logger.warning("Dropping all tables...")
        Base.metadata.drop_all(bind=self.engine)

    @contextmanager
    def get_session(self) -> Session:
        """Get database session context manager"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database session error: {e}")
            raise
        finally:
            session.close()

    # Bulk insert operations

    def insert_orders(self, orders: List[Order]) -> int:
        """Bulk insert orders"""
        logger.info(f"Inserting {len(orders)} orders...")

        with self.get_session() as session:
            db_orders = [
                OrderDB(
                    order_id=o.order_id,
                    order_date=o.order_date,
                    ship_mode=o.ship_mode,
                    segment=o.segment,
                    country=o.country,
                    city=o.city,
                    state=o.state,
                    postal_code=o.postal_code,
                    region=o.region,
                    category=o.category,
                    sub_category=o.sub_category,
                    product_id=o.product_id,
                    cost_price=o.cost_price,
                    list_price=o.list_price,
                    quantity=o.quantity,
                    discount_percent=o.discount_percent,
                    discount=o.discount,
                    sale_price=o.sale_price,
                    profit=o.profit,
                    is_returned=o.is_returned
                )
                for o in orders
            ]

            session.bulk_save_objects(db_orders)

        logger.info(f"✅ Inserted {len(orders)} orders")
        return len(orders)

    def insert_shipments(self, shipments: List[Shipment]) -> int:
        """Bulk insert shipments"""
        logger.info(f"Inserting {len(shipments)} shipments...")

        with self.get_session() as session:
            db_shipments = [
                ShipmentDB(
                    shipment_id=s.shipment_id,
                    product_id=s.product_id,
                    origin_port=s.origin_port,
                    destination_port=s.destination_port,
                    carrier=s.carrier,
                    shipment_date=s.shipment_date,
                    expected_delivery=s.expected_delivery,
                    actual_delivery=s.actual_delivery,
                    quantity=s.quantity,
                    weight_kg=s.weight_kg,
                    freight_cost=s.freight_cost,
                    insurance_cost=s.insurance_cost,
                    customs_cost=s.customs_cost,
                    status=s.status,
                    delay_reason=s.delay_reason
                )
                for s in shipments
            ]

            session.bulk_save_objects(db_shipments)

        logger.info(f"✅ Inserted {len(shipments)} shipments")
        return len(shipments)

    def insert_inventory(self, inventory: List[InventoryItem]) -> int:
        """Bulk insert inventory"""
        logger.info(f"Inserting {len(inventory)} inventory items...")

        with self.get_session() as session:
            db_inventory = [
                InventoryDB(
                    sku=i.sku,
                    product_id=i.product_id,
                    product_name=i.product_name,
                    category=i.category,
                    warehouse_location=i.warehouse_location,
                    stock_quantity=i.stock_quantity,
                    reorder_level=i.reorder_level,
                    reorder_quantity=i.reorder_quantity,
                    unit_cost=i.unit_cost,
                    last_restock_date=i.last_restock_date,
                    lead_time_days=i.lead_time_days,
                    supplier_id=i.supplier_id
                )
                for i in inventory
            ]

            session.bulk_save_objects(db_inventory)

        logger.info(f"✅ Inserted {len(inventory)} inventory items")
        return len(inventory)

    def insert_transactions(self, transactions: List[FinancialTransaction]) -> int:
        """Bulk insert financial transactions"""
        logger.info(f"Inserting {len(transactions)} transactions...")

        with self.get_session() as session:
            db_transactions = [
                FinancialTransactionDB(
                    transaction_id=t.transaction_id,
                    transaction_date=t.transaction_date,
                    transaction_type=t.transaction_type,
                    category=t.category,
                    subcategory=t.subcategory,
                    amount=t.amount,
                    currency=t.currency,
                    cost_center=t.cost_center,
                    business_unit=t.business_unit,
                    payment_method=t.payment_method,
                    vendor_id=t.vendor_id,
                    notes=t.notes
                )
                for t in transactions
            ]

            session.bulk_save_objects(db_transactions)

        logger.info(f"✅ Inserted {len(transactions)} transactions")
        return len(transactions)

    def load_all_data(self, data: Dict[str, List[Any]], clear_existing: bool = False) -> Dict[str, int]:
        """
        Load all data from loaders.

        Args:
            data: Dictionary with data to load
            clear_existing: If True, clear all existing data before loading
        """
        counts = {}

        # Clear existing data if requested
        if clear_existing:
            logger.info("Clearing existing data before loading...")
            self.clear_all_data()

        # Use upsert for orders to handle duplicates
        if 'orders' in data:
            counts['orders'] = self.upsert_orders(data['orders'])

        # For other tables, use regular insert (they typically don't have duplicates)
        if 'shipments' in data:
            counts['shipments'] = self.insert_shipments(data['shipments'])

        if 'inventory' in data:
            counts['inventory'] = self.insert_inventory(data['inventory'])

        if 'transactions' in data:
            counts['transactions'] = self.insert_transactions(data['transactions'])

        return counts

    # Query operations

    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Execute raw SQL query"""
        with self.get_session() as session:
            result = session.execute(text(query), params or {})
            return [dict(row._mapping) for row in result]

    def get_table_counts(self) -> Dict[str, int]:
        """Get row counts for all tables"""
        with self.get_session() as session:
            return {
                'orders': session.query(OrderDB).count(),
                'shipments': session.query(ShipmentDB).count(),
                'inventory': session.query(InventoryDB).count(),
                'transactions': session.query(FinancialTransactionDB).count()
            }

    def clear_all_data(self):
        """Clear all data (keep schema)"""
        logger.warning("Clearing all data from database...")
        with self.get_session() as session:
            # Delete in reverse order to respect foreign keys
            session.query(FinancialTransactionDB).delete()
            session.query(InventoryDB).delete()
            session.query(ShipmentDB).delete()
            session.query(OrderDB).delete()
        logger.info("✅ All data cleared")

    def has_data(self) -> bool:
        """Check if database has any data"""
        counts = self.get_table_counts()
        return any(count > 0 for count in counts.values())

    def upsert_orders(self, orders: List[Order]) -> int:
        """Insert orders, skipping duplicates"""
        logger.info(f"Upserting {len(orders)} orders...")

        # Deduplicate by order_id (keep last occurrence)
        unique_orders = {}
        for o in orders:
            unique_orders[o.order_id] = o

        logger.info(f"Deduplicated to {len(unique_orders)} unique orders")

        # Get existing order_ids to skip
        existing_ids = set()
        with self.get_session() as session:
            result = session.query(OrderDB.order_id).all()
            existing_ids = {row[0] for row in result}

        logger.info(f"Found {len(existing_ids)} existing orders in database")

        # Filter out existing orders
        new_orders = [o for o in unique_orders.values() if o.order_id not in existing_ids]

        if not new_orders:
            logger.info("No new orders to insert")
            return 0

        logger.info(f"Inserting {len(new_orders)} new orders...")

        # Batch insert for better performance
        batch_size = 1000
        inserted = 0

        with self.get_session() as session:
            for i in range(0, len(new_orders), batch_size):
                batch = new_orders[i:i + batch_size]
                db_orders = [
                    OrderDB(
                        order_id=o.order_id,
                        order_date=o.order_date,
                        ship_mode=o.ship_mode,
                        segment=o.segment,
                        country=o.country,
                        city=o.city,
                        state=o.state,
                        postal_code=o.postal_code,
                        region=o.region,
                        category=o.category,
                        sub_category=o.sub_category,
                        product_id=o.product_id,
                        cost_price=o.cost_price,
                        list_price=o.list_price,
                        quantity=o.quantity,
                        discount_percent=o.discount_percent,
                        discount=o.discount,
                        sale_price=o.sale_price,
                        profit=o.profit,
                        is_returned=o.is_returned
                    )
                    for o in batch
                ]
                session.bulk_save_objects(db_orders)
                session.flush()  # Commit this batch
                inserted += len(batch)
                logger.info(f"Inserted batch {i // batch_size + 1}: {inserted}/{len(new_orders)} orders")

        logger.info(f"✅ Upserted {inserted} new orders (skipped {len(orders) - inserted} duplicates)")
        return inserted

    def get_db_type(self) -> str:
        """Get database type (sqlite, postgresql, duckdb)"""
        return self.engine.dialect.name

    def get_date_interval_sql(self, days: int) -> str:
        """Get SQL for date interval calculation based on database type"""
        db_type = self.get_db_type()

        if db_type == "postgresql":
            return f"CURRENT_DATE - INTERVAL '{days} days'"
        elif db_type == "sqlite":
            return f"date('now', '-{days} days')"
        elif db_type == "duckdb":
            return f"CURRENT_DATE - INTERVAL '{days}' DAY"
        else:
            return f"date('now', '-{days} days')"  # fallback to SQLite

    def get_date_diff_sql(self, date1: str, date2: str) -> str:
        """Get SQL for date difference calculation based on database type"""
        db_type = self.get_db_type()

        if db_type == "postgresql":
            return f"EXTRACT(EPOCH FROM ({date1} - {date2}))/86400"
        elif db_type == "sqlite":
            return f"JULIANDAY({date1}) - JULIANDAY({date2})"
        elif db_type == "duckdb":
            return f"DATE_DIFF('day', {date2}, {date1})"
        else:
            return f"JULIANDAY({date1}) - JULIANDAY({date2})"  # fallback to SQLite

    def get_date_format_sql(self, date_column: str, format_str: str = '%Y-%m') -> str:
        """Get SQL for date formatting based on database type"""
        db_type = self.get_db_type()

        if db_type == "postgresql":
            # Convert Python format to PostgreSQL format
            pg_format = format_str.replace('%Y', 'YYYY').replace('%m', 'MM').replace('%d', 'DD')
            return f"TO_CHAR({date_column}, '{pg_format}')"
        elif db_type == "sqlite":
            return f"strftime('{format_str}', {date_column})"
        elif db_type == "duckdb":
            return f"strftime({date_column}, '{format_str}')"
        else:
            return f"strftime('{format_str}', {date_column})"  # fallback to SQLite

    def close(self):
        """Close database connection"""
        self.engine.dispose()
        logger.info("Database connection closed")
