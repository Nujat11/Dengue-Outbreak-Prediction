from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, func
from .database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role = Column(String(50), default="Public", nullable=False) # Admin, Inspector, Public
    is_active = Column(Boolean, default=True, nullable=False)

class ClimateData(Base):
    __tablename__ = "climate_data"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    min_temp = Column(Float, nullable=False)
    max_temp = Column(Float, nullable=False)
    humidity = Column(Float, nullable=False)
    rainfall = Column(Float, nullable=False)

class DengueRecord(Base):
    __tablename__ = "dengue_records"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    cases = Column(Integer, nullable=False)
    location = Column(String(100), default="Dhaka", nullable=False)

class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True, index=True)
    year = Column(Integer, nullable=False)
    month = Column(Integer, nullable=False)
    predicted_cases = Column(Integer, nullable=False)
    risk_level = Column(String(50), nullable=False) # Low, Medium, High
    location = Column(String(100), default="Dhaka", nullable=False)
    created_at = Column(DateTime, server_default=func.now(), nullable=False)

class Notification(Base):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    channel = Column(String(50), nullable=False) # SMS, Email
    recipient = Column(String(100), nullable=False)
    message = Column(Text, nullable=False)
    status = Column(String(50), default="SENT", nullable=False) # SENT, FAILED
    risk_level = Column(String(50), nullable=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, server_default=func.now(), nullable=False)
    username = Column(String(100), nullable=False)
    action = Column(String(100), nullable=False)
    details = Column(Text, nullable=False)

class SystemConfig(Base):
    __tablename__ = "system_configs"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, index=True, nullable=False)
    value = Column(String(255), nullable=False)
