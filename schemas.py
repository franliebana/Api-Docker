from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator


# Data required to create a new user.
class UserCreate(BaseModel):
	email: EmailStr
	password: str = Field(min_length=8) # Password must be at least 8 characters long.


# Optional fields accepted when updating a user.
class UserUpdate(BaseModel):
	email: EmailStr | None = None
	password: str | None = Field(default=None, min_length=8) # Password must be at least 8 characters long if provided.

	# Validator to ensure that if the email or password fields are provided, they cannot be null.
	@model_validator(mode="after")
	def reject_null_fields(self):
		for field in ("email", "password"):
			if field in self.model_fields_set and getattr(self, field) is None:
				raise ValueError(f"{field} cannot be null")
		return self


# Public user data returned by the API.
class UserResponse(BaseModel):
	# Allows validation directly from a SQLAlchemy model instance.
	model_config = ConfigDict(from_attributes=True)

	id: int
	email: EmailStr
	created_at: datetime


class LoginRequest(BaseModel):
	email: EmailStr
	password: str


class TokenResponse(BaseModel):
	access_token: str
	token_type: str = "bearer"


# Data required to create a new project.
class ProjectCreate(BaseModel):
	name: str = Field(min_length=1, max_length=255) # Name must be at least 1 character long and cannot exceed 255 characters.
	description: str | None = Field(default=None, max_length=2000) # Description can be null, but if provided, it must not exceed 2000 characters.


# Optional fields accepted when updating a project.
class ProjectUpdate(BaseModel):
	name: str | None = Field(default=None, min_length=1, max_length=255) # Name must be at least 1 character long and cannot exceed 255 characters.
	description: str | None = Field(default=None, max_length=2000) # Description can be null, but if provided, it must not exceed 2000 characters.

	# Validator to ensure that if the name field is provided, it cannot be null.
	@model_validator(mode="after")
	def reject_null_name(self):
		if "name" in self.model_fields_set and self.name is None:
			raise ValueError("name cannot be null")
		return self

# Project data returned by the API.
class ProjectResponse(BaseModel):
	# Allows validation directly from a SQLAlchemy model instance.
	model_config = ConfigDict(from_attributes=True)

	id: int
	name: str
	description: str | None
	owner_id: int
	created_at: datetime
