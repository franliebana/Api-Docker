from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import get_db
from models import Project, User
from schemas import ProjectCreate, ProjectResponse, ProjectUpdate

# Groups all project-related endpoints under /projects.
router = APIRouter(prefix="/projects", tags=["projects"])

@router.post("", response_model=ProjectResponse, status_code=status.HTTP_201_CREATED)
def create_project(project_data: ProjectCreate, db: Session = Depends(get_db)) -> Project:
    # Prevent duplicate projects before inserting the new project.
    existing_project = db.scalar(select(Project).where(Project.name == project_data.name))
    if existing_project:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="A project with this name already exists",
        )
    
    # Check if the owner exists before creating the project.
    owner = db.get(User, project_data.owner_id)
    if owner is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Owner not found",
        )      
                    
    # Create a new project instance.
    project = Project(
        name=project_data.name,
        description=project_data.description,
        owner_id=project_data.owner_id,
    )

    # Persist the project and load database-generated fields such as id and created_at.
    db.add(project)
    db.commit()
    db.refresh(project)
    
    return project


@router.get("", response_model=list[ProjectResponse])
def list_projects(db: Session = Depends(get_db)) -> list[Project]:
    # Return projects ordered by their database id.
    return list(db.scalars(select(Project).order_by(Project.id)))


@router.get("/{project_id}", response_model=ProjectResponse)
def get_project(project_id: int, db: Session = Depends(get_db)) -> Project:
    # Look up a project by its primary key.
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )
    return project


@router.patch("/{project_id}", response_model=ProjectResponse)
def update_project(project_id: int, project_data: ProjectUpdate, db: Session = Depends(get_db),) -> Project:
    # Look up the project before updating it.
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    # Convert the Pydantic model to a dictionary, excluding unset fields to allow partial updates.
    update_data = project_data.model_dump(exclude_unset=True)

    # Check that the new name is not already taken by another project before updating it.
    if "name" in update_data and update_data["name"] != project.name:
        # Check for existing projects with the same name, excluding the current project.
        existing_project = db.scalar(
            select(Project).where(
                Project.name == update_data["name"],
                Project.id != project_id,
            )
        )
        if existing_project:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="A project with this name already exists",
            )
        project.name = update_data["name"]

    # Update the project description if a new description is provided.
    if "description" in update_data:
        project.description = update_data["description"]

    db.commit()
    db.refresh(project)
    return project


@router.delete("/{project_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_project(project_id: int, db: Session = Depends(get_db)) -> None:
    # Look up the project before deleting it.
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Project not found",
        )

    db.delete(project)
    db.commit()