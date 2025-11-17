from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from pydantic import BaseModel
import logging
import uuid
from datetime import datetime

from app.database import get_db, init_db
from app.models import CodeReviewTask, TaskStatus
from app.tasks import analyze_pr_task


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI Code Review System",
    description="Autonomous AI-powered code review for GitHub PRs",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def startup():
    init_db()
    logger.info("Database initialized")

class AnalyzePRRequest(BaseModel):
    repo_url: str
    pr_number: int
    github_token: str = None

class TaskResponse(BaseModel):
    task_id: str
    status: str
    message: str

class StatusResponse(BaseModel):
    task_id: str
    status: str
    created_at: str
    updated_at: str

class ResultResponse(BaseModel):
    task_id: str
    status: str
    results: dict = None
    error_message: str = None

# Routes
@app.get("/health", tags=["Health"])
def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "service": "AI Code Review System",
        "version": "1.0.0"
    }

@app.post("/analyze-pr", response_model=TaskResponse, tags=["Analysis"])
def analyze_pr(request: AnalyzePRRequest, db: Session = Depends(get_db)):
    """
    Queue a PR for analysis
    """
    task_id = str(uuid.uuid4())

    task = CodeReviewTask(
        id=task_id,
        repo_url=request.repo_url,
        pr_number=request.pr_number,
        status=TaskStatus.PENDING,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    celery_task = analyze_pr_task.delay(task_id, request.repo_url, request.pr_number, request.github_token)
    logger.info(f"Queued PR analysis task: {task_id} (Celery ID: {celery_task.id})")

    return TaskResponse(
        task_id=task_id,
        status=task.status.value,
        message="PR analysis has been queued"
    )

@app.get("/task-status/{task_id}", response_model=StatusResponse, tags=["Analysis"])
def get_task_status(task_id: str, db: Session = Depends(get_db)):
    """
    Get the current status of a queued task
    """
    task = db.query(CodeReviewTask).filter(CodeReviewTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    return StatusResponse(
        task_id=task.id,
        status=task.status.value,
        created_at=task.created_at.isoformat(),
        updated_at=(task.updated_at.isoformat() if task.updated_at else "")
    )

@app.get("/task-result/{task_id}", response_model=ResultResponse, tags=["Analysis"])
def get_task_result(task_id: str, db: Session = Depends(get_db)):
    """
    Get the results of a completed task
    """
    task = db.query(CodeReviewTask).filter(CodeReviewTask.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    if task.status == TaskStatus.COMPLETED:
        return ResultResponse(
            task_id=task.id,
            status=task.status.value,
            results=task.results
        )
    elif task.status == TaskStatus.FAILED:
        return ResultResponse(
            task_id=task.id,
            status=task.status.value,
            error_message=task.error_message
        )
    else:
        return ResultResponse(
            task_id=task.id,
            status=task.status.value,
            error_message="Task is still processing"
        )
