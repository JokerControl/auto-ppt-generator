"""
PPT Generation API Routes
API v1 version - compatible with frontend
"""
import os
from typing import List
from pathlib import Path

from fastapi import APIRouter, HTTPException, BackgroundTasks, Query
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from models.schemas import (
    PPTGenerateRequest,
    PPTGenerateResponse,
    PPTOutlineRequest,
    PPTOutlineResponse,
    PPTOutlineItem,
    TaskStatusResponse,
    TaskStatus,
    MCPSkillInput,
    MCPSkillResult,
    PPTTheme,
    PPTLanguage
)
from services.task_manager import task_manager
from services.minimax_service import minimax_service
from mcp.skills import mcp_registry
from config import settings


router = APIRouter(prefix="/api/v1/ppt", tags=["PPT Generation v1"])


# Field mapping for frontend compatibility
STYLE_TO_THEME = {
    "modern": "minimal",
    "business": "business",
    "creative": "creative",
    "tech": "tech",
    "education": "education",
    "elegant": "minimal"
}

LANGUAGE_MAP = {
    "zh-CN": "zh",
    "en-US": "en",
    "zh": "zh",
    "en": "en"
}


@router.get("/")
async def root():
    """API root endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@router.post("/generate")
async def generate_ppt(
    request: dict,
    background_tasks: BackgroundTasks
):
    """
    Generate PPT file asynchronously
    Compatible with frontend request format
    """
    try:
        # Check if MiniMax API is configured
        if not settings.MINIMAX_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="MiniMax API key not configured. Please set MINIMAX_API_KEY environment variable."
            )
        
        # Map frontend fields to backend
        topic = request.get("topic", "")
        page_count = request.get("page_count", 10)
        style = request.get("style", "modern")
        language = request.get("language", "zh-CN")
        
        # Convert to internal format
        theme = STYLE_TO_THEME.get(style, "business")
        lang_code = LANGUAGE_MAP.get(language, "zh")
        
        # Create task
        task = await task_manager.create_task(
            topic=topic,
            description="",
            pages=page_count,
            theme=theme,
            language=lang_code
        )
        
        # Process in background
        background_tasks.add_task(task_manager.process_task, task.task_id)
        
        return {
            "task_id": task.task_id,
            "status": task.status.value,
            "message": "PPT generation started"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/status/{task_id}")
async def get_task_status(task_id: str):
    """Get the status of a PPT generation task"""
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    response = {
        "task_id": task.task_id,
        "status": task.status.value,
        "message": task.message,
        "created_at": task.created_at.isoformat() if task.created_at else None,
    }
    
    if task.status == TaskStatus.COMPLETED:
        response["download_url"] = task.file_url
        response["preview"] = {
            "pages": [
                {
                    "page_number": p.get("page_num", i+1),
                    "title": p.get("title", ""),
                    "content": p.get("content", ""),
                    "bullets": p.get("bullets", [])
                }
                for i, p in enumerate(task.outline)
            ]
        }
    
    if task.status == TaskStatus.FAILED:
        response["error"] = task.error
    
    return response


@router.get("/download/{task_id}")
async def download_ppt(task_id: str):
    """Download generated PPT file by task_id"""
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    if not task.file_url:
        raise HTTPException(status_code=404, detail="File not ready")
    
    filename = task.file_url.split("/")[-1]
    filepath = Path(settings.OUTPUT_DIR) / filename
    
    if not filepath.exists():
        raise HTTPException(status_code=404, detail="File not found")
    
    return FileResponse(
        path=str(filepath),
        filename=f"{task.topic}.pptx",
        media_type="application/vnd.openxmlformats-officedocument.presentationml.presentation"
    )


@router.get("/tasks")
async def list_tasks(limit: int = Query(default=20, le=100)):
    """List all generation tasks"""
    tasks = await task_manager.list_tasks(limit)
    
    return {
        "total": len(tasks),
        "tasks": [
            {
                "task_id": t.task_id,
                "topic": t.topic,
                "status": t.status.value,
                "created_at": t.created_at.isoformat(),
                "completed_at": t.completed_at.isoformat() if t.completed_at else None
            }
            for t in tasks
        ]
    }


@router.delete("/task/{task_id}")
async def delete_task(task_id: str):
    """Delete a task and its generated file"""
    task = await task_manager.get_task(task_id)
    
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    
    # Delete file if exists
    if task.file_url:
        filename = task.file_url.split("/")[-1]
        filepath = Path(settings.OUTPUT_DIR) / filename
        if filepath.exists():
            filepath.unlink()
    
    # Delete task
    await task_manager.delete_task(task_id)
    
    return {"message": "Task deleted successfully"}


# Legacy routes for backward compatibility
@router.post("/outline", response_model=PPTOutlineResponse)
async def generate_outline(request: PPTOutlineRequest):
    """Generate PPT outline (legacy)"""
    try:
        if not settings.MINIMAX_API_KEY:
            raise HTTPException(
                status_code=503,
                detail="MiniMax API key not configured"
            )
        
        result = await minimax_service.generate_ppt_outline(
            topic=request.topic,
            pages=request.pages,
            language=request.language.value,
            theme=request.theme.value if hasattr(request, 'theme') else "business"
        )
        
        outline_items = [
            PPTOutlineItem(
                page_num=item["page_num"],
                title=item["title"],
                content=item["content"],
                bullets=item.get("bullets", [])
            )
            for item in result.get("outline", [])
        ]
        
        return PPTOutlineResponse(
            topic=result.get("topic", request.topic),
            total_pages=len(outline_items),
            outline=outline_items,
            theme=request.theme or PPTTheme.BUSINESS,
            language=request.language
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# MCP Skills endpoints
@router.post("/mcp/execute", response_model=MCPSkillResult)
async def execute_mcp_skill(request: MCPSkillInput):
    """Execute an MCP skill"""
    result = await mcp_registry.execute(
        request.skill_name,
        request.parameters
    )
    
    return MCPSkillResult(
        skill_name=request.skill_name,
        success=result.get("success", False),
        result=result.get("result", {}),
        error=result.get("error")
    )


@router.get("/mcp/skills")
async def list_mcp_skills():
    """List available MCP skills"""
    skills = {
        "ppt.structure": "Analyze and validate PPT structure",
        "ppt.content": "Generate detailed content for PPT pages",
        "ppt.design": "Apply design templates and themes",
        "ppt.export": "Process export formats and options",
        "ppt.validate": "Validate PPT file and content",
        "ppt.optimize": "Optimize content for better presentation"
    }
    
    return {
        "skills": skills,
        "total": len(skills)
    }
