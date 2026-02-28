"""
Task management service for async PPT generation
"""
import uuid
import asyncio
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum
from dataclasses import dataclass, field

from models.schemas import TaskStatus


@dataclass
class PPTTask:
    """PPT Generation Task"""
    task_id: str
    topic: str
    description: str
    pages: int
    theme: str
    language: str
    status: TaskStatus = TaskStatus.PENDING
    message: str = ""
    file_url: Optional[str] = None
    outline: list = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error: Optional[str] = None


class TaskManager:
    """Manages async PPT generation tasks"""
    
    def __init__(self):
        self.tasks: Dict[str, PPTTask] = {}
        self._lock = asyncio.Lock()
    
    async def create_task(
        self,
        topic: str,
        description: str,
        pages: int,
        theme: str,
        language: str
    ) -> PPTTask:
        """Create a new task"""
        task_id = str(uuid.uuid4())
        
        task = PPTTask(
            task_id=task_id,
            topic=topic,
            description=description,
            pages=pages,
            theme=theme,
            language=language,
            status=TaskStatus.PENDING,
            message="Task created, waiting for processing"
        )
        
        async with self._lock:
            self.tasks[task_id] = task
        
        return task
    
    async def get_task(self, task_id: str) -> Optional[PPTTask]:
        """Get task by ID"""
        async with self._lock:
            return self.tasks.get(task_id)
    
    async def update_status(
        self,
        task_id: str,
        status: TaskStatus,
        message: str = "",
        file_url: Optional[str] = None,
        outline: list = None,
        error: Optional[str] = None
    ):
        """Update task status"""
        async with self._lock:
            if task_id in self.tasks:
                task = self.tasks[task_id]
                task.status = status
                if message:
                    task.message = message
                if file_url:
                    task.file_url = file_url
                if outline is not None:
                    task.outline = outline
                if error:
                    task.error = error
                if status == TaskStatus.COMPLETED or status == TaskStatus.FAILED:
                    task.completed_at = datetime.now()
    
    async def process_task(self, task_id: str):
        """Process a task (generate PPT)"""
        task = await self.get_task(task_id)
        if not task:
            return
        
        try:
            # Update status to processing
            await self.update_status(
                task_id,
                TaskStatus.PROCESSING,
                "Generating PPT outline..."
            )
            
            # Import services here to avoid circular imports
            from services.minimax_service import minimax_service
            from services.ppt_generator import ppt_generator
            from mcp.skills import mcp_registry
            
            # Generate outline using MiniMax
            outline_result = await minimax_service.generate_ppt_outline(
                topic=task.topic,
                pages=task.pages,
                language=task.language,
                theme=task.theme
            )
            
            outline = outline_result.get("outline", [])
            
            # Apply MCP skills for optimization
            await self.update_status(
                task_id,
                TaskStatus.PROCESSING,
                "Optimizing content..."
            )
            
            optimize_result = await mcp_registry.execute("ppt.optimize", {
                "outline": outline,
                "max_bullets_per_slide": 6
            })
            
            if optimize_result.get("success"):
                outline = optimize_result.get("result", {}).get("enhanced_pages", outline)
            
            await self.update_status(
                task_id,
                TaskStatus.PROCESSING,
                "Generating PPT file...",
                outline=outline
            )
            
            # Generate PPT file
            result = await ppt_generator.generate(
                topic=task.topic,
                outline=outline,
                theme=task.theme,
                language=task.language
            )
            
            # Update with success
            await self.update_status(
                task_id,
                TaskStatus.COMPLETED,
                "PPT generated successfully!",
                file_url=f"/api/ppt/download/{result['filename']}"
            )
            
        except Exception as e:
            await self.update_status(
                task_id,
                TaskStatus.FAILED,
                error=str(e),
                message=f"Failed to generate PPT: {str(e)}"
            )
    
    async def list_tasks(self, limit: int = 50) -> list:
        """List all tasks"""
        async with self._lock:
            tasks = list(self.tasks.values())
            tasks.sort(key=lambda t: t.created_at, reverse=True)
            return tasks[:limit]
    
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task"""
        async with self._lock:
            if task_id in self.tasks:
                del self.tasks[task_id]
                return True
            return False


# Singleton instance
task_manager = TaskManager()
