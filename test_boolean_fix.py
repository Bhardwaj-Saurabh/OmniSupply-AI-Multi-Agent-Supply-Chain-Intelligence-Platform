"""
Test script to verify the is_returned BOOLEAN migration works correctly.

This script will:
1. Connect to PostgreSQL
2. Insert test orders with boolean is_returned values
3. Query orders using boolean comparisons
4. Verify everything works without type errors
"""
import os
from dotenv import load_dotenv
from datetime import datetime
from src.storage.sql.database import DatabaseClient
from src.data.models import Order

load_dotenv()

print("=" * 80)
print("Testing BOOLEAN Migration Fix")
print("=" * 80)

# Build PostgreSQL connection
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

database_url = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}:{postgres_port}/{postgres_db}"

print(f"\n📊 Connecting to: {postgres_host}:{postgres_port}/{postgres_db}")

try:
    db = DatabaseClient(database_url=database_url)
    print(f"✅ Connected successfully!")

    # Check current data
    counts = db.get_table_counts()
    print(f"\n📈 Current data in database:")
    for table, count in counts.items():
        print(f"   • {table}: {count} records")

    # Create test orders with boolean values
    print("\n" + "=" * 80)
    print("TEST 1: Insert orders with boolean is_returned values")
    print("=" * 80)

    test_orders = [
        Order(
            order_id="TEST-001",
            order_date=datetime(2024, 1, 1),
            ship_mode="Standard",
            segment="Consumer",
            country="USA",
            city="New York",
            state="NY",
            postal_code="10001",
            region="East",
            category="Technology",
            sub_category="Phones",
            product_id="PROD-001",
            cost_price=500.0,
            list_price=800.0,
            quantity=1,
            discount_percent=10.0,
            discount=80.0,
            sale_price=720.0,
            profit=220.0,
            is_returned=False  # Boolean value
        ),
        Order(
            order_id="TEST-002",
            order_date=datetime(2024, 1, 2),
            ship_mode="Express",
            segment="Corporate",
            country="USA",
            city="Los Angeles",
            state="CA",
            postal_code="90001",
            region="West",
            category="Technology",
            sub_category="Laptops",
            product_id="PROD-002",
            cost_price=800.0,
            list_price=1200.0,
            quantity=1,
            discount_percent=5.0,
            discount=60.0,
            sale_price=1140.0,
            profit=340.0,
            is_returned=True  # Boolean value
        )
    ]

    print(f"📝 Inserting {len(test_orders)} test orders...")
    inserted = db.insert_orders(test_orders)
    print(f"✅ Inserted {inserted} orders with boolean is_returned values")

    # Test queries with boolean comparisons
    print("\n" + "=" * 80)
    print("TEST 2: Query orders using boolean comparisons")
    print("=" * 80)

    # Query 1: Get non-returned orders (is_returned = FALSE)
    print("\n📊 Query 1: SELECT * FROM orders WHERE is_returned = FALSE")
    non_returned = db.execute_query("""
        SELECT order_id, category, is_returned
        FROM orders
        WHERE is_returned = FALSE
        LIMIT 5
    """)
    print(f"✅ Found {len(non_returned)} non-returned orders:")
    for order in non_returned:
        print(f"   • {order['order_id']}: {order['category']} (returned: {order['is_returned']})")

    # Query 2: Get returned orders (is_returned = TRUE)
    print("\n📊 Query 2: SELECT * FROM orders WHERE is_returned = TRUE")
    returned = db.execute_query("""
        SELECT order_id, category, is_returned
        FROM orders
        WHERE is_returned = TRUE
        LIMIT 5
    """)
    print(f"✅ Found {len(returned)} returned orders:")
    for order in returned:
        print(f"   • {order['order_id']}: {order['category']} (returned: {order['is_returned']})")

    # Query 3: Count orders by return status
    print("\n📊 Query 3: SELECT is_returned, COUNT(*) FROM orders GROUP BY is_returned")
    stats = db.execute_query("""
        SELECT is_returned, COUNT(*) as count
        FROM orders
        GROUP BY is_returned
    """)
    print(f"✅ Return statistics:")
    for stat in stats:
        status = "Returned" if stat['is_returned'] else "Not Returned"
        print(f"   • {status}: {stat['count']} orders")

    # Query 4: Test boolean NOT operator
    print("\n📊 Query 4: SELECT * FROM orders WHERE NOT is_returned")
    not_returned = db.execute_query("""
        SELECT COUNT(*) as count
        FROM orders
        WHERE NOT is_returned
    """)
    print(f"✅ Orders NOT returned: {not_returned[0]['count']}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED!")
    print("=" * 80)
    print("\n✨ Summary:")
    print("  1. Successfully inserted orders with boolean values (True/False)")
    print("  2. Successfully queried with: is_returned = FALSE")
    print("  3. Successfully queried with: is_returned = TRUE")
    print("  4. Successfully used boolean GROUP BY aggregation")
    print("  5. Successfully used NOT operator with boolean column")
    print("\n🎉 The migration fix is working perfectly!")
    print("=" * 80)

    db.close()

except Exception as e:
    print(f"\n❌ Test failed: {e}")
    import traceback
    traceback.print_exc()
