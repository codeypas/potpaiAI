# PotPieAI Code Review System

An autonomous AI agent system that analyzes GitHub pull requests asynchronously.

---

## Features

- ✅ Analyze GitHub PRs via API  
- ✅ AI-powered code review (style, bugs, performance, best practices)  
- ✅ Asynchronous task processing with Celery  
- ✅ Task status tracking and result retrieval  
- ✅ Multiple programming language support  
- ✅ Structured JSON API responses  

---

## Quick Start

```bash
# 1. Clone the project
git clone https://github.com/yourusername/PotPieAI.git
cd PotPieAI

# 2. Create virtual environment
python -m venv venv

# 3. Activate environment
# macOS/Linux:
source venv/bin/activate
# Windows:
venv\Scripts\activate

# 4. Install dependencies
pip install -r requirements.txt

# 5. Create .env file with API keys and GitHub token
# Example:
# OPENAI_API_KEY=your_openai_key
# GITHUB_TOKEN=your_github_pat

# 6. Set up MySQL database

# 7. Start Redis server
redis-server

# 8. Start Celery worker in Terminal 1
celery -A app.tasks worker --loglevel=info

# 9. Start FastAPI server in Terminal 2
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 10. Test API
python test_api.py

```

---

## API Endpoints

- `POST /analyze-pr` - Queue PR for analysis  
- `GET /status/<task_id>` - Check task status  
- `GET /results/<task_id>` - Get analysis results  
- `GET /tasks` - List recent tasks  
- `GET /health` - Health check  


---

## Testing Steps

**1. Queue PR for analysis**  

```bash
curl -X POST "http://localhost:8000/analyze-pr" \
-H "Content-Type: application/json" \
-d '{
    "repo_url": "https://github.com/torvalds/linux",
    "pr_number": 1,
    "github_token": "your_github_token"
}'


```

**2. Check task status**
```bash
curl "http://localhost:8000/status/<task_id>"
```

**3. Get analysis results (after 60–120 seconds)**
```bash
curl "http://localhost:8000/results/<task_id>"
```

Expected result format: JSON with file issues, summary, and suggestions.
---


## Expected Output Format

```bash
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
    },
    "error_message": null
}
```
---

## Dashboard and API  Docs

**Dashboard:** http://localhost:8000
---
<img src="https://raw.githubusercontent.com/codeypas/potpieAI/main/images/2%20UI.png" width="40%" alt="Dashboard Screenshot" />
- Displays tasks, statistics, and results

**API Docs:** http://localhost:8000/docs
---
<img src="https://raw.githubusercontent.com/codeypas/potpieAI/main/images/1%20docs.png" width="40%" alt="API Docs Screenshot" />
- Swagger UI  Only shows API endpoints

---
## 📫 Contact

Got feedback or want to connect?

📌 [GitHub Profile](https://github.com/codeypas)  
📧 Contact: bjbestintheworld@gmail.com  
