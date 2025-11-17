import logging
from typing import List, Dict, Any
import json
from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

logger = logging.getLogger(__name__)

class AICodeReviewer:
    def __init__(self):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"
    
    def analyze_code(self, file_name: str, file_content: str, diff: str = None) -> Dict[str, Any]:
        """Analyze code file using OpenAI and return structured review"""
        try:
            prompt = self._build_prompt(file_name, file_content, diff)
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert code reviewer. Analyze code and return ONLY valid JSON output."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.3,
                max_tokens=2000
            )
            
            response_text = response.choices[0].message.content.strip()
            
            import re
            json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response_text)
            
            return result
        except json.JSONDecodeError:
            logger.error(f"Failed to parse JSON response for {file_name}")
            return {"issues": []}
        except Exception as e:
            logger.error(f"Error analyzing code: {str(e)}")
            raise
    
    def _build_prompt(self, file_name: str, file_content: str, diff: str = None) -> str:
        """Build prompt for code review"""
        prompt = f"""
Analyze the following code file for issues and return ONLY a valid JSON object.

File: {file_name}

{f"Diff:" if diff else ""}
{diff if diff else ""}

Code:
{file_content[:5000]}  # Limit to first 5000 chars

Return ONLY this JSON structure (no markdown, no extra text):
{{
    "issues": [
        {{
            "type": "style|bug|performance|best_practice",
            "line": <line number>,
            "description": "Issue description",
            "suggestion": "How to fix"
        }}
    ]
}}

Focus on:
1. Style issues (formatting, naming conventions)
2. Bugs (null checks, error handling, logic errors)
3. Performance issues (inefficient algorithms, memory leaks)
4. Best practices (design patterns, security)

Be concise. Return only the JSON.
"""
        return prompt
    
    def review_pr_files(self, files_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Review all files in PR and return summary"""
        files_reviews = []
        total_issues = 0
        critical_issues = 0
        
        for file_info in files_data:
            if file_info["filename"].endswith((".md", ".txt", ".json", ".yaml", ".yml")):
                continue
            
            try:
                file_content = file_info.get("patch", "")
                if not file_content:
                    continue
                
                review = self.analyze_code(
                    file_info["filename"],
                    file_info.get("raw", ""),
                    file_content
                )
                
                issues = review.get("issues", [])
                
                file_review = {
                    "name": file_info["filename"],
                    "issues": issues
                }
                
                files_reviews.append(file_review)
                
                total_issues += len(issues)
                critical_issues += sum(1 for issue in issues if issue.get("type") == "bug")
                
            except Exception as e:
                logger.error(f"Error reviewing file {file_info['filename']}: {str(e)}")
                continue
        
        return {
            "files": files_reviews,
            "summary": {
                "total_files": len(files_reviews),
                "total_issues": total_issues,
                "critical_issues": critical_issues
            }
        }
