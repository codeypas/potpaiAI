import json
import logging
from typing import Dict, List, Optional
from openai import OpenAI

logger = logging.getLogger(__name__)

class AICodeReviewer:
    """AI-powered code review agent"""
    
    def __init__(self, api_key: str):
        self.client = OpenAI(api_key=api_key)
        self.model = "gpt-4-turbo-preview"
    
    def analyze_code(self, file_content: str, file_name: str) -> Dict:
        """
        Analyze code for issues using AI
        Returns:
        {
            "name": filename,
            "issues": [
                {
                    "type": "style|bug|performance|best_practice",
                    "line": int,
                    "description": str,
                    "suggestion": str
                }
            ]
        }
        """
        try:
            # Properly closed triple-quoted string
            prompt = f"""Analyze the following code file and identify issues.
File: {file_name}

Code:
{file_content}

For each issue, provide:
- type (style, bug, performance, best_practice)
- line number
- description
- suggestion
Return the response in JSON format like this:
{{
    "name": "{file_name}",
    "issues": [
        {{
            "type": "style",
            "line": 1,
            "description": "Example issue",
            "suggestion": "Example suggestion"
        }}
    ]
}}
"""
            # Send prompt to OpenAI API
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0
            )

            # Extract text from response
            content = response.choices[0].message.content
            # Parse JSON safely
            result = json.loads(content)
            return result

        except Exception as e:
            logger.error(f"Error analyzing code: {e}")
            return {"name": file_name, "issues": []}
