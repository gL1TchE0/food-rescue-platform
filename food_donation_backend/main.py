from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import datetime
from typing import List
import os

# Database Configuration
DATABASE_URL = "postgresql://postgres:surplusSync%4012345@db.bwrwszeftkiwbybolzrh.supabase.co:5432/postgres"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# SQLAlchemy Model
class Donation(Base):
    __tablename__ = "donations"
    id = Column(Integer, primary_key=True, index=True)
    donor_name = Column(String)
    food_type = Column(String)
    quantity_kg = Column(Float)
    latitude = Column(Float)
    longitude = Column(Float)
    address = Column(String)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)

# Base.metadata.drop_all(bind=engine) # Wipe and restart to fix schema
Base.metadata.create_all(bind=engine)

# Pydantic Schemas
class DonationCreate(BaseModel):
    donor_name: str
    food_type: str
    quantity_kg: float
    latitude: float
    longitude: float
    address: str
    expires_at: datetime

class DonationOut(DonationCreate):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

# FastAPI App
app = FastAPI(title="SurplusSync Backend")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/api/donations", response_model=DonationOut)
def create_donation(donation: DonationCreate, db: Session = Depends(get_db)):
    db_donation = Donation(**donation.dict())
    db.add(db_donation)
    db.commit()
    db.refresh(db_donation)
    return db_donation

@app.get("/api/donations", response_model=List[DonationOut])
def get_donations(db: Session = Depends(get_db)):
    return db.query(Donation).filter(Donation.expires_at > datetime.utcnow()).all()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
