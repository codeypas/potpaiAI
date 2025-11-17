import requests
from typing import Optional, Dict, List
import logging

logger = logging.getLogger(__name__)

class GitHubService:
    """Service to interact with GitHub API"""
    
    def __init__(self, token: Optional[str] = None):
        self.token = token
        self.base_url = "https://api.github.com"
        self.headers = self._get_headers()
    
    def _get_headers(self) -> Dict:
        """Get request headers"""
        headers = {"Accept": "application/vnd.github.v3+json"}
        if self.token:
            headers["Authorization"] = f"token {self.token}"
        return headers
    
    def get_pr_files(self, repo_url: str, pr_number: int) -> List[Dict]:
        """Get PR files and changes"""
        try:
            # Extract owner and repo from URL
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
            
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}/files"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            logger.info(f"Retrieved {len(response.json())} files for PR #{pr_number}")
            return response.json()
        except Exception as e:
            logger.error(f"Error fetching PR files: {str(e)}")
            return []
    
    def get_file_content(self, repo_url: str, ref: str, file_path: str) -> Optional[str]:
        """Get file content from GitHub"""
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
            
            url = f"{self.base_url}/repos/{owner}/{repo}/contents/{file_path}?ref={ref}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            import base64
            content = base64.b64decode(response.json()['content']).decode('utf-8')
            return content
        except Exception as e:
            logger.error(f"Error fetching file content: {str(e)}")
            return None
    
    def get_pr_diff(self, repo_url: str, pr_number: int) -> Optional[str]:
        """Get full PR diff"""
        try:
            parts = repo_url.rstrip('/').split('/')
            owner, repo = parts[-2], parts[-1]
            
            url = f"{self.base_url}/repos/{owner}/{repo}/pulls/{pr_number}"
            headers = self.headers.copy()
            headers["Accept"] = "application/vnd.github.v3.diff"
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            
            return response.text
        except Exception as e:
            logger.error(f"Error fetching PR diff: {str(e)}")
            return None
