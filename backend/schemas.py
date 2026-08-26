from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

# Token Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    username: str
    role: str

class TokenData(BaseModel):
    username: Optional[str] = None
    role: Optional[str] = None

# User Schemas
class UserBase(BaseModel):
    username: str

class UserCreate(UserBase):
    password: str
    role: Optional[str] = "Public" # Public, Inspector, Admin

class UserResponse(UserBase):
    id: int
    role: str
    is_active: bool

    class Config:
        from_attributes = True

# Climate Data Schemas
class ClimateDataBase(BaseModel):
    year: int
    month: int
    min_temp: float
    max_temp: float
    humidity: float
    rainfall: float
    location: str = "Dhaka"

class ClimateDataCreate(ClimateDataBase):
    pass

class ClimateDataResponse(ClimateDataBase):
    id: int

    class Config:
        from_attributes = True

# Dengue Record Schemas
class DengueRecordBase(BaseModel):
    year: int
    month: int
    cases: int
    location: Optional[str] = "Dhaka"

class DengueRecordCreate(DengueRecordBase):
    pass

class DengueRecordResponse(DengueRecordBase):
    id: int

    class Config:
        from_attributes = True

# Prediction Schemas
class PredictionResponse(BaseModel):
    id: int
    year: int
    month: int
    predicted_cases: int
    risk_level: str
    location: str
    created_at: datetime

    class Config:
        from_attributes = True

# Notification Schemas
class NotificationResponse(BaseModel):
    id: int
    timestamp: datetime
    channel: str
    recipient: str
    message: str
    status: str
    risk_level: str

    class Config:
        from_attributes = True

# Audit Log Schemas
class AuditLogResponse(BaseModel):
    id: int
    timestamp: datetime
    username: str
    action: str
    details: str

    class Config:
        from_attributes = True

# Configuration Schemas
class SystemConfigResponse(BaseModel):
    key: str
    value: str

    class Config:
        from_attributes = True

class SystemConfigUpdate(BaseModel):
    value: str

# Model Metrics Schema
class ModelMetrics(BaseModel):
    r2: float
    mae: float
    mse: float
    rmse: float
    intercept: float
    coefficients: dict
    training_samples: int
