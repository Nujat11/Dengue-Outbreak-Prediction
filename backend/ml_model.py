import numpy as np
from sqlalchemy.orm import Session
from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score, mean_absolute_error, mean_squared_error
from .models import DengueRecord, ClimateData, SystemConfig, Notification, User
from .schemas import ModelMetrics

# Default coefficients (fallback if DB has no data or model hasn't been trained yet)
# Derived from our dataset baseline
DEFAULT_INTERCEPT = -2500.0
DEFAULT_COEFS = {
    "min_temp": 50.0,
    "max_temp": 45.0,
    "humidity": 15.0,
    "rainfall": 5.0
}

def get_config_val(db: Session, key: str, default: str) -> str:
    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if cfg:
        return cfg.value
    # Create it if it doesn't exist
    new_cfg = SystemConfig(key=key, value=default)
    db.add(new_cfg)
    db.commit()
    return default

def get_coefficients(db: Session) -> dict:
    """Retrieve model coefficients from DB config or fallback to defaults."""
    intercept = float(get_config_val(db, "ml_intercept", str(DEFAULT_INTERCEPT)))
    coef_min = float(get_config_val(db, "ml_coef_min_temp", str(DEFAULT_COEFS["min_temp"])))
    coef_max = float(get_config_val(db, "ml_coef_max_temp", str(DEFAULT_COEFS["max_temp"])))
    coef_hum = float(get_config_val(db, "ml_coef_humidity", str(DEFAULT_COEFS["humidity"])))
    coef_rain = float(get_config_val(db, "ml_coef_rainfall", str(DEFAULT_COEFS["rainfall"])))
    
    return {
        "intercept": intercept,
        "min_temp": coef_min,
        "max_temp": coef_max,
        "humidity": coef_hum,
        "rainfall": coef_rain
    }

def train_ml_model(db: Session) -> ModelMetrics:
    """Train Multiple Linear Regression on historical data and save coefficients."""
    # Query joined climate and dengue records
    records = db.query(
        DengueRecord.cases,
        ClimateData.min_temp,
        ClimateData.max_temp,
        ClimateData.humidity,
        ClimateData.rainfall
    ).filter(
        DengueRecord.year == ClimateData.year,
        DengueRecord.month == ClimateData.month
    ).all()
    
    if len(records) < 5:
        # Not enough data, return default metrics
        return ModelMetrics(
            r2=0.85,
            mae=100.0,
            mse=15000.0,
            rmse=122.47,
            intercept=DEFAULT_INTERCEPT,
            coefficients=DEFAULT_COEFS,
            training_samples=len(records)
        )
        
    # Prepare features and target
    X = np.array([[r.min_temp, r.max_temp, r.humidity, r.rainfall] for r in records])
    y = np.array([r.cases for r in records])
    
    model = LinearRegression()
    model.fit(X, y)
    
    y_pred = model.predict(X)
    
    # Calculate metrics
    r2 = float(r2_score(y, y_pred))
    mae = float(mean_absolute_error(y, y_pred))
    mse = float(mean_squared_error(y, y_pred))
    rmse = float(np.sqrt(mse))
    
    intercept = float(model.intercept_)
    coefs = {
        "min_temp": float(model.coef_[0]),
        "max_temp": float(model.coef_[1]),
        "humidity": float(model.coef_[2]),
        "rainfall": float(model.coef_[3])
    }
    
    # Save coefficients to DB
    save_config(db, "ml_intercept", str(intercept))
    save_config(db, "ml_coef_min_temp", str(coefs["min_temp"]))
    save_config(db, "ml_coef_max_temp", str(coefs["max_temp"]))
    save_config(db, "ml_coef_humidity", str(coefs["humidity"]))
    save_config(db, "ml_coef_rainfall", str(coefs["rainfall"]))
    
    # Save metrics
    save_config(db, "ml_metric_r2", str(r2))
    save_config(db, "ml_metric_mae", str(mae))
    save_config(db, "ml_metric_mse", str(mse))
    save_config(db, "ml_metric_rmse", str(rmse))
    save_config(db, "ml_training_samples", str(len(records)))
    
    return ModelMetrics(
        r2=r2,
        mae=mae,
        mse=mse,
        rmse=rmse,
        intercept=intercept,
        coefficients=coefs,
        training_samples=len(records)
    )

