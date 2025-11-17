import logging
from celery import Celery
from dotenv import load_dotenv
import os
import json
from datetime import datetime
from sqlalchemy.orm import Session

load_dotenv()

# Initialize Celery
celery_app = Celery(
    "code_review",
    broker=os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0"),
    backend=os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60, 
)

logger = logging.getLogger(__name__)

@celery_app.task(bind=True, name="analyze_pr_task")
def analyze_pr_task(self, task_id: str, repo_url: str, pr_number: int, github_token: str = None):
    """Celery task to analyze PR asynchronously"""
    try:
        from app.database import SessionLocal
        from app.models import CodeReviewTask, TaskStatus
        from app.github_service import GitHubService
        from app.ai_reviewer import AICodeReviewer
        
        db = SessionLocal()
        
        task = db.query(CodeReviewTask).filter_by(task_id=task_id).first()
        task.status = TaskStatus.PROCESSING
        task.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Processing task {task_id}")
        
        gh_service = GitHubService(github_token)
        pr_files = gh_service.get_pr_files(repo_url, pr_number)
        
        pr_metadata = gh_service.get_pr_metadata(repo_url, pr_number)
        
        reviewer = AICodeReviewer()
        results = reviewer.review_pr_files(pr_files)
        
        final_result = {
            "task_id": task_id,
            "status": "completed",
            "pr_metadata": pr_metadata,
            "results": results
        }
        
        task.status = TaskStatus.COMPLETED
        task.result = json.dumps(final_result)
        task.updated_at = datetime.utcnow()
        db.commit()
        
        logger.info(f"Task {task_id} completed successfully")
        
        return final_result
        
    except Exception as e:
        logger.error(f"Error in analyze_pr_task: {str(e)}")
        
        try:
            db = SessionLocal()
            task = db.query(CodeReviewTask).filter_by(task_id=task_id).first()
            if task:
                task.status = TaskStatus.FAILED
                task.error_message = str(e)
                task.updated_at = datetime.utcnow()
                db.commit()
        except:
            pass
        
        raise
