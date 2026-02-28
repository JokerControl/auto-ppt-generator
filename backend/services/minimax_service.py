"""
MiniMax API Service - PPT Expert Agent Integration
"""
import json
import hashlib
import time
from typing import Dict, Any, Optional, List
import httpx
from config import settings


class MiniMaxService:
    """MiniMax API Service for PPT generation"""
    
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or settings.MINIMAX_API_KEY
        self.base_url = settings.MINIMAX_BASE_URL
        self.model = settings.MINIMAX_MODEL
        
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    async def chat(
        self, 
        messages: List[Dict[str, str]], 
        temperature: float = 0.7,
        max_tokens: int = 4096
    ) -> Dict[str, Any]:
        """Send chat request to MiniMax"""
        if not self.api_key:
            raise ValueError("MiniMax API key not configured")
        
        async with httpx.AsyncClient(timeout=120.0) as client:
            response = await client.post(
                f"{self.base_url}/text/chatcompletion_v2",
                headers=self._get_headers(),
                json={
                    "model": self.model,
                    "messages": messages,
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            )
            response.raise_for_status()
            return response.json()
    
    async def generate_ppt_outline(
        self, 
        topic: str, 
        pages: int = 10,
        language: str = "zh",
        theme: str = "business"
    ) -> Dict[str, Any]:
        """Generate PPT outline using MiniMax"""
        
        system_prompt = f"""你是一个专业的PPT制作专家和演讲顾问。你的任务是根据用户提供的主题生成一个结构清晰、内容丰富的PPT大纲。

请按照以下要求生成PPT大纲：
1. 生成{pages}页的PPT大纲
2. 使用{language}语言输出
3. 主题风格：{theme}
4. 每页包含：标题、副标题、要点列表

请以JSON格式输出，格式如下：
{{
    "topic": "PPT主题",
    "total_pages": 页数,
    "outline": [
        {{
            "page_num": 1,
            "title": "页面标题",
            "content": "主要内容描述",
            "bullets": ["要点1", "要点2", "要点3"]
        }}
    ]
}}

确保内容专业、逻辑清晰、层次分明。"""

        user_message = f"请为以下主题生成PPT大纲：\n主题：{topic}\n要求：{pages}页，{theme}风格，{language}语言"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = await self.chat(messages)
        
        # Parse the response
        try:
            content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
            # Try to extract JSON from the response
            json_start = content.find("{")
            json_end = content.rfind("}") + 1
            if json_start >= 0 and json_end > json_start:
                json_str = content[json_start:json_end]
                return json.loads(json_str)
            else:
                raise ValueError("No JSON found in response")
        except Exception as e:
            # Return mock data if parsing fails
            return self._generate_mock_outline(topic, pages, language)
    
    async def generate_ppt_content(
        self,
        page_title: str,
        page_content: str,
        bullets: List[str],
        theme: str = "business"
    ) -> Dict[str, Any]:
        """Generate detailed content for a single PPT slide"""
        
        system_prompt = f"""你是一个专业的PPT内容生成专家。根据提供的大纲内容，生成详细的PPT页面内容。

主题风格：{theme}
请为每个要点生成详细的解释文本，保持简洁专业。"""

        user_message = f"""页面标题：{page_title}
主要内容：{page_content}
要点列表：{', '.join(bullets)}

请为每个要点生成2-3句话的详细解释。"""

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ]

        response = await self.chat(messages, temperature=0.5)
        content = response.get("choices", [{}])[0].get("message", {}).get("content", "")
        
        return {
            "title": page_title,
            "content": page_content,
            "bullets": bullets,
            "detailed_content": content
        }
    
    def _generate_mock_outline(
        self, 
        topic: str, 
        pages: int, 
        language: str
    ) -> Dict[str, Any]:
        """Generate mock outline when API is not available"""
        
        outline = []
        for i in range(1, pages + 1):
            outline.append({
                "page_num": i,
                "title": f"第{i}页标题",
                "content": f"这是关于{topic}的第{i}页内容",
                "bullets": [
                    f"要点{i}-1: 重要信息",
                    f"要点{i}-2: 关键数据",
                    f"要点{i}-3: 结论建议"
                ]
            })
        
        return {
            "topic": topic,
            "total_pages": pages,
            "outline": outline
        }


# Singleton instance
minimax_service = MiniMaxService()
