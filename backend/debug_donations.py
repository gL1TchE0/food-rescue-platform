from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from dotenv import load_dotenv
import os
from models import Donation
from datetime import datetime

load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
db = SessionLocal()

print(f"🕒 Current UTC Time: {datetime.utcnow()}")
print("-" * 50)

donations = db.query(Donation).all()
print(f"📦 Total Donations in DB: {len(donations)}")

for d in donations:
    is_active = d.expiry_time > datetime.utcnow()
    print(f"ID: {d.id} | Status: {d.status} | Expiry: {d.expiry_time} | Active? {is_active} | Created: {d.created_at}")

print("-" * 50)
print("🔍 Checking API Query logic:")
available = db.query(Donation).filter(Donation.status == "AVAILABLE").all() # Raw string check first
print(f"Count with status='AVAILABLE': {len(available)}")

from models import DonationStatusEnum
available_enum = db.query(Donation).filter(Donation.status == DonationStatusEnum.AVAILABLE).all()
print(f"Count with Enum=AVAILABLE: {len(available_enum)}")

final_query = db.query(Donation).filter(
    Donation.status == DonationStatusEnum.AVAILABLE,
    Donation.expiry_time > datetime.utcnow()
).all()
print(f"Count with Query (Status + Expiry): {len(final_query)}")
