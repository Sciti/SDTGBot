import base64
import datetime
import os

from aiogram import Bot, types
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.text import Const, Format
from aiogram_dialog.widgets.kbd import (
    Row,
    SwitchTo,
    Cancel,
    Button,
    ScrollingGroup,
    Select,
    PrevPage,
    CurrentPage,
    NextPage,
    Column,
)
from aiogram_dialog.widgets.input import MessageInput
from aiogram.enums import ChatType

from database import repository as repo
from database import models
from ..states import AdminSG


async def generate_code(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    random_bytes = os.urandom(16)
    token = base64.urlsafe_b64encode(random_bytes).rstrip(b"=")
    code = token.decode("utf-8")
    
    user = await repo.get_user_by_tg_id(callback.from_user.id)
    code_obj = await repo.add_code(code=code, created_by=user.id)
    code_obj.expires_at = code_obj.created_at + datetime.timedelta(minutes=1)
    await repo.update_object(code_obj)
    dialog_manager.dialog_data["selected_code"] = code_obj.id
    await dialog_manager.switch_to(AdminSG.show_code)


async def on_code_select(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    selected_item: str,
):
    dialog_manager.dialog_data["selected_code"] = selected_item
    await dialog_manager.switch_to(AdminSG.show_code)


async def code_getter(dialog_manager: DialogManager, **_kwargs):
    bot: Bot = dialog_manager.middleware_data.get("bot")
    bot_data = await bot.get_me()
    code_id = dialog_manager.dialog_data.get("selected_code")
    code_obj = await repo.get_code(int(code_id))
    if (
        code_obj.is_active
        and code_obj.expires_at
        and code_obj.expires_at < datetime.datetime.utcnow()
    ):
        code_obj.is_active = False
        await repo.update_object(code_obj)

    return {
        "code": code_obj.code,
        "created_at": code_obj.created_at,
        "max_uses": code_obj.max_uses,
        "used_count": code_obj.used_count,
        "expires_at": code_obj.expires_at,
        "is_active": "✅" if code_obj.is_active else "❌",
        "creator": await repo.get_user(code_obj.created_by),
        "link": f"https://t.me/{bot_data.username}?start={code_obj.code}",
    }


async def codes_getter(**_):
    codes = await repo.get_codes()
    return {"codes": codes}


async def on_user_select(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    selected_item: str,
):
    user = await repo.get_user(int(selected_item))
    dialog_manager.dialog_data["selected_user"] = user.id
    await dialog_manager.switch_to(AdminSG.user_info)


async def users_getter(dialog_manager: DialogManager, **_kwargs):
    users = await repo.get_users()
    return {"users": users}


async def user_info_getter(dialog_manager: DialogManager, **_kwargs):
    user_id = dialog_manager.dialog_data.get("selected_user")
    user = await repo.get_user(user_id)
    return {"user": user}


async def channels_getter(dialog_manager: DialogManager, **_kwargs):
    channels = await repo.get_channels()
    return {"channels": channels}


async def on_channel_select(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    selected_item: str,
):
    dialog_manager.dialog_data["selected_channel"] = int(selected_item)
    await dialog_manager.switch_to(AdminSG.channel_info)


async def channel_info_getter(dialog_manager: DialogManager, **_kwargs):
    channel_id = dialog_manager.dialog_data.get("selected_channel")
    channel = await repo.get_channel_by_chat_id(channel_id)
    return {"channel": channel}


async def delete_channel(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
):
    channel_id = dialog_manager.dialog_data.get("selected_channel")
    await repo.delete_channel(channel_id)
    await dialog_manager.switch_to(AdminSG.channels)


async def on_channel_id(message: types.Message, message_input: MessageInput, dialog_manager: DialogManager):
    try:
        chat_id = int(message.text)
    except ValueError:
        await message.answer("Некорректный ID")
        return
    bot: Bot = dialog_manager.middleware_data.get("bot")
    try:
        chat = await bot.get_chat(chat_id)
    except Exception:
        await message.answer("Не удалось получить информацию о чате")
        return
    channel_type = models.ChannelType.CHANNEL
    if chat.type in {ChatType.GROUP, ChatType.SUPERGROUP}:
        channel_type = models.ChannelType.GROUP
    await repo.create_channel(chat_id=chat.id, channel_type=channel_type, title=chat.title)
    await message.answer("Канал добавлен")
    await dialog_manager.switch_to(AdminSG.channels)


async def on_role_select(
    callback: types.CallbackQuery,
    button: Button,
    dialog_manager: DialogManager,
    selected_item: str,
):
    await repo.modify_user(
        user_id=dialog_manager.dialog_data["selected_user"],
        role=selected_item,
    )
    await dialog_manager.switch_to(AdminSG.user_info)


administration_dialog = Dialog(
    Window(
        Const("Администрирование:"),
        Row(
            SwitchTo(Const("Каналы"), id="channels", state=AdminSG.channels),
            SwitchTo(Const("Пользователи"), id="users", state=AdminSG.users),
            SwitchTo(Const("Коды регистрации"), id="rcodes", state=AdminSG.register_codes),
        ),
        Cancel(Const("Назад")),
        state=AdminSG.menu,
    ),
    Window(
        Const("Каналы:"),
        Column(
            Select(
                Format("[{item.channel_type.value}] {item.title} ({item.channel_id})"),
                id="s_channel",
                items="channels",
                on_click=on_channel_select,
                item_id_getter=lambda c: c.channel_id,
            )
        ),
        Row(
            SwitchTo(Const("Создать канал"), id="create_channel", state=AdminSG.create_channel),
            Cancel(Const("Назад")),
        ),
        state=AdminSG.channels,
        getter=channels_getter,
    ),
    Window(
        Format("Канал: {channel.title} ({channel.channel_id})"),
        Button(Const("Удалить"), id="delete", on_click=delete_channel),
        Row(
            SwitchTo(Const("Назад"), id="back_to_channels", state=AdminSG.channels),
            Cancel(Const("Меню")),
        ),
        state=AdminSG.channel_info,
        getter=channel_info_getter,
    ),
    Window(
        Const("Введите ID канала:"),
        MessageInput(on_channel_id),
        Cancel(Const("Назад")),
        state=AdminSG.create_channel,
    ),
    Window(
        Const("Выберите пользователя:"),
        ScrollingGroup(
            Select(
                Format("{item.tg_username}"),
                id="s_user",
                items="users",
                on_click=on_user_select,
                item_id_getter=lambda u: u.id,
            ),
            width=1,
            height=6,
            id="users_scroll",
        ),
        Row(
            PrevPage(scroll="users_scroll"),
            NextPage(scroll="users_scroll"),
        ),
        Cancel(Const("Назад")),
        state=AdminSG.users,
        getter=users_getter,
    ),
    Window(
        Format("Пользователь: {user.tg_username}"),
        Format("Telegram ID: {user.tg_id}"),
        Format("Роль: {user.role.name}"),
        SwitchTo(Const("Сменить роль"), id="change_role", state=AdminSG.change_role),
        Cancel(Const("Назад")),
        getter=user_info_getter,
        state=AdminSG.user_info,
    ),
    Window(
        Const("Выберите роль:"),
        Column(
            Select(
                Format("{item.name}"),
                id="s_role",
                items=list(models.UserRole),
                on_click=on_role_select,
                item_id_getter=lambda r: r.name,
            )
        ),
        Cancel(Const("Назад")),
        state=AdminSG.change_role,
    ),
    Window(
        Const("Управление кодами регистрации"),
        Button(Const("Сгенерировать ссылку"), id="generate_link", on_click=generate_code),
        SwitchTo(Const("Просмотреть"), id="show_codes", state=AdminSG.show_codes),
        Cancel(Const("Назад")),
        state=AdminSG.register_codes,
    ),
    Window(
        Const("Сгенерированные коды:"),
        ScrollingGroup(
            Select(
                Format("#{item.id}: {item.created_at:%Y-%m-%d}"),
                id="s_code",
                items="codes",
                on_click=on_code_select,
                item_id_getter=lambda c: c.id,
            ),
            width=1,
            height=6,
            id="codes_scroll",
        ),
        Row(
            PrevPage(scroll="codes_scroll"),
            CurrentPage(scroll="codes_scroll"),
            NextPage(scroll="codes_scroll"),
        ),
        Row(
            SwitchTo(Const("Назад"), id="back", state=AdminSG.register_codes),
            Cancel(Const("Меню")),
        ),
        state=AdminSG.show_codes,
        getter=codes_getter,
    ),
    Window(
        Format("Код: {code}"),
        Format("Создан: {created_at:%Y-%m-%d}"),
        Format("Активен: {is_active} [{expires_at:%Y-%m-%d %H:%M}]"),
        Format("Использовано: {used_count}/{max_uses}"),
        Format("Ссылка: {link}"),
        Row(
            SwitchTo(Const("Назад"), id="back_to_codes", state=AdminSG.register_codes),
            Cancel(Const("Меню")),
        ),
        state=AdminSG.show_code,
        getter=code_getter,
    ),
)
