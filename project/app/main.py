from typing import Optional
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import json
import logging
from datetime import datetime

from app.database import get_db, init_db
from app.models import CodeReviewTask
from app.tasks import analyze_github_pr, celery_app
from app.config import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="AI Code Review System",
    description="Autonomous agent for analyzing GitHub pull requests",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup():
    init_db()
    logger.info("Database initialized")

# Request/Response Models
class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: Optional[str] = None

class TaskStatus(BaseModel):
    task_id: str
    status: str
    created_at: datetime
    updated_at: datetime

class TaskResult(BaseModel):
    task_id: str
    status: str
    results: dict = None
    error_message: str = None

# Endpoints
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AI Code Review System",
        "version": "1.0.0",
        "environment": settings.ENVIRONMENT
    }

@app.post("/analyze-pr")
async def analyze_pr(request: AnalyzePRRequest, db: Session = Depends(get_db)):
    """
    Queue a PR for analysis
    
    Returns:
    {
        "task_id": "uuid",
        "status": "pending",
        "message": "PR analysis queued successfully"
    }
    """
    try:
        # Validate repo URL
        if "github.com" not in request.repo_url:
            raise HTTPException(status_code=400, detail="Invalid GitHub repository URL")
        
        logger.info(f"Queuing analysis for {request.repo_url}#{request.pr_number}")
        
        # Create task in database
        task = CodeReviewTask(
            repo_url=request.repo_url,
            pr_number=str(request.pr_number),
            status="pending"
        )
        db.add(task)
        db.commit()
        db.refresh(task)
        
        # Queue Celery task
        analyze_github_pr.delay(
            task.task_id,
            request.repo_url,
            request.pr_number,
            request.github_token
        )
        
        return {
            "task_id": task.task_id,
            "status": "pending",
            "message": "PR analysis queued successfully"
        }
    
    except Exception as e:
        logger.error(f"Error queuing PR analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/status/{task_id}")
async def get_status(task_id: str, db: Session = Depends(get_db)):
    """
    Get status of an analysis task
    
    Returns:
    {
        "task_id": "uuid",
        "status": "pending|processing|completed|failed",
        "created_at": "timestamp",
        "updated_at": "timestamp"
    }
    """
    task = db.query(CodeReviewTask).filter(CodeReviewTask.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    return {
        "task_id": task.task_id,
        "status": task.status,
        "created_at": task.created_at,
        "updated_at": task.updated_at
    }

@app.get("/results/{task_id}")
async def get_results(task_id: str, db: Session = Depends(get_db)):
    """
    Get analysis results for a completed task
    
    Returns:
    {
        "task_id": "uuid",
        "status": "completed|failed|pending",
        "results": {
            "files": [...],
            "summary": {...}
        },
        "error_message": null
    }
    """
    task = db.query(CodeReviewTask).filter(CodeReviewTask.task_id == task_id).first()
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    result = {
        "task_id": task.task_id,
        "status": task.status,
        "error_message": task.error_message
    }
    
    if task.results:
        result["results"] = json.loads(task.results)
    
    return result

@app.get("/tasks")
async def list_tasks(db: Session = Depends(get_db), limit: int = 10):
    """
    List recent tasks
    
    Returns: List of tasks with their status
    """
    tasks = db.query(CodeReviewTask).order_by(CodeReviewTask.created_at.desc()).limit(limit).all()
    
    return [
        {
            "task_id": task.task_id,
            "repo_url": task.repo_url,
            "pr_number": task.pr_number,
            "status": task.status,
            "created_at": task.created_at,
            "updated_at": task.updated_at
        }
        for task in tasks
    ]

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API documentation link"""
    return {
        "message": "AI Code Review System API",
        "documentation": "http://localhost:8000/docs",
        "status": "running"
    }
