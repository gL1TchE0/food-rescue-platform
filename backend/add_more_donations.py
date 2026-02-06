from datetime import datetime, timedelta
from database import SessionLocal
from models import Donation, FoodTypeEnum, DonationStatusEnum

def add_more():
    db = SessionLocal()
    
    new_donations = [
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
        ),
    ]

    count = 0
    for d in new_donations:
        # Simple check by donor name and quantity to avoid dupes
        exists = db.query(Donation).filter(
            Donation.donor_name == d.donor_name, 
            Donation.quantity == d.quantity
        ).first()
        
        if not exists:
            db.add(d)
            count += 1
            print(f"Adding donation from {d.donor_name}")
    
    db.commit()
    print(f"✅ Added {count} new donations.")

if __name__ == "__main__":
    add_more()
