from sqlalchemy import Column, String, DateTime, Text
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class CodeReviewTask(Base):
    __tablename__ = "code_review_tasks"
    
    task_id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    repo_url = Column(String(255), nullable=False)
    pr_number = Column(String(50), nullable=False)
    status = Column(String(50), default="pending")  # pending, processing, completed, failed
    results = Column(Text, nullable=True)  # JSON string
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
