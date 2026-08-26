import os
import pandas as pd
from sqlalchemy.orm import Session
from .database import engine, Base, SessionLocal
from .models import User, ClimateData, DengueRecord, SystemConfig
from .auth import get_password_hash
from .ml_model import train_ml_model

def get_dataset_path():
    """Locate the CSV dataset file."""
    script_dir = os.path.dirname(os.path.realpath(__file__))
    possible_paths = [
        os.path.join(script_dir, "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "..", "DengueOutbreakPrediction", "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "..", "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "DengueOutbreakPrediction", "Dataset", "DengueAndClimateBangladesh.csv")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def seed_db(db: Session):
    """Seed users, climate data, and dengue records from CSV."""
    print("Initializing Database tables...")
    Base.metadata.create_all(bind=engine)
    
    # 1. Seed System Configuration default thresholds
    configs = {
        "threshold_medium": "150",
        "threshold_high": "400",
    }
    for k, v in configs.items():
        if not db.query(SystemConfig).filter(SystemConfig.key == k).first():
            db.add(SystemConfig(key=k, value=v))
    
    # 2. Seed Default Users
    users_to_seed = [
        {"username": "admin", "password": "admin123", "role": "Admin"},
        {"username": "inspector", "password": "inspector123", "role": "Inspector"},
        {"username": "user", "password": "user123", "role": "Public"}
    ]
    
    for user_info in users_to_seed:
        exists = db.query(User).filter(User.username == user_info["username"]).first()
        if not exists:
            print(f"Seeding user: {user_info['username']} ({user_info['role']})")
            db.add(User(
                username=user_info["username"],
                password_hash=get_password_hash(user_info["password"]),
                role=user_info["role"],
                is_active=True
            ))
    db.commit()
    
    # 3. Seed Climate Data and Dengue Records from CSV
    if db.query(ClimateData).count() > 0 or db.query(DengueRecord).count() > 0:
        print("Climate/Dengue records already present in DB. Skipping CSV import.")
        return
        
    csv_path = get_dataset_path()
    if not csv_path:
        print("WARNING: DengueAndClimateBangladesh.csv not found, skipping historical seeding.")
        return
        
    print(f"Loading historical data from: {csv_path}")
    try:
        df = pd.read_csv(csv_path)
        
        # Batch insert
        climate_list = []
        dengue_list = []
        
        for _, row in df.iterrows():
            year = int(row['YEAR'])
            month = int(row['MONTH'])
            
            climate_list.append(ClimateData(
                year=year,
                month=month,
                min_temp=float(row['MIN']),
                max_temp=float(row['MAX']),
                humidity=float(row['HUMIDITY']),
                rainfall=float(row['RAINFALL'])
            ))
            
            dengue_list.append(DengueRecord(
                year=year,
                month=month,
                cases=int(row['DENGUE']),
                location="Dhaka"
            ))
            
        print(f"Inserting {len(climate_list)} climate & dengue records...")
        db.bulk_save_objects(climate_list)
        db.bulk_save_objects(dengue_list)
        db.commit()
        print("Historical database seeding completed successfully!")
        
        # Train baseline model immediately
        print("Training baseline ML prediction model...")
        train_ml_model(db)
        print("Model trained and coefficients successfully saved!")
        
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to seed historical data: {str(e)}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
