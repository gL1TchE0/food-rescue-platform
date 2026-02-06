from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import os
from database import init_db, SessionLocal
from models import Donation

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

def reset_schema():
    print("🔥 RESETTING SCHEMA...")
    with engine.connect() as conn:
        conn.execute(text("COMMIT")) # Close any open transaction
        
        # Drop the broken donations table
        print("   Dropping table 'donations'...")
        try:
            conn.execute(text("DROP TABLE IF EXISTS donations CASCADE"))
            print("   ✅ Dropped 'donations'.")
        except Exception as e:
            print(f"   ⚠️ Could not drop 'donations': {e}")

        conn.commit()

    print("🔧 Re-creating tables...")
    # This will create the table with the correct columns defined in models.py
    init_db()
    print("✅ Tables recreated.")

if __name__ == "__main__":
    reset_schema()
