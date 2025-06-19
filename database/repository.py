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


class Repository:
    """Database access layer using per-method sessions."""

    # Users
    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        async with async_session_factory() as session:
            stmt = select(User).where(User.tg_id == tg_id)
            return await session.scalar(stmt)

    async def get_user(self, user_id: int) -> User | None:
        async with async_session_factory() as session:
            stmt = select(User).where(User.id == user_id)
            return await session.scalar(stmt)

    async def create_user(
        self,
        role: UserRole,
        tg_id: int,
        tg_username: str | None = None,
    ) -> User:
        async with async_session_factory() as session:
            user = User(role=role, tg_id=tg_id, tg_username=tg_username)
            session.add(user)
            await session.commit()
            return user

    async def get_users(self) -> list[User]:
        async with async_session_factory() as session:
            result = await session.scalars(select(User))
            return list(result)

    async def modify_user(self, user_id: int, role: str | UserRole) -> None:
        async with async_session_factory() as session:
            user = await session.scalar(select(User).where(User.id == user_id))
            if user:
                if isinstance(role, str):
                    role = UserRole[role]
                user.role = role
                await session.commit()

    # Channels
    async def get_channel_by_chat_id(self, chat_id: int) -> Channel | None:
        async with async_session_factory() as session:
            stmt = select(Channel).where(Channel.channel_id == chat_id)
            return await session.scalar(stmt)

    async def create_channel(
        self,
        chat_id: int,
        channel_type: ChannelType,
        title: str | None = None,
    ) -> Channel:
        async with async_session_factory() as session:
            channel = Channel(channel_id=chat_id, channel_type=channel_type, title=title)
            session.add(channel)
            await session.commit()
            return channel

    async def get_channels(self) -> list[Channel]:
        async with async_session_factory() as session:
            result = await session.scalars(select(Channel))
            return list(result)

    async def delete_channel(self, chat_id: int) -> None:
        async with async_session_factory() as session:
            channel = await session.scalar(select(Channel).where(Channel.channel_id == chat_id))
            if channel:
                await session.delete(channel)
                await session.commit()

    # Templates
    async def get_template(self, template_id: int) -> Template | None:
        async with async_session_factory() as session:
            stmt = select(Template).where(Template.id == template_id)
            return await session.scalar(stmt)

    async def create_template(
        self,
        user_id: int,
        name: str,
        text: str,
        buttons: list[dict] | None = None,
    ) -> Template:
        async with async_session_factory() as session:
            template = Template(name=name, text=text, buttons=buttons, user_id=user_id)
            session.add(template)
            await session.commit()
            return template

    # Posts
    async def get_post(self, post_id: int) -> Post | None:
        async with async_session_factory() as session:
            stmt = select(Post).where(Post.id == post_id)
            return await session.scalar(stmt)

    async def create_post(
        self,
        user_id: int,
        text: str,
        steam_id: int | None = None,
        template_id: int | None = None,
        scheduled_at: datetime | None = None,
    ) -> Post:
        async with async_session_factory() as session:
            post = Post(
                user_id=user_id,
                text=text,
                steam_id=steam_id,
                template_id=template_id,
                scheduled_at=scheduled_at,
            )
            session.add(post)
            await session.commit()
            return post

    async def link_post_channel(self, post_id: int, channel_id: int) -> None:
        async with async_session_factory() as session:
            link = PostChannel(post_id=post_id, channel_id=channel_id)
            session.add(link)
            await session.commit()

    async def mark_post_sent(self, post_id: int, tg_message_id: int) -> None:
        async with async_session_factory() as session:
            post = await session.scalar(select(Post).where(Post.id == post_id))
            if post:
                post.is_sent = True
                post.tg_message_id = tg_message_id
                await session.commit()

    # Registration codes
    async def add_code(
        self,
        code: str,
        created_by: int,
        expires_at: datetime | None = None,
        max_uses: int = 1,
    ) -> RegistrationCode:
        async with async_session_factory() as session:
            code_obj = RegistrationCode(
                code=code,
                created_by=created_by,
                expires_at=expires_at,
                max_uses=max_uses,
            )
            session.add(code_obj)
            await session.commit()
            return code_obj

    async def get_code(self, code: str | int) -> RegistrationCode | None:
        async with async_session_factory() as session:
            if isinstance(code, int):
                stmt = select(RegistrationCode).where(RegistrationCode.id == code)
            else:
                stmt = select(RegistrationCode).where(RegistrationCode.code == code)
            return await session.scalar(stmt)

    async def get_codes(self) -> list[RegistrationCode]:
        async with async_session_factory() as session:
            result = await session.scalars(select(RegistrationCode))
            return list(result)

    async def update_object(self, obj: Base) -> None:
        async with async_session_factory() as session:
            session.add(obj)
            await session.commit()
