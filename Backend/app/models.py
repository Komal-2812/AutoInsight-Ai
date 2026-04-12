from sqlalchemy import Column, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
import uuid
from datetime import datetime

def gen_uuid():
    return str(uuid.uuid4())

class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, default=gen_uuid)
    email = Column(String, unique=True, nullable=False, index=True)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=True)
    is_verified = Column(Boolean, default=False)
    verification_token = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    datasets = relationship("Dataset", back_populates="owner", cascade="all, delete")

class Dataset(Base):
    __tablename__ = "datasets"
    id = Column(String, primary_key=True, default=gen_uuid)
    user_id = Column(String, ForeignKey("users.id"), nullable=False)
    file_name = Column(String, nullable=False)
    original_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_size = Column(String, nullable=True)
    row_count = Column(String, nullable=True)
    column_count = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    owner = relationship("User", back_populates="datasets")
    
class Analysis(Base):
    __tablename__ = "analysis"

    id = Column(String, primary_key=True, default=gen_uuid)

    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    user_id    = Column(String, ForeignKey("users.id"), nullable=False)

    status = Column(String, default="pending")  # pending | running | completed | failed

    result_path = Column(String, nullable=True)
    error       = Column(Text, nullable=True)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # relationships (optional but good)
    dataset = relationship("Dataset")
    user    = relationship("User")