import os
import io
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from sqlalchemy import desc, func

from .database import get_db, SessionLocal
from .models import User, ClimateData, DengueRecord, Prediction, Notification, AuditLog, SystemConfig
from .schemas import (
    UserCreate, UserResponse, Token, ClimateDataResponse, ClimateDataCreate,
    DengueRecordResponse, DengueRecordCreate, PredictionResponse, NotificationResponse,
    AuditLogResponse, SystemConfigResponse, SystemConfigUpdate, ModelMetrics
)
from .auth import verify_password, create_access_token, get_current_user, RoleChecker, get_password_hash
from .ml_model import predict_dengue, get_current_metrics, train_ml_model, trigger_warnings_if_needed
from .pdf_generator import generate_report_pdf
from .seed_data import seed_db

app = FastAPI(title="Dengue Outbreak Prediction & Early Warning System", version="1.0.0")

# Enable CORS for frontend local development and production domain
ALLOWED_ORIGINS = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://dengueoutbreakprediction.netlify.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup DB seeding
@app.on_event("startup")
def startup_event():
    db = SessionLocal()
    try:
        seed_db(db)
    finally:
        db.close()

# Helper for Audit Logging
def log_audit(db: Session, username: str, action: str, details: str):
    log = AuditLog(username=username, action=action, details=details)
    db.add(log)
    db.commit()

# --- AUTHENTICATION ENDPOINTS ---

@app.post("/api/auth/register", response_model=UserResponse)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already exists")
    
    hashed_password = get_password_hash(user.password)
    # Default is Public. Admins must promote to Inspector or Admin
    db_user = User(
        username=user.username,
        password_hash=hashed_password,
        role=user.role,
        is_active=True
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    
    log_audit(db, user.username, "REGISTER", f"Account registered with role: {user.role}")
    return db_user

@app.post("/api/auth/login", response_model=Token)
def login_for_access_token(form_data: UserCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == form_data.username).first()
    if not user or not verify_password(form_data.password, user.password_hash):
        log_audit(db, form_data.username, "LOGIN_FAILED", "Invalid username or password")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Account is deactivated")
        
    access_token = create_access_token(data={"sub": user.username, "role": user.role})
    log_audit(db, user.username, "LOGIN_SUCCESS", f"User logged in from client")
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "username": user.username,
        "role": user.role
    }

# --- ADMIN USER MANAGEMENT ---

