from sqlalchemy.orm import Session
from database import SessionLocal
from models import NGO, NGOBranch, Donation, DonationStatusEnum

def setup_test_env():
    db = SessionLocal()
    try:
        print("🛠️ Setting up test environment...")
        
        # 1. Get Main NGO
        ngo = db.query(NGO).filter(NGO.email == "hope@foundation.org").first()
        if not ngo:
            print("❌ 'hope@foundation.org' NGO not found. Please run seed_data.py first.")
            return

        print(f"✅ Found NGO: {ngo.name} (ID: {ngo.id})")
        
        # 2. Reset Donations
        donations = db.query(Donation).all()
        reset_count = 0
        for d in donations:
            if d.status != DonationStatusEnum.AVAILABLE:
                d.status = DonationStatusEnum.AVAILABLE
                d.ngo_id = None
                d.branch_id = None
                d.claimed_at = None
                reset_count += 1
        
        print(f"✅ Reset {reset_count} donations to AVAILABLE.")

        # 3. Setup Branches
        # Clear existing branches to ensure clean state or update them?
        # Let's update or create specific ones.
        
        existing_branches = db.query(NGOBranch).filter(NGOBranch.ngo_id == ngo.id).all()
             
        # Define desired branches
        desired_branches = [
            {
                "name": "Bandra West Center (Small)",
                "address": "Bandra West, Mumbai",
                "capacity": 30.0  # Very small limit for easy testing
            },
            {
                "name": "Andheri East Hub (Large)",
                "address": "Andheri East, Mumbai",
                "capacity": 500.0 # Large limit
            }
        ]

        # If branches exist, update the first two, else create
        current_idx = 0
        for b in existing_branches:
            if current_idx < len(desired_branches):
                target = desired_branches[current_idx]
                b.name = target["name"]
                b.address = target["address"]
                b.storage_capacity = target["capacity"]
                b.is_active = 1
                print(f"   -> Updated Branch {b.id}: {b.name} (Cap: {b.storage_capacity}kg)")
                current_idx += 1
        
        # Create remaining needed branches
        while current_idx < len(desired_branches):
            target = desired_branches[current_idx]
            new_branch = NGOBranch(
                ngo_id=ngo.id,
                name=target["name"],
                address=target["address"],
                phone="1234567890",
                storage_capacity=target["capacity"],
                is_active=1
            )
            db.add(new_branch)
            print(f"   -> Created Branch: {new_branch.name} (Cap: {new_branch.storage_capacity}kg)")
            current_idx += 1

        db.commit()
        print("🎉 Test environment ready! Branches configured and claims reset.")

    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    setup_test_env()
