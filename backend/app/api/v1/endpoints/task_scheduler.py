"""
API endpoints for task scheduler management
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from typing import Any, Dict

from app.api import deps
from app.models.user import User
from app.services.task_scheduler import task_scheduler_service

router = APIRouter()


@router.post("/generate", response_model=Dict[str, Any])
async def manually_generate_recurring_tasks(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Manually trigger recurring task generation.
    Useful for testing and debugging.
    """
    try:
        stats = await task_scheduler_service.manual_generate()
        return {
            "message": "Manual task generation completed",
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error during manual generation: {str(e)}")


@router.get("/status", response_model=Dict[str, Any])
def get_scheduler_status(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get the status of the task scheduler service.
    """
    try:
        return {
            "is_running": task_scheduler_service.is_running,
            "scheduler_state": "running" if task_scheduler_service.is_running else "stopped",
            "jobs": [
                {
                    "id": job.id,
                    "name": job.name,
                    "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None
                }
                for job in task_scheduler_service.scheduler.get_jobs()
            ] if task_scheduler_service.is_running else []
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting scheduler status: {str(e)}")


@router.post("/start", response_model=Dict[str, str])
def start_scheduler(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Start the task scheduler service.
    """
    try:
        if task_scheduler_service.is_running:
            return {"message": "Task scheduler is already running"}
        
        task_scheduler_service.start()
        return {"message": "Task scheduler started successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error starting scheduler: {str(e)}")


@router.post("/stop", response_model=Dict[str, str])
def stop_scheduler(
    request: Request,
    *,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Stop the task scheduler service.
    """
    try:
        if not task_scheduler_service.is_running:
            return {"message": "Task scheduler is not running"}
        
        task_scheduler_service.stop()
        return {"message": "Task scheduler stopped successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error stopping scheduler: {str(e)}")