"""HTTP endpoints for ContextBridge projects."""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.repositories.project_repository import project_repository
from app.schemas.project import Project, ProjectCreate

router = APIRouter(prefix="/projects", tags=["projects"])


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED)
def create_project(
    project_data: ProjectCreate,
    db: Annotated[Session, Depends(get_db)],
) -> Project:
    """Create a context-isolated project."""
    return project_repository.create(db, project_data)


@router.get("", response_model=list[Project])
def list_projects(db: Annotated[Session, Depends(get_db)]) -> list[Project]:
    """List every project in creation order."""
    return project_repository.list_all(db)

