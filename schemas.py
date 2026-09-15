from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


# Data required to create a new user.
class UserCreate(BaseModel):
	email: EmailStr
	password: str


# Public user data returned by the API.
class UserResponse(BaseModel):
	# Allows validation directly from a SQLAlchemy model instance.
	model_config = ConfigDict(from_attributes=True)

	id: int
	email: EmailStr
	created_at: datetime


# Data required to create a new project.
class ProjectCreate(BaseModel):
	# This will later come from the authenticated user.
	name: str
	description: str | None = None
	owner_id: int


# Optional fields accepted when updating a project.
class ProjectUpdate(BaseModel):
	name: str | None = None
	description: str | None = None


# Project data returned by the API.
class ProjectResponse(BaseModel):
	# Allows validation directly from a SQLAlchemy model instance.
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	description: str | None
	owner_id: int
	created_at: datetime
