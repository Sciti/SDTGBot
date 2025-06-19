from __future__ import annotations

import enum
from datetime import datetime

from sqlalchemy import BigInteger, Boolean, Enum, ForeignKey, Integer, String, Text, DateTime, JSON
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class ChannelType(enum.Enum):
    GROUP = "group"
    CHANNEL = "channel"


class UserRole(enum.Enum):
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"


class PostChannel(Base):
    __tablename__ = "posts_channels"

    post_id: Mapped[int] = mapped_column(ForeignKey("posts.id", ondelete="CASCADE"), primary_key=True)
    channel_id: Mapped[int] = mapped_column(ForeignKey("channels.id", ondelete="CASCADE"), primary_key=True)


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), nullable=False)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    tg_username: Mapped[str | None] = mapped_column(String(length=255), nullable=True)

    posts: Mapped[list["Post"]] = relationship(back_populates="author", cascade="all, delete-orphan")
    templates: Mapped[list["Template"]] = relationship(back_populates="creator", cascade="all, delete-orphan")


class Channel(Base):
    __tablename__ = "channels"

    id: Mapped[int] = mapped_column(primary_key=True)
    channel_id: Mapped[int] = mapped_column(BigInteger, unique=True, nullable=False)
    channel_type: Mapped[ChannelType] = mapped_column(Enum(ChannelType), nullable=False)
    title: Mapped[str | None] = mapped_column(String(length=255))

    posts: Mapped[list["Post"]] = relationship(
        secondary="posts_channels",
        back_populates="channels",
    )


class Template(Base):
    __tablename__ = "templates"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(length=255), nullable=False)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    buttons: Mapped[list[dict] | None] = mapped_column(JSON, nullable=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    creator: Mapped["User"] = relationship(back_populates="templates")
    posts: Mapped[list["Post"]] = relationship(back_populates="template")


class Post(Base):
    __tablename__ = "posts"

    id: Mapped[int] = mapped_column(primary_key=True)
    steam_id: Mapped[int | None] = mapped_column(BigInteger)
    text: Mapped[str] = mapped_column(Text, nullable=False)
    tg_message_id: Mapped[int | None] = mapped_column(BigInteger)
    tg_image_id: Mapped[int | None] = mapped_column(BigInteger)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    is_sent: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    template_id: Mapped[int | None] = mapped_column(ForeignKey("templates.id", ondelete="SET NULL"))

    author: Mapped["User"] = relationship(back_populates="posts")
    template: Mapped[Template | None] = relationship(back_populates="posts")
    channels: Mapped[list["Channel"]] = relationship(
        secondary="posts_channels",
        back_populates="posts",
    )


class RegistrationCode(Base):
    __tablename__ = "registration_codes"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(String(length=32), unique=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    max_uses: Mapped[int] = mapped_column(Integer, default=1)
    used_count: Mapped[int] = mapped_column(Integer, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_by: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    used_by: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    creator: Mapped["User"] = relationship(foreign_keys=[created_by])
    user: Mapped[User | None] = relationship(foreign_keys=[used_by])


