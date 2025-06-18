from __future__ import annotations

from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .models import Channel, ChannelType, Post, PostChannel, Template, User


class Repository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    # Users
    async def get_user_by_tg_id(self, tg_id: int) -> User | None:
        stmt = select(User).where(User.tg_id == tg_id)
        return await self.session.scalar(stmt)

    async def create_user(self, role: str, tg_id: int, tg_username: str | None = None) -> User:
        user = User(role=role, tg_id=tg_id, tg_username=tg_username)
        self.session.add(user)
        await self.session.flush()
        return user

    # Channels
    async def get_channel_by_chat_id(self, chat_id: int) -> Channel | None:
        stmt = select(Channel).where(Channel.channel_id == chat_id)
        return await self.session.scalar(stmt)

    async def create_channel(
        self,
        chat_id: int,
        channel_type: ChannelType,
        title: str | None = None,
    ) -> Channel:
        channel = Channel(channel_id=chat_id, channel_type=channel_type, title=title)
        self.session.add(channel)
        await self.session.flush()
        return channel

    # Templates
    async def get_template(self, template_id: int) -> Template | None:
        stmt = select(Template).where(Template.id == template_id)
        return await self.session.scalar(stmt)

    async def create_template(
        self,
        user_id: int,
        name: str,
        text: str,
        buttons: list[dict] | None = None,
    ) -> Template:
        template = Template(name=name, text=text, buttons=buttons, user_id=user_id)
        self.session.add(template)
        await self.session.flush()
        return template

    # Posts
    async def get_post(self, post_id: int) -> Post | None:
        stmt = select(Post).where(Post.id == post_id)
        return await self.session.scalar(stmt)

    async def create_post(
        self,
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
        self.session.add(post)
        await self.session.flush()
        return post

    async def link_post_channel(self, post_id: int, channel_id: int) -> None:
        link = PostChannel(post_id=post_id, channel_id=channel_id)
        self.session.add(link)
        await self.session.flush()

    async def mark_post_sent(self, post_id: int, tg_message_id: int) -> None:
        post = await self.get_post(post_id)
        if post:
            post.is_sent = True
            post.tg_message_id = tg_message_id
            await self.session.flush()
