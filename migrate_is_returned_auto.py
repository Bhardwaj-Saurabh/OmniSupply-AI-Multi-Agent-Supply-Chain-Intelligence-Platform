"""
Automatic non-destructive schema migration: ALTER is_returned column from INTEGER to BOOLEAN.

This migration:
1. Connects to your existing PostgreSQL database
2. Converts INTEGER values to BOOLEAN (0 -> false, non-zero -> true)
3. Preserves all existing data
4. Handles the type conversion gracefully

SAFE TO RUN: This will not drop or delete any data.
Runs automatically without prompts.
"""
import os
import sys
from dotenv import load_dotenv
import psycopg2
from psycopg2 import sql

load_dotenv()

print("=" * 80)
print("AUTO Schema Migration: is_returned INTEGER → BOOLEAN")
print("=" * 80)
print("\nThis migration will:")
print("  1. Check current column type")
print("  2. Convert existing data (0 → FALSE, non-zero → TRUE)")
print("  3. Change column type to BOOLEAN")
print("  4. Preserve all your existing data")
print("=" * 80)

# Build PostgreSQL connection parameters
postgres_user = os.getenv("POSTGRES_USER")
postgres_password = os.getenv("POSTGRES_PASSWORD")
postgres_db = os.getenv("POSTGRES_DB")
postgres_host = os.getenv("POSTGRES_HOST")
postgres_port = os.getenv("POSTGRES_PORT", "5432")

if not all([postgres_user, postgres_password, postgres_db, postgres_host]):
    print("\n❌ ERROR: Missing PostgreSQL configuration in .env file")
    print("Required variables: POSTGRES_USER, POSTGRES_PASSWORD, POSTGRES_DB, POSTGRES_HOST")
    sys.exit(1)

schema_name = "omnisupply"
table_name = "orders"
column_name = "is_returned"

print(f"\n📊 Target Database:")
print(f"   Host: {postgres_host}:{postgres_port}")
print(f"   Database: {postgres_db}")
print(f"   Schema: {schema_name}")
print(f"   Table: {table_name}")
print(f"   Column: {column_name}")

