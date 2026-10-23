"""Database operations for projects."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.project import ProjectRecord
from app.schemas.project import ProjectCreate


class ProjectRepository:
    """Translate project use cases into SQLAlchemy operations."""

    @staticmethod
    def create(db: Session, project_data: ProjectCreate) -> ProjectRecord:
        project = ProjectRecord(**project_data.model_dump())
        db.add(project)
        db.commit()
        db.refresh(project)
        return project

    @staticmethod
    def list_all(db: Session) -> list[ProjectRecord]:
        statement = select(ProjectRecord).order_by(ProjectRecord.created_at)
        return list(db.scalars(statement))


project_repository = ProjectRepository()

