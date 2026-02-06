"""
Seed database with sample data for testing (Safe Version)
"""

from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import exc

from database import SessionLocal, init_db
from models import NGO, NGOBranch, User, Donation, FoodTypeEnum, DonationStatusEnum, UserRoleEnum, ApprovalStatusEnum
from auth import get_password_hash

def seed_database():
    """Seed the database with sample data"""
    print("🔧 Initializing database...")
    init_db()
    db = SessionLocal()
    
    try:
        print("🌱 Seeding database...")
        
        # --- 1. SEED NGOs ---
        ngo1 = db.query(NGO).filter_by(email="hope@foundation.org").first()
        if not ngo1:
            ngo1 = NGO(
                name="Hope Foundation",
                email="hope@foundation.org",
                phone="+91-9876543210",
                address="123 Charity Street, Mumbai, Maharashtra",
                storage_capacity=500.0,
                approval_status=ApprovalStatusEnum.APPROVED
            )
            db.add(ngo1)
            print("   + Added NGO: Hope Foundation")

        ngo2 = db.query(NGO).filter_by(email="contact@foodforall.org").first()
        if not ngo2:
            ngo2 = NGO(
                name="Food For All",
                email="contact@foodforall.org",
                phone="+91-9876543211",
                address="456 Service Road, Delhi",
                storage_capacity=800.0,
                approval_status=ApprovalStatusEnum.APPROVED
            )
            db.add(ngo2)
            print("   + Added NGO: Food For All")

        ngo3 = db.query(NGO).filter_by(email="info@helpinghands.org").first()
        if not ngo3:
            ngo3 = NGO(
                name="Helping Hands NGO",
                email="info@helpinghands.org",
                phone="+91-9876543212",
                address="789 Care Avenue, Bangalore",
                storage_capacity=300.0,
                approval_status=ApprovalStatusEnum.PENDING
            )
            db.add(ngo3)
            print("   + Added NGO: Helping Hands NGO")
        
        db.commit() # Ensure IDs are fixed
        
        # --- 2. SEED USERS ---
        # Assuming we only need users for the first NGO for now or ensure uniqueness
        
        def create_user_if_not_exists(email, pwd, role, ngo_obj):
            u = db.query(User).filter_by(email=email).first()
            if not u:
                u = User(
                    email=email,
                    hashed_password=get_password_hash(pwd),
                    role=role,
                    ngo_id=ngo_obj.id if ngo_obj else None
                )
                db.add(u)
                print(f"   + Added User: {email}")

        if ngo1: create_user_if_not_exists("hope@foundation.org", "password123", UserRoleEnum.NGO, ngo1)
        if ngo2: create_user_if_not_exists("contact@foodforall.org", "password123", UserRoleEnum.NGO, ngo2)
        if ngo3: create_user_if_not_exists("info@helpinghands.org", "password123", UserRoleEnum.NGO, ngo3)
        
        db.commit()

        # --- 3. SEED DONATIONS ---
        # We only check if table is empty to avoid duplicates
        existing_donations = db.query(Donation).count()
        if existing_donations == 0:
            donations = [
                Donation(
                    donor_name="Grand Hyatt Hotel",
                    donor_phone="+91-9876540001",
                    food_type=FoodTypeEnum.MIXED,
                    quantity=45.5,
                    address="Grand Hyatt, Santacruz East, Mumbai",
                    latitude=19.0790,
                    longitude=72.8520,
                    expiry_time=datetime.utcnow() + timedelta(hours=4),
                    status=DonationStatusEnum.AVAILABLE
                ),
                Donation(
                    donor_name="Taj Lands End",
                    donor_phone="+91-9876540002",
                    food_type=FoodTypeEnum.NON_VEG,
                    quantity=30.0,
                    address="Bandstand, Bandra West, Mumbai",
                    latitude=19.0430,
                    longitude=72.8190,
                    expiry_time=datetime.utcnow() + timedelta(hours=3),
                    status=DonationStatusEnum.AVAILABLE
                ),
                Donation(
                    donor_name="Pizza Hut",
                    donor_phone="+91-9876540003",
                    food_type=FoodTypeEnum.SNACK,
                    quantity=15.0,
                    address="Linking Road, Khar West, Mumbai",
                    latitude=19.0700,
                    longitude=72.8350,
                    expiry_time=datetime.utcnow() + timedelta(hours=2),
                    status=DonationStatusEnum.AVAILABLE
                ),
                 Donation(
                    donor_name="Paradise Biryani",
                    donor_phone="+91-9876540004",
                    food_type=FoodTypeEnum.NON_VEG,
                    quantity=50.0,
                    address="Hitech City, Hyderabad",
                    latitude=17.4435, 
                    longitude=78.3772,
                    expiry_time=datetime.utcnow() + timedelta(hours=5),
                    status=DonationStatusEnum.AVAILABLE
                ),
                Donation(
                    donor_name="Dominos Pizza",
                    donor_phone="+91-9876540005",
                    food_type=FoodTypeEnum.NON_VEG,
                    quantity=12.5,
                    address="Dominos, Linking Road, Bandra",
                    latitude=19.0600,
                    longitude=72.8300,
                    expiry_time=datetime.utcnow() + timedelta(hours=6),
                    status=DonationStatusEnum.AVAILABLE
                ),
                Donation(
                    donor_name="Green Salad Bar",
                    donor_phone="+91-9876540006",
                    food_type=FoodTypeEnum.VEGAN,
                    quantity=8.0,
                    address="Green Salad, Juhu Tara Road",
                    latitude=19.0900,
                    longitude=72.8200,
                    expiry_time=datetime.utcnow() + timedelta(hours=3),
                    status=DonationStatusEnum.AVAILABLE
                ),
                Donation(
                    donor_name="Monginis Cake Shop",
                    donor_phone="+91-9876540007",
                    food_type=FoodTypeEnum.SNACK,
                    quantity=20.0,
                    address="Monginis, Dadar West",
                    latitude=19.0200,
                    longitude=72.8400,
                    expiry_time=datetime.utcnow() + timedelta(hours=5),
                    status=DonationStatusEnum.AVAILABLE
                ),            ]
            db.add_all(donations)
            db.commit()
            print(f"   + Added {len(donations)} donations.")
        else:
            print("   (Donations already exist, skipping)")

        print("🎉 Database seeded successfully!")

    except Exception as e:
        print(f"❌ Error seeding database: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    seed_database()