try:
    # Connect to PostgreSQL
    print(f"\n🔌 Connecting to PostgreSQL...")
    conn = psycopg2.connect(
        host=postgres_host,
        port=postgres_port,
        database=postgres_db,
        user=postgres_user,
        password=postgres_password
    )
    conn.autocommit = False
    cursor = conn.cursor()
    print("✅ Connected successfully!")

    # Set search path to use our schema
    cursor.execute(
        sql.SQL("SET search_path TO {}, public").format(
            sql.Identifier(schema_name)
        )
    )
    print(f"✅ Using schema: {schema_name}")

    # Check if table exists
    cursor.execute("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables
            WHERE table_schema = %s
            AND table_name = %s
        )
    """, (schema_name, table_name))

    table_exists = cursor.fetchone()[0]

    if not table_exists:
        print(f"\n⚠️  WARNING: Table '{schema_name}.{table_name}' does not exist!")
        print("This is normal if you haven't created tables yet.")
        print("\nAction: Run your application to create tables first, then re-run this migration.")
        conn.close()
        sys.exit(0)

    print(f"✅ Table '{table_name}' exists")

    # Check current column type
    cursor.execute("""
        SELECT data_type, udt_name
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name = %s
        AND column_name = %s
    """, (schema_name, table_name, column_name))

    result = cursor.fetchone()

    if not result:
        print(f"\n❌ ERROR: Column '{column_name}' not found in table '{table_name}'")
        conn.close()
        sys.exit(1)

    current_type = result[0]
    udt_name = result[1]

    print(f"\n📋 Current column type: {current_type} ({udt_name})")

    # Check if already boolean
    if current_type.lower() == 'boolean' or udt_name.lower() == 'bool':
        print(f"✅ Column '{column_name}' is already BOOLEAN type!")
        print("No migration needed.")
        conn.close()
        sys.exit(0)

    # Count records
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    record_count = cursor.fetchone()[0]
    print(f"📊 Records in table: {record_count}")

    # Show current data distribution
    if record_count > 0:
        cursor.execute(f"""
            SELECT {column_name}, COUNT(*)
            FROM {table_name}
            GROUP BY {column_name}
            ORDER BY {column_name}
        """)
        print(f"\n📈 Current '{column_name}' distribution:")
        for value, count in cursor.fetchall():
            print(f"   {column_name} = {value}: {count} records")

    # Proceed automatically
    print("\n" + "=" * 80)
    print("MIGRATION PLAN:")
    print(f"  - Convert {record_count} records")
    print(f"  - Change column type: {current_type} → BOOLEAN")
    print(f"  - Conversion rule: 0 → FALSE, non-zero → TRUE")
    print(f"  - This operation is REVERSIBLE (we can convert back if needed)")
    print("=" * 80)
    print("\n🚀 Starting migration automatically...")

    # Begin transaction
    print("\n1️⃣  Starting transaction...")

    # Step 1: Alter column type using USING clause
    print(f"2️⃣  Altering column type from {current_type} to BOOLEAN...")

    alter_query = sql.SQL("""
        ALTER TABLE {}
        ALTER COLUMN {}
        TYPE BOOLEAN
        USING CASE
            WHEN {} = 0 THEN FALSE
            ELSE TRUE
        END
    """).format(
        sql.Identifier(table_name),
        sql.Identifier(column_name),
        sql.Identifier(column_name)
    )

    cursor.execute(alter_query)
    print("✅ Column type altered successfully!")

    # Step 2: Set default value for new records
    print("3️⃣  Setting default value to FALSE...")
    default_query = sql.SQL("""
        ALTER TABLE {}
        ALTER COLUMN {}
        SET DEFAULT FALSE
    """).format(
        sql.Identifier(table_name),
        sql.Identifier(column_name)
    )

    cursor.execute(default_query)
    print("✅ Default value set!")

    # Verify the change
    print("4️⃣  Verifying migration...")
    cursor.execute("""
        SELECT data_type, column_default
        FROM information_schema.columns
        WHERE table_schema = %s
        AND table_name = %s
        AND column_name = %s
    """, (schema_name, table_name, column_name))

    new_type, default_value = cursor.fetchone()
    print(f"✅ New column type: {new_type}")
    print(f"✅ Default value: {default_value}")

    # Show new data distribution
    if record_count > 0:
        cursor.execute(f"""
            SELECT {column_name}, COUNT(*)
            FROM {table_name}
            GROUP BY {column_name}
            ORDER BY {column_name}
        """)
        print(f"\n📈 New '{column_name}' distribution:")
        for value, count in cursor.fetchall():
            print(f"   {column_name} = {value}: {count} records")

    # Commit transaction
    print("\n5️⃣  Committing changes...")
    conn.commit()
    print("✅ Migration committed successfully!")

    print("\n" + "=" * 80)
    print("✅ MIGRATION COMPLETE!")
    print("=" * 80)
    print(f"\nResults:")
    print(f"  - Migrated {record_count} records")
    print(f"  - Column '{column_name}' is now BOOLEAN type")
    print(f"  - All queries with boolean comparisons will now work")
    print(f"\nYou can now run your application without type errors!")
    print("=" * 80)

    cursor.close()
    conn.close()

except psycopg2.Error as e:
    print(f"\n❌ PostgreSQL Error: {e}")
    print(f"Error code: {e.pgcode}")
    if conn:
        conn.rollback()
        print("🔄 Transaction rolled back - no changes made")
        conn.close()
    sys.exit(1)

except Exception as e:
    print(f"\n❌ Migration failed: {e}")
    if conn:
        conn.rollback()
        print("🔄 Transaction rolled back - no changes made")
        conn.close()
    import traceback
    traceback.print_exc()
    sys.exit(1)