@app.get("/api/admin/users", response_model=List[UserResponse])
def get_all_users(
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    return db.query(User).all()

@app.put("/api/admin/users/{user_id}/role", response_model=UserResponse)
def update_user_role(
    user_id: int,
    role: str = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if role not in ["Admin", "Inspector", "Public"]:
        raise HTTPException(status_code=400, detail="Invalid role")
        
    old_role = user.role
    user.role = role
    db.commit()
    log_audit(db, admin.username, "ROLE_CHANGE", f"Changed user {user.username} role from {old_role} to {role}")
    return user

@app.put("/api/admin/users/{user_id}/status", response_model=UserResponse)
def toggle_user_status(
    user_id: int,
    is_active: bool = Query(...),
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    if user.id == admin.id:
        raise HTTPException(status_code=400, detail="Cannot deactivate yourself")
        
    user.is_active = is_active
    db.commit()
    action = "ACTIVATE" if is_active else "DEACTIVATE"
    log_audit(db, admin.username, f"USER_{action}", f"Changed user {user.username} status to {is_active}")
    return user

# --- CLIMATE RECORDS CRUD ---

@app.get("/api/records/climate", response_model=List[ClimateDataResponse])
def read_climate_records(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(ClimateData).order_by(desc(ClimateData.year), desc(ClimateData.month)).limit(100).all()

@app.post("/api/records/climate", response_model=ClimateDataResponse)
def create_climate_record(
    record: ClimateDataCreate,
    db: Session = Depends(get_db),
    inspector: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    exists = db.query(ClimateData).filter(
        ClimateData.year == record.year,
        ClimateData.month == record.month
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Climate record already exists for this month")
        
    db_record = ClimateData(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    log_audit(db, inspector.username, "CLIMATE_CREATE", f"Added climate record for {record.month}/{record.year}")
    return db_record

@app.delete("/api/records/climate/{record_id}")
def delete_climate_record(
    record_id: int,
    db: Session = Depends(get_db),
    inspector: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    record = db.query(ClimateData).filter(ClimateData.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    db.delete(record)
    db.commit()
    log_audit(db, inspector.username, "CLIMATE_DELETE", f"Deleted record ID {record_id} ({record.month}/{record.year})")
    return {"detail": "Record deleted"}

# --- DENGUE RECORDS CRUD ---

@app.get("/api/records/dengue", response_model=List[DengueRecordResponse])
def read_dengue_records(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(DengueRecord).order_by(desc(DengueRecord.year), desc(DengueRecord.month)).limit(100).all()

@app.post("/api/records/dengue", response_model=DengueRecordResponse)
def create_dengue_record(
    record: DengueRecordCreate,
    db: Session = Depends(get_db),
    inspector: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    exists = db.query(DengueRecord).filter(
        DengueRecord.year == record.year,
        DengueRecord.month == record.month,
        DengueRecord.location == record.location
    ).first()
    if exists:
        raise HTTPException(status_code=400, detail="Dengue record already exists for this location and date")
        
    db_record = DengueRecord(**record.dict())
    db.add(db_record)
    db.commit()
    db.refresh(db_record)
    log_audit(db, inspector.username, "DENGUE_CREATE", f"Added dengue cases: {record.cases} for {record.month}/{record.year}")
    return db_record

@app.delete("/api/records/dengue/{record_id}")
def delete_dengue_record(
    record_id: int,
    db: Session = Depends(get_db),
    inspector: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    record = db.query(DengueRecord).filter(DengueRecord.id == record_id).first()
    if not record:
        raise HTTPException(status_code=404, detail="Record not found")
        
    db.delete(record)
    db.commit()
    log_audit(db, inspector.username, "DENGUE_DELETE", f"Deleted dengue record ID {record_id} ({record.month}/{record.year})")
    return {"detail": "Record deleted"}

# --- PREDICTIONS & ANALYTICS ---

@app.post("/api/predictions/predict", response_model=PredictionResponse)
def generate_prediction(
    year: int = Query(...),
    month: int = Query(...),
    min_temp: float = Query(...),
    max_temp: float = Query(...),
    humidity: float = Query(...),
    rainfall: float = Query(...),
    location: str = Query("Dhaka"),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    cases, risk = predict_dengue(db, min_temp, max_temp, humidity, rainfall)
    
    # Save the prediction in DB
    db_pred = Prediction(
        year=year,
        month=month,
        predicted_cases=cases,
        risk_level=risk,
        location=location
    )
    db.add(db_pred)
    db.commit()
    db.refresh(db_pred)
    
    # Trigger notifications if MEDIUM/HIGH risk
    trigger_warnings_if_needed(db, year, month, cases, risk)
    
    log_audit(db, user.username, "PREDICTION", f"Ran prediction for {month}/{year}: {cases} cases ({risk} risk)")
    return db_pred

@app.get("/api/predictions/history", response_model=List[PredictionResponse])
def get_prediction_history(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user)
):
    return db.query(Prediction).order_by(desc(Prediction.created_at)).limit(50).all()

# --- NOTIFICATIONS LOGS ---

@app.get("/api/notifications", response_model=List[NotificationResponse])
def get_notifications(
    db: Session = Depends(get_db),
    user: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    return db.query(Notification).order_by(desc(Notification.timestamp)).limit(100).all()

# --- ADMIN MODEL/CONFIG CONTROL ---

@app.get("/api/admin/metrics", response_model=ModelMetrics)
def get_model_metrics(
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    return get_current_metrics(db)

@app.post("/api/admin/retrain", response_model=ModelMetrics)
def retrain_model(
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    metrics = train_ml_model(db)
    log_audit(db, admin.username, "MODEL_RETRAIN", f"Retrained ML model with R2={metrics.r2:.4f}")
    return metrics

@app.get("/api/admin/config", response_model=List[SystemConfigResponse])
def get_configs(
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    return db.query(SystemConfig).filter(SystemConfig.key.like("threshold_%")).all()

@app.put("/api/admin/config/{key}", response_model=SystemConfigResponse)
def update_config(
    key: str,
    payload: SystemConfigUpdate,
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if not cfg:
        raise HTTPException(status_code=404, detail="Config key not found")
        
    old_val = cfg.value
    cfg.value = payload.value
    db.commit()
    log_audit(db, admin.username, "CONFIG_CHANGE", f"Updated {key} from {old_val} to {payload.value}")
    return cfg

@app.get("/api/admin/logs", response_model=List[AuditLogResponse])
def get_audit_logs(
    db: Session = Depends(get_db),
    admin: User = Depends(RoleChecker(allowed_roles=["Admin"]))
):
    return db.query(AuditLog).order_by(desc(AuditLog.timestamp)).limit(200).all()

# --- WEATHER DATA INTEGRATION ---

@app.get("/api/weather/current")
def get_current_weather():
    import urllib.request
    import json
    url = (
        "https://api.open-meteo.com/v1/forecast?"
        "latitude=23.8103&longitude=90.4125"
        "&current=temperature_2m,relative_humidity_2m"
        "&daily=temperature_2m_max,temperature_2m_min,precipitation_sum"
        "&timezone=auto"
    )
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res_data = json.loads(response.read().decode())
            current = res_data.get("current", {})
            daily = res_data.get("daily", {})
            
            max_temp_list = daily.get("temperature_2m_max", [])
            min_temp_list = daily.get("temperature_2m_min", [])
            rainfall_list = daily.get("precipitation_sum", [])
            
            max_temp = max_temp_list[0] if max_temp_list else current.get("temperature_2m", 32.0)
            min_temp = min_temp_list[0] if min_temp_list else current.get("temperature_2m", 25.0)
            humidity = current.get("relative_humidity_2m", 80.0)
            rainfall = rainfall_list[0] if rainfall_list else 0.0
            
            return {
                "status": "success",
                "location": "Dhaka",
                "current_temp": current.get("temperature_2m", 28.0),
                "min_temp": min_temp,
                "max_temp": max_temp,
                "humidity": humidity,
                "rainfall": rainfall
            }
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Failed to fetch weather data: {str(e)}"
        )

# --- PUBLIC DASHBOARD DATA ---

@app.get("/api/dashboard/summary")
def get_dashboard_summary(db: Session = Depends(get_db)):
    # 1. Fetch latest dengue record cases
    latest_record = db.query(DengueRecord).order_by(desc(DengueRecord.year), desc(DengueRecord.month)).first()
    latest_cases = latest_record.cases if latest_record else 0
    latest_date = f"{latest_record.month}/{latest_record.year}" if latest_record else "N/A"
    
    # 2. Total historical cases in database
    total_cases = db.query(func.sum(DengueRecord.cases)).scalar() or 0
    
    # 3. Fetch latest prediction
    latest_pred = db.query(Prediction).order_by(desc(Prediction.created_at)).first()
    pred_cases = latest_pred.predicted_cases if latest_pred else 0
    pred_risk = latest_pred.risk_level if latest_pred else "LOW"
    pred_date = f"{latest_pred.month}/{latest_pred.year}" if latest_pred else "N/A"
    
    # 4. Generate historical data points for line charts (last 24 months)
    history = db.query(
        DengueRecord.year,
        DengueRecord.month,
        DengueRecord.cases,
        ClimateData.min_temp,
        ClimateData.max_temp,
        ClimateData.humidity,
        ClimateData.rainfall
    ).filter(
        DengueRecord.year == ClimateData.year,
        DengueRecord.month == ClimateData.month
    ).order_by(DengueRecord.year, DengueRecord.month).all()
    
    historical_chart = [
        {
            "date": f"{r.month}/{r.year}",
            "cases": r.cases,
            "min_temp": r.min_temp,
            "max_temp": r.max_temp,
            "humidity": r.humidity,
            "rainfall": r.rainfall
        }
        for r in history[-36:] # Limit to last 3 years of records
    ]
    
    # Calculate seasonal breakdown averages
    # seasons: Monsoon (Jun-Sep), Post-Monsoon (Oct-Nov), Winter (Dec-Feb), Pre-Monsoon (Mar-May)
    seasons = {
        "Pre-Monsoon": [3, 4, 5],
        "Monsoon": [6, 7, 8, 9],
        "Post-Monsoon": [10, 11],
        "Winter": [12, 1, 2]
    }
    
    seasonal_data = {}
    for s_name, months in seasons.items():
        avg_cases = db.query(func.avg(DengueRecord.cases)).filter(DengueRecord.month.in_(months)).scalar() or 0
        seasonal_data[s_name] = int(round(avg_cases))
        
    return {
        "latest_cases": latest_cases,
        "latest_date": latest_date,
        "total_cases": total_cases,
        "predicted_cases": pred_cases,
        "predicted_risk": pred_risk,
        "predicted_date": pred_date,
        "historical_chart": historical_chart,
        "seasonal_data": seasonal_data
    }
# --- REALTIME WEATHER API ---

@app.get("/api/weather/realtime")
def get_realtime_weather():
    url = "https://api.open-meteo.com/v1/forecast?latitude=23.8103&longitude=90.4125&current=temperature_2m,relative_humidity_2m,precipitation&daily=temperature_2m_max,temperature_2m_min,precipitation_sum&timezone=auto"
    try:
        import urllib.request
        import json
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=5) as response:
            res = json.loads(response.read().decode())
            
        min_temp = res['daily']['temperature_2m_min'][0]
        max_temp = res['daily']['temperature_2m_max'][0]
        humidity = res['current']['relative_humidity_2m']
        rainfall = res['daily']['precipitation_sum'][0]
        
        return {
            "min_temp": float(min_temp),
            "max_temp": float(max_temp),
            "humidity": float(humidity),
            "rainfall": float(rainfall),
            "location": "Dhaka",
            "source": "Open-Meteo API"
        }
    except Exception as e:
        raise HTTPException(status_code=502, detail=f"Failed to fetch weather data: {str(e)}")

# --- PDF REPORT DOWNLOAD ---

@app.get("/api/reports/pdf")
def download_pdf_report(
    year: int = Query(...),
    month: int = Query(...),
    db: Session = Depends(get_db),
    inspector: User = Depends(RoleChecker(allowed_roles=["Inspector", "Admin"]))
):
    try:
        pdf_bytes = generate_report_pdf(db, year, month, inspector.username)
        
        log_audit(db, inspector.username, "PDF_REPORT", f"Generated PDF report for {month}/{year}")
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=dengue_report_{year}_{month:02d}.pdf"
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

# --- FRONTEND ASSETS SERVING ---

# Serve React static build folder if present
frontend_dist_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "frontend", "dist"))
if os.path.exists(frontend_dist_path):
    # Mount files
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist_path, "assets")), name="assets")
    
    # Catch-all endpoint for SPAs
    @app.get("/{full_path:path}")
    def serve_frontend(full_path: str):
        # Prevent intercepting API calls
        if full_path.startswith("api/") or full_path.startswith("docs") or full_path.startswith("redoc") or full_path.startswith("openapi.json"):
            raise HTTPException(status_code=404)
        
        index_file = os.path.join(frontend_dist_path, "index.html")
        if os.path.exists(index_file):
            return FileResponse(index_file)
        raise HTTPException(status_code=404, detail="Frontend assets not found")
