from sqlalchemy import create_engine, inspect
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("❌ No DATABASE_URL found in .env")
    exit(1)

print(f"Connecting to database...")
engine = create_engine(DATABASE_URL)
inspector = inspect(engine)

def inspect_table(table_name):
    if not inspector.has_table(table_name):
        print(f"❌ Table '{table_name}' does not exist.")
        return

    print(f"\n📋 Schema for table '{table_name}':")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")

inspect_table("donations")
