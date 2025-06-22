from __future__ import annotations

from datetime import datetime

from sqlalchemy import select

from . import async_session_factory
from .models import (
    Base,
    Channel,
    ChannelType,
    Post,
    PostChannel,
    RegistrationCode,
    Template,
    User,
    UserRole,
)


# Users
async def get_user_by_tg_id(tg_id: int) -> User | None:
    stmt = select(User).where(User.tg_id == tg_id)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def get_user(user_id: int) -> User | None:
    stmt = select(User).where(User.id == user_id)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def create_user(
    role: UserRole,
    tg_id: int,
    tg_username: str | None = None,
) -> User:
    user = User(role=role, tg_id=tg_id, tg_username=tg_username)
    async with async_session_factory() as session:
        session.add(user)
        await session.commit()
    return user


async def get_users() -> list[User]:
    async with async_session_factory() as session:
        result = await session.scalars(select(User))
        return list(result)


async def modify_user(user_id: int, role: str | UserRole) -> None:
    stmt = select(User).where(User.id == user_id)
    async with async_session_factory() as session:
        user = await session.scalar(stmt)
        if user:
            if isinstance(role, str):
                role = UserRole[role]
            user.role = role
            await session.commit()


# Channels
async def get_channel_by_chat_id(chat_id: int) -> Channel | None:
    stmt = select(Channel).where(Channel.channel_id == chat_id)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def create_channel(
    chat_id: int,
    channel_type: ChannelType,
    title: str | None = None,
) -> Channel:
    channel = Channel(channel_id=chat_id, channel_type=channel_type, title=title)
    async with async_session_factory() as session:
        session.add(channel)
        await session.commit()
    return channel


async def get_channels() -> list[Channel]:
    async with async_session_factory() as session:
        result = await session.scalars(select(Channel))
        return list(result)


async def delete_channel(chat_id: int) -> None:
    stmt = select(Channel).where(Channel.channel_id == chat_id)
    async with async_session_factory() as session:
        channel = await session.scalar(stmt)
        if channel:
            await session.delete(channel)
            await session.commit()


# Templates
async def get_template(template_id: int) -> Template | None:
    stmt = select(Template).where(Template.id == template_id)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def create_template(
    user_id: int,
    name: str,
    text: str,
    buttons: list[dict] | None = None,
) -> Template:
    template = Template(name=name, text=text, buttons=buttons, user_id=user_id)
    async with async_session_factory() as session:
        session.add(template)
        await session.commit()
    return template


# Posts
async def get_post(post_id: int) -> Post | None:
    stmt = select(Post).where(Post.id == post_id)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def create_post(
    user_id: int,
    text: str,
    steam_id: int | None = None,
    template_id: int | None = None,
    scheduled_at: datetime | None = None,
) -> Post:
    post = Post(
        user_id=user_id,
        text=text,
        steam_id=steam_id,
        template_id=template_id,
        scheduled_at=scheduled_at,
    )
    async with async_session_factory() as session:
        session.add(post)
        await session.commit()
    return post


async def link_post_channel(post_id: int, channel_id: int) -> None:
    link = PostChannel(post_id=post_id, channel_id=channel_id)
    async with async_session_factory() as session:
        session.add(link)
        await session.commit()


async def mark_post_sent(post_id: int, tg_message_id: int) -> None:
    stmt = select(Post).where(Post.id == post_id)
    async with async_session_factory() as session:
        post = await session.scalar(stmt)
        if post:
            post.is_sent = True
            post.tg_message_id = tg_message_id
            await session.commit()


async def get_post_channels(post_id: int) -> list[Channel]:
    """Return channels linked with the post."""
    stmt = (
        select(Channel)
        .join(PostChannel, Channel.id == PostChannel.channel_id)
        .where(PostChannel.post_id == post_id)
    )
    async with async_session_factory() as session:
        result = await session.scalars(stmt)
        return list(result)


# Registration codes
async def add_code(
    code: str,
    created_by: int,
    expires_at: datetime | None = None,
    max_uses: int = 1,
) -> RegistrationCode:
    code_obj = RegistrationCode(
        code=code,
        created_by=created_by,
        expires_at=expires_at,
        max_uses=max_uses,
    )
    async with async_session_factory() as session:
        session.add(code_obj)
        await session.commit()
    return code_obj


async def get_code(code: str | int) -> RegistrationCode | None:
    if isinstance(code, int):
        stmt = select(RegistrationCode).where(RegistrationCode.id == code)
    else:
        stmt = select(RegistrationCode).where(RegistrationCode.code == code)
    async with async_session_factory() as session:
        return await session.scalar(stmt)


async def get_codes() -> list[RegistrationCode]:
    async with async_session_factory() as session:
        result = await session.scalars(select(RegistrationCode))
        return list(result)


async def update_object(obj: Base) -> None:
    async with async_session_factory() as session:
        session.add(obj)
        await session.commit()