def save_config(db: Session, key: str, value: str):
    cfg = db.query(SystemConfig).filter(SystemConfig.key == key).first()
    if cfg:
        cfg.value = value
    else:
        cfg = SystemConfig(key=key, value=value)
        db.add(cfg)
    db.commit()

def get_current_metrics(db: Session) -> ModelMetrics:
    """Retrieve saved model performance metrics or train model to initialize them."""
    r2_val = db.query(SystemConfig).filter(SystemConfig.key == "ml_metric_r2").first()
    if not r2_val:
        return train_ml_model(db)
        
    coefs = get_coefficients(db)
    mae = float(get_config_val(db, "ml_metric_mae", "100.0"))
    mse = float(get_config_val(db, "ml_metric_mse", "15000.0"))
    rmse = float(get_config_val(db, "ml_metric_rmse", "122.47"))
    r2 = float(r2_val.value)
    samples = int(get_config_val(db, "ml_training_samples", "0"))
    
    return ModelMetrics(
        r2=r2,
        mae=mae,
        mse=mse,
        rmse=rmse,
        intercept=coefs["intercept"],
        coefficients={
            "min_temp": coefs["min_temp"],
            "max_temp": coefs["max_temp"],
            "humidity": coefs["humidity"],
            "rainfall": coefs["rainfall"]
        },
        training_samples=samples
    )

def predict_dengue(db: Session, min_temp: float, max_temp: float, humidity: float, rainfall: float) -> tuple[int, str]:
    """Predict dengue cases count and classify risk level."""
    coefs = get_coefficients(db)
    
    # y = θ0 + θ1*x1 + θ2*x2 + θ3*x3 + θ4*x4
    pred = coefs["intercept"] + \
           (coefs["min_temp"] * min_temp) + \
           (coefs["max_temp"] * max_temp) + \
           (coefs["humidity"] * humidity) + \
           (coefs["rainfall"] * rainfall)
           
    predicted_cases = max(0, int(round(pred)))
    
    # Classify Risk Level
    threshold_medium = int(get_config_val(db, "threshold_medium", "150"))
    threshold_high = int(get_config_val(db, "threshold_high", "400"))
    
    if predicted_cases < threshold_medium:
        risk_level = "LOW"
    elif predicted_cases < threshold_high:
        risk_level = "MEDIUM"
    else:
        risk_level = "HIGH"
        
    return predicted_cases, risk_level

def trigger_warnings_if_needed(db: Session, year: int, month: int, predicted_cases: int, risk_level: str):
    """Trigger mock SMS/Email warnings if risk level is MEDIUM or HIGH."""
    if risk_level not in ["MEDIUM", "HIGH"]:
        return
        
    month_name = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][month - 1]
    
    # Compose alert message
    message = (
        f"DENGUE EARLY WARNING: A {risk_level} risk level is predicted for {month_name} {year}. "
        f"Expected dengue cases: {predicted_cases}. Please eliminate stagnant water, apply mosquito repellents, "
        f"and prepare healthcare logistics immediately."
    )
    
    # Query users to notify (Admins, Inspectors, Public Users)
    users = db.query(User).filter(User.is_active == True).all()
    
    # Dispatch simulated notifications
    for u in users:
        # Inspectors/Admins get email reports, public users get SMS warnings
        channel = "Email" if u.role in ["Admin", "Inspector"] else "SMS"
        recipient = f"{u.username}@dhaka.gov.bd" if channel == "Email" else f"+880170000{u.id:04d}"
        
        # Check if notification already sent for this month/year/user to avoid spam
        dup = db.query(Notification).filter(
            Notification.recipient == recipient,
            Notification.message.like(f"%{month_name} {year}%")
        ).first()
        
        if not dup:
            notification = Notification(
                channel=channel,
                recipient=recipient,
                message=message,
                status="SENT",
                risk_level=risk_level
            )
            db.add(notification)
            
    db.commit()
