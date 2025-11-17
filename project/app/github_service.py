import requests
import logging
from typing import List, Dict, Any
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self, github_token: str = None):
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.base_url = "https://api.github.com"
        self.session = requests.Session()
        if self.github_token:
            self.session.headers.update({
                "Authorization": f"token {self.github_token}",
                "Accept": "application/vnd.github.v3+json"
            })
    
    def _parse_repo_url(self, repo_url: str) -> tuple:
        """Parse GitHub repo URL to extract owner and repo"""
        if "github.com" not in repo_url:
            raise ValueError("Invalid GitHub URL")
        
        # Remove .git if present
        repo_url = repo_url.rstrip("/").replace(".git", "")
        
        # Extract owner and repo
        parts = repo_url.split("/")
        owner = parts[-2]
        repo = parts[-1]
        
        return owner, repo
    
    def get_pr_files(self, repo_url: str, pr_number: int) -> List[Dict[str, Any]]:
        """Get list of changed files in a PR"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            files = response.json()
            logger.info(f"Fetched {len(files)} files from PR #{pr_number}")
            return files
        except Exception as e:
            logger.error(f"Error fetching PR files: {str(e)}")
            raise
    
    def get_file_content(self, repo_url: str, file_path: str, ref: str = "HEAD") -> str:
        """Get raw file content from repository"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            # GitHub API returns base64 encoded content
            import base64
            content = base64.b64decode(response.json()["content"]).decode("utf-8")
            return content
        except Exception as e:
            logger.error(f"Error fetching file content: {str(e)}")
            raise
    
    def get_pr_metadata(self, repo_url: str, pr_number: int) -> Dict[str, Any]:
        """Get PR metadata"""
        try:
            owner, repo = self._parse_repo_url(repo_url)
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            
            response = self.session.get(url)
            response.raise_for_status()
            
            pr_data = response.json()
            return {
                "title": pr_data.get("title"),
                "description": pr_data.get("body"),
                "author": pr_data.get("user", {}).get("login"),
                "state": pr_data.get("state"),
                "created_at": pr_data.get("created_at"),
                "updated_at": pr_data.get("updated_at")
            }
        except Exception as e:
            logger.error(f"Error fetching PR metadata: {str(e)}")
            raise
