"""
Data models for AutoPPT Generator
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class PPTTheme(str, Enum):
    """PPT主题风格"""
    BUSINESS = "business"
    EDUCATION = "education"
    CREATIVE = "creative"
    MINIMAL = "minimal"
    TECH = "tech"


class PPTLanguage(str, Enum):
    """PPT语言"""
    CHINESE = "zh"
    ENGLISH = "en"


class TaskStatus(str, Enum):
    """任务状态"""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


# Request models
class PPTGenerateRequest(BaseModel):
    """PPT生成请求 - 适配前端字段"""
    topic: str = Field(..., description="PPT主题/标题")
    description: str = Field(default="", description="详细描述或大纲要求")
    page_count: int = Field(default=10, ge=5, le=50, description="页数")
    style: str = Field(default="modern", description="风格: modern/business/creative/tech/education/elegant")
    language: str = Field(default="zh-CN", description="语言: zh-CN/en-US")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "人工智能在教育中的应用",
                "description": "包括AI辅导、个性化学习、智能评估等方面",
                "page_count": 15,
                "style": "education",
                "language": "zh-CN"
            }
        }


class PPTOutlineRequest(BaseModel):
    """PPT大纲生成请求"""
    topic: str = Field(..., description="PPT主题")
    pages: int = Field(default=10, ge=5, le=50)
    language: PPTLanguage = PPTLanguage.CHINESE


# Response models
class PPTOutlineItem(BaseModel):
    """PPT大纲项"""
    page_num: int
    title: str
    content: str
    bullets: List[str] = []


class PPTOutlineResponse(BaseModel):
    """PPT大纲响应"""
    topic: str
    total_pages: int
    outline: List[PPTOutlineItem]
    theme: PPTTheme
    language: PPTLanguage


class PPTGenerateResponse(BaseModel):
    """PPT生成响应"""
    task_id: str
    status: TaskStatus
    message: str
    file_url: Optional[str] = None
    preview_data: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """任务状态查询响应"""
    task_id: str
    status: TaskStatus
    message: str
    file_url: Optional[str] = None
    created_at: datetime
    completed_at: Optional[datetime] = None


# MCP Skill models
class MCPSkillInput(BaseModel):
    """MCP技能输入"""
    skill_name: str
    parameters: Dict[str, Any]


class MCPSkillResult(BaseModel):
    """MCP技能结果"""
    skill_name: str
    success: bool
    result: Dict[str, Any]
    error: Optional[str] = None
