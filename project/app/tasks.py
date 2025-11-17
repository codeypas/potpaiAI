from celery import Celery
from app.config import settings
from app.github_service import GitHubService
from app.ai_reviewer import AICodeReviewer
from app.database import SessionLocal
from app.models import CodeReviewTask
import json
import logging

logger = logging.getLogger(__name__)

# Configure Celery
celery_app = Celery(
    'code_review_system',
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)

@celery_app.task(bind=True, name='analyze_github_pr')
def analyze_github_pr(self, task_id: str, repo_url: str, pr_number: int, github_token: str = None):
    """
    Celery task: Analyze GitHub PR
    Updates task status in database
    """
    db = SessionLocal()
    
    try:
        # Update status to processing
        task = db.query(CodeReviewTask).filter(CodeReviewTask.task_id == task_id).first()
        if task:
            task.status = "processing"
            db.commit()
        
        logger.info(f"Starting analysis for PR: {repo_url}#{pr_number}")
        
        # Fetch PR files
        gh_service = GitHubService(github_token)
        pr_files = gh_service.get_pr_files(repo_url, pr_number)
        
        if not pr_files:
            raise Exception("No files found in PR")
        
        # Get file contents
        file_contents = {}
        for file_data in pr_files[:10]:  # Limit to 10 files
            file_name = file_data.get("filename", "")
            if AICodeReviewer._is_code_file(file_name):
                content = gh_service.get_file_content(repo_url, f"pull/{pr_number}/head", file_name)
                if content:
                    file_contents[file_name] = content
        
        logger.info(f"Retrieved content for {len(file_contents)} files")
        
        # Run AI analysis
        if not settings.OPENAI_API_KEY:
            raise Exception("OPENAI_API_KEY not configured")
        
        ai_reviewer = AICodeReviewer(settings.OPENAI_API_KEY)
        analysis_results = ai_reviewer.analyze_pr(pr_files, file_contents)
        
        # Update task with results
        task = db.query(CodeReviewTask).filter(CodeReviewTask.task_id == task_id).first()
        if task:
            task.status = "completed"
            task.results = json.dumps(analysis_results)
            db.commit()
        
        logger.info(f"Analysis completed for task {task_id}")
        return analysis_results
    
    except Exception as e:
        logger.error(f"Error in task {task_id}: {str(e)}")
        task = db.query(CodeReviewTask).filter(CodeReviewTask.task_id == task_id).first()
        if task:
            task.status = "failed"
            task.error_message = str(e)
            db.commit()
        raise
    
    finally:
        db.close()
