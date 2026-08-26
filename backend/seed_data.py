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
        os.path.join(script_dir, "..", "Old_Models_and_Dataset", "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "..", "DengueOutbreakPrediction", "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "..", "Dataset", "DengueAndClimateBangladesh.csv"),
        os.path.join(script_dir, "DengueOutbreakPrediction", "Dataset", "DengueAndClimateBangladesh.csv")
    ]
    for p in possible_paths:
        if os.path.exists(p):
            return os.path.abspath(p)
    return None

def seed_db(db: Session):
    """Seed users, climate data, and dengue records from CSV for all supported districts."""
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
    
    # 3. Seed Climate Data and Dengue Records from CSV district by district
    csv_path = get_dataset_path()
    if not csv_path:
        print("WARNING: DengueAndClimateBangladesh.csv not found, skipping historical seeding.")
        return
        
    try:
        df = pd.read_csv(csv_path)
        
        # Check if Dhaka is already seeded, if not seed it first
        dhaka_count = db.query(DengueRecord).filter(DengueRecord.location == "Dhaka").count()
        if dhaka_count == 0:
            print("Seeding Dhaka historical records...")
            climate_list = []
            dengue_list = []
            for _, row in df.iterrows():
                year = int(row['YEAR'])
                month = int(row['MONTH'])
                climate_list.append(ClimateData(
                    year=year, month=month,
                    min_temp=float(row['MIN']), max_temp=float(row['MAX']),
                    humidity=float(row['HUMIDITY']), rainfall=float(row['RAINFALL']),
                    location="Dhaka"
                ))
                dengue_list.append(DengueRecord(
                    year=year, month=month,
                    cases=int(row['DENGUE']), location="Dhaka"
                ))
            db.bulk_save_objects(climate_list)
            db.bulk_save_objects(dengue_list)
            db.commit()
            print("Dhaka historical records seeded.")

        # Now train baseline model if model file doesn't exist, so we can use it for seeding other districts
        backend_dir = os.path.dirname(os.path.realpath(__file__))
        model_path = os.path.join(backend_dir, "dengue_model.joblib")
        
        if not os.path.exists(model_path):
            print("Training baseline ML prediction model...")
            train_ml_model(db)
            print("Model trained.")

        # Seed other districts using weather offsets and ML predictions
        districts = {
            "Chittagong": {"min_temp_offset": 0.5, "max_temp_offset": -0.5, "humidity_offset": 4.0, "rainfall_multiplier": 1.35},
            "Jamalpur": {"min_temp_offset": -1.5, "max_temp_offset": 0.2, "humidity_offset": -2.0, "rainfall_multiplier": 0.90},
            "Sylhet": {"min_temp_offset": -0.5, "max_temp_offset": -1.0, "humidity_offset": 2.0, "rainfall_multiplier": 1.65}
        }

        # We import predict_dengue here to avoid circular dependencies
        from .ml_model import predict_dengue

        for loc, offsets in districts.items():
            count = db.query(DengueRecord).filter(DengueRecord.location == loc).count()
            if count > 0:
                print(f"Historical records for {loc} already present. Skipping.")
                continue
                
            print(f"Seeding {loc} historical records using weather offsets and ML predictions...")
            climate_list = []
            dengue_list = []
            for _, row in df.iterrows():
                year = int(row['YEAR'])
                month = int(row['MONTH'])
                
                # Apply offsets to create realistic local climate
                min_temp = float(row['MIN']) + offsets["min_temp_offset"]
                max_temp = float(row['MAX']) + offsets["max_temp_offset"]
                humidity = min(100.0, max(0.0, float(row['HUMIDITY']) + offsets["humidity_offset"]))
                rainfall = float(row['RAINFALL']) * offsets["rainfall_multiplier"]
                
                climate_list.append(ClimateData(
                    year=year, month=month,
                    min_temp=min_temp, max_temp=max_temp,
                    humidity=humidity, rainfall=rainfall,
                    location=loc
                ))
                
                # Predict cases based on the new local weather
                predicted_cases, _ = predict_dengue(db, month, min_temp, max_temp, humidity, rainfall)
                
                dengue_list.append(DengueRecord(
                    year=year, month=month,
                    cases=predicted_cases, location=loc
                ))
                
            db.bulk_save_objects(climate_list)
            db.bulk_save_objects(dengue_list)
            db.commit()
            print(f"{loc} historical records seeded successfully!")
            
    except Exception as e:
        db.rollback()
        print(f"ERROR: Failed to seed historical data: {str(e)}")

if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()
