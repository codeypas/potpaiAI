from sqlalchemy import Column, String, Text, DateTime, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum
import json

Base = declarative_base()

class TaskStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class CodeReviewTask(Base):
    __tablename__ = "code_review_tasks"
    
    task_id = Column(String(100), primary_key=True, index=True)
    repo_url = Column(String(500), nullable=False)
    pr_number = Column(String(50), nullable=False)
    status = Column(SQLEnum(TaskStatus), default=TaskStatus.PENDING, index=True)
    result = Column(Text, nullable=True)  # Stores JSON result
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        result_data = None
        if self.result:
            result_data = json.loads(self.result)
        return {
            "task_id": self.task_id,
            "repo_url": self.repo_url,
            "pr_number": self.pr_number,
            "status": self.status.value,
            "result": result_data,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat()
        }
