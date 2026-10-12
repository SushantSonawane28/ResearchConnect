"""Database tables. One class = one table. Compare with docs/schema.sql."""
from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Index, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .database import Base


class Organization(Base):          # a college, university or company
    __tablename__ = "organizations"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(200), unique=True)
    org_type: Mapped[str] = mapped_column(String(20), default="college")  # college|university|company


class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(20), default="researcher")  # researcher|coordinator|industry|admin
    organization_id: Mapped[int] = mapped_column(ForeignKey("organizations.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    organization: Mapped[Organization] = relationship()
    profile: Mapped[Optional["Profile"]] = relationship(back_populates="user", uselist=False)


class Tag(Base):                   # one shared list of skills/interests, stored once
    __tablename__ = "tags"
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)


class Profile(Base):
    __tablename__ = "profiles"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)
    bio: Mapped[str] = mapped_column(Text, default="")
    department: Mapped[str] = mapped_column(String(120), default="")
    designation: Mapped[str] = mapped_column(String(120), default="")
    visibility: Mapped[str] = mapped_column(String(10), default="public")  # org (my organisation only) | public
    looking_for_collab: Mapped[bool] = mapped_column(Boolean, default=True)
    collab_area: Mapped[str] = mapped_column(String(200), default="")
    email_alerts: Mapped[bool] = mapped_column(Boolean, default=True)  # consent to match emails
    user: Mapped[User] = relationship(back_populates="profile")
    tags: Mapped[list["ProfileTag"]] = relationship(cascade="all, delete-orphan")


class ProfileTag(Base):
    __tablename__ = "profile_tags"
    profile_id: Mapped[int] = mapped_column(ForeignKey("profiles.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    kind: Mapped[str] = mapped_column(String(10), primary_key=True)  # skill|interest|expertise
    tag: Mapped[Tag] = relationship()
    __table_args__ = (Index("ix_profile_tags_tag", "tag_id"),)


class Project(Base):
    __tablename__ = "projects"
    id: Mapped[int] = mapped_column(primary_key=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(120), default="", index=True)
    status: Mapped[str] = mapped_column(String(20), default="ongoing")
    visibility: Mapped[str] = mapped_column(String(10), default="public")
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    owner: Mapped[User] = relationship()
    tags: Mapped[list["ProjectTag"]] = relationship(cascade="all, delete-orphan")


class ProjectTag(Base):
    __tablename__ = "project_tags"
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), primary_key=True)
    tag_id: Mapped[int] = mapped_column(ForeignKey("tags.id"), primary_key=True)
    tag: Mapped[Tag] = relationship()


class Opportunity(Base):           # funding call, conference, workshop, industry challenge
    __tablename__ = "opportunities"
    id: Mapped[int] = mapped_column(primary_key=True)
    posted_by: Mapped[int] = mapped_column(ForeignKey("users.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    domain: Mapped[str] = mapped_column(String(120), default="")
    opp_type: Mapped[str] = mapped_column(String(30), default="funding")  # funding|conference|workshop|industry_challenge
    deadline: Mapped[datetime | None] = mapped_column(DateTime, nullable=True, index=True)
    visibility: Mapped[str] = mapped_column(String(10), default="public")
    poster: Mapped[User] = relationship()


class CollabRequest(Base):
    __tablename__ = "collaboration_requests"
    id: Mapped[int] = mapped_column(primary_key=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.id"))
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    project_id: Mapped[int | None] = mapped_column(ForeignKey("projects.id"), nullable=True)
    message: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(10), default="pending")  # pending|accepted|rejected
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    sender: Mapped[User] = relationship(foreign_keys=[sender_id])
    receiver: Mapped[User] = relationship(foreign_keys=[receiver_id])


class Notification(Base):
    __tablename__ = "notifications"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(String(300))
    kind: Mapped[str] = mapped_column(String(30), default="info")
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class RelevanceLabel(Base):        # faculty judgement, used as ground truth in evaluation
    __tablename__ = "relevance_labels"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_a: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_b: Mapped[int] = mapped_column(ForeignKey("users.id"))
    relevant: Mapped[bool] = mapped_column(Boolean)
    judged_by: Mapped[str] = mapped_column(String(120), default="")


class MatchAlert(Base):            # remembers which pairs were already emailed (no repeats)
    __tablename__ = "match_alerts"
    id: Mapped[int] = mapped_column(primary_key=True)
    user_low: Mapped[int] = mapped_column(ForeignKey("users.id"))
    user_high: Mapped[int] = mapped_column(ForeignKey("users.id"))
    score: Mapped[float] = mapped_column(Float)
    email_status: Mapped[str] = mapped_column(String(40), default="")
    sent_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    __table_args__ = (UniqueConstraint("user_low", "user_high", name="uq_match_alert_pair"),)
