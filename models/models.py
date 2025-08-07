from sqlalchemy import Column, Integer, String, Float, DateTime
from db.database import Base
from datetime import datetime, UTC


class MathRequest(Base):
    __tablename__ = "math_requests"
    id = Column(Integer, primary_key=True, index=True)
    operation = Column(String, index=True)
    param1 = Column(Float, nullable=True)
    param2 = Column(Float, nullable=True)
    result = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))


class LogEntry(Base):
    __tablename__ = "log_entries"
    id = Column(Integer, primary_key=True, index=True)
    level = Column(String)
    message = Column(String)
    timestamp = Column(DateTime, default=lambda: datetime.now(UTC))


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default="user")
