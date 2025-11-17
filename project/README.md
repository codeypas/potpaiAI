# AI Code Review System

An autonomous agent system that uses AI to analyze GitHub pull requests with asynchronous processing.

## Features

- ✅ GitHub PR Analysis via API
- ✅ AI-powered code review (style, bugs, performance, best practices)
- ✅ Asynchronous task processing with Celery
- ✅ Task status tracking and result retrieval
- ✅ Multiple programming language support
- ✅ Structured JSON API responses

## Expected Output Format

\`\`\`json
{
    "task_id": "abc123",
    "status": "completed",
    "results": {
        "files": [
            {
                "name": "main.py",
                "issues": [
                    {
                        "type": "style",
                        "line": 15,
                        "description": "Line too long",
                        "suggestion": "Break line into multiple lines"
                    }
                ]
            }
        ],
        "summary": {
            "total_files": 1,
            "total_issues": 2,
            "critical_issues": 1
        }
    }
}
\`\`\`

## Quick Start

1. Clone/Extract project
2. Create virtual environment: `python -m venv venv`
3. Activate: `source venv/bin/activate`
4. Install dependencies: `pip install -r requirements.txt`
5. Create `.env` file with API keys
6. Set up MySQL database
7. Start Redis server
8. Start Celery worker in Terminal 1
9. Start FastAPI in Terminal 2
10. Test with `python test_api.py`

## API Endpoints

- `POST /analyze-pr` - Queue PR for analysis
- `GET /status/<task_id>` - Check task status
- `GET /results/<task_id>` - Get analysis results
- `GET /tasks` - List recent tasks
- `GET /health` - Health check

## Documentation

Access Swagger UI at: http://localhost:8000/docs
