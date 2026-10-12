"""Pydantic models = input validation. Bad input is rejected before it reaches the database."""
from datetime import datetime
from typing import Literal

import email_validator
from pydantic import BaseModel, EmailStr, Field

email_validator.TEST_ENVIRONMENT = True


class RegisterIn(BaseModel):
    name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=72)
    organization_name: str = Field(min_length=2, max_length=200)
    organization_type: Literal["college", "university", "company"] = "college"
    role: Literal["researcher", "coordinator", "industry"] = "researcher"   # admin is set manually


class LoginIn(BaseModel):
    email: EmailStr
    password: str


class TokenOut(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: str
    user_id: int
    name: str


class ProfileIn(BaseModel):
    bio: str = Field(default="", max_length=3000)
    department: str = ""
    designation: str = ""
    visibility: Literal["org", "public"] = "public"
    looking_for_collab: bool = True
    collab_area: str = ""
    email_alerts: bool = True
    skills: list[str] = []
    interests: list[str] = []
    expertise: list[str] = []


class ProjectIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(default="", max_length=5000)
    domain: str = ""
    status: Literal["idea", "ongoing", "completed"] = "ongoing"
    visibility: Literal["org", "public"] = "public"
    tags: list[str] = []


class RequestIn(BaseModel):
    receiver_id: int
    project_id: int | None = None
    message: str = Field(default="", max_length=1000)


class RequestUpdate(BaseModel):
    status: Literal["accepted", "rejected"]


class OpportunityIn(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = ""
    domain: str = ""
    opp_type: Literal["funding", "conference", "workshop", "industry_challenge"] = "funding"
    deadline: datetime | None = None
    visibility: Literal["org", "public"] = "public"
