from __future__ import annotations

import datetime

from aiogram import types, F
from aiogram_dialog import Dialog, Window, DialogManager
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import (
    Calendar,
    Row,
    SwitchTo,
    Cancel,
    Button,
    Multiselect,
    Select,
    Back,
)
from aiogram_dialog.widgets.text import Const, Format
from aiogram.enums import ParseMode
from config import settings

from database import repository as repo
from ..states import PostSG
from tasks import send_post, schedule_post
from bot import bot

# MARK: creation

async def on_post_text(
    message: types.Message, message_input: MessageInput, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["text"] = message.html_text or message.text
    if dialog_manager.dialog_data.pop("editing", False):
        await dialog_manager.switch_to(PostSG.confirm)
    else:
        await dialog_manager.switch_to(PostSG.image)


async def on_image(
    message: types.Message, message_input: MessageInput, dialog_manager: DialogManager
) -> None:
    if not message.photo:
        await message.answer("Пришлите изображение")
        return
    dialog_manager.dialog_data["image_id"] = message.photo[-1].file_id
    if dialog_manager.dialog_data.pop("editing", False):
        await dialog_manager.switch_to(PostSG.confirm)
    else:
        await dialog_manager.switch_to(PostSG.app_id)


async def skip_image(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["image_id"] = None
    if dialog_manager.dialog_data.pop("editing", False):
        await dialog_manager.switch_to(PostSG.confirm)
    else:
        await dialog_manager.switch_to(PostSG.app_id)


async def on_app_id_success(
    message: types.Message,
    widget: TextInput,
    dialog_manager: DialogManager,
    app_id: int,
) -> None:
    dialog_manager.dialog_data["app_id"] = app_id
    if dialog_manager.dialog_data.pop("editing", False):
        await dialog_manager.switch_to(PostSG.confirm)
    else:
        await dialog_manager.switch_to(PostSG.channels)


async def on_app_id_error(
    message: types.Message, widget: TextInput, dialog_manager: DialogManager
) -> None:
    await message.answer("Введите число")


async def channels_getter(dialog_manager: DialogManager, **_kwargs):
    channels = await repo.get_channels()
    return {"channels": channels}


async def on_channels_next(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    widget: Multiselect = dialog_manager.find("m_channels").widget
    selected = widget.get_checked(dialog_manager)
    dialog_manager.dialog_data["channels"] = [int(i) for i in selected]
    if dialog_manager.dialog_data.pop("editing", False):
        await dialog_manager.switch_to(PostSG.confirm)
    else:
        await dialog_manager.switch_to(PostSG.schedule)


async def send_now(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["scheduled_at"] = None
    dialog_manager.dialog_data.pop("editing", None)
    await dialog_manager.switch_to(PostSG.confirm)


async def on_date_selected(
    callback: types.CallbackQuery,
    widget: Calendar,
    dialog_manager: DialogManager,
    selected_date: datetime.date,
) -> None:
    dialog_manager.dialog_data["date"] = selected_date.isoformat()
    await dialog_manager.switch_to(PostSG.time)


async def on_datetime_input(
    message: types.Message, widget: MessageInput, dialog_manager: DialogManager
) -> None:
    current_state = dialog_manager.middleware_data.get("aiogd_context").state

    try:
        if current_state == PostSG.calendar:
            dt = datetime.datetime.strptime(message.text, "%d-%m-%Y")
        elif current_state == PostSG.time:
            dt = datetime.datetime.combine(
                datetime.date.fromisoformat(dialog_manager.dialog_data['date']),
                datetime.datetime.strptime(message.text, "%H:%M").time()
            )
    except ValueError:
        await message.answer("Неверный формат. Пример: 17:30")
        return
    
    dialog_manager.dialog_data["scheduled_at"] = dt.isoformat()
    dialog_manager.dialog_data.pop("editing", None)
    await dialog_manager.switch_to(PostSG.confirm)


async def time_options_getter(**_kwargs):
    return {"times": settings.POST_TIME_OPTIONS}


async def on_time_select(
    callback: types.CallbackQuery,
    widget: Select,
    dialog_manager: DialogManager,
    item_id: str,
) -> None:
    date = dialog_manager.dialog_data.get("date")
    if date:
        hour, minute = map(int, item_id.split(":"))
        date_obj = datetime.date.fromisoformat(date)
        dt = datetime.datetime.combine(
            date_obj,
            datetime.time(hour=hour, minute=minute),
        )
        dialog_manager.dialog_data["scheduled_at"] = dt.isoformat()
    dialog_manager.dialog_data.pop("editing", None)
    await dialog_manager.switch_to(PostSG.confirm)


async def confirm_getter(dialog_manager: DialogManager, **_kwargs):
    return {
        "text": dialog_manager.dialog_data.get("text"),
        "app_id": dialog_manager.dialog_data.get("app_id"),
        "channels": dialog_manager.dialog_data.get("channels", []),
        "scheduled_at": dialog_manager.dialog_data.get("scheduled_at"),
        "image_id": dialog_manager.dialog_data.get("image_id"),
    }


async def start_edit_text(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["editing"] = True
    await dialog_manager.switch_to(PostSG.create)


async def start_edit_image(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["editing"] = True
    await dialog_manager.switch_to(PostSG.image)


async def start_edit_app(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["editing"] = True
    await dialog_manager.switch_to(PostSG.app_id)


async def start_edit_channels(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["editing"] = True
    await dialog_manager.switch_to(PostSG.channels)


async def start_edit_time(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    dialog_manager.dialog_data["editing"] = True
    await dialog_manager.switch_to(PostSG.schedule)


async def create_post(
    callback: types.CallbackQuery, button: Button, dialog_manager: DialogManager
) -> None:
    user = await repo.get_user_by_tg_id(callback.from_user.id)
    data = dialog_manager.dialog_data
    scheduled = data.get("scheduled_at")
    scheduled_dt = (
        datetime.datetime.fromisoformat(scheduled)
        if scheduled
        else None
    )
    post = await repo.create_post(
        user_id=user.id,
        text=data.get("text"),
        steam_id=data.get("app_id"),
        scheduled_at=scheduled_dt,
        tg_image_id=data.get("image_id"),
    )

    for cid in data.get("channels", []):
        channel = await repo.get_channel_by_chat_id(cid)
        await repo.link_post_channel(post.id, channel.id)

    if post.scheduled_at:
        schedule_post(post.scheduled_at, post.id, bot)
    else:
        await send_post(post.id, bot)

    await callback.message.answer("Пост создан")
    await dialog_manager.done()


# MARK: windows

creation_windows = [
    Window(
        Const("Введите текст поста:"),
        MessageInput(on_post_text),
        SwitchTo(Const("Назад"), id="c_cancel", state=PostSG.menu),
        state=PostSG.create,
    ),
    Window(
        Const("Отправьте изображение или пропустите:"),
        MessageInput(on_image),
        Button(Const("Без картинки"), id="skip_img", on_click=skip_image),
        Back(Const("Назад")),
        state=PostSG.image,
    ),
    Window(
        Const("Введите app id:"),
        TextInput(
            id="app_id",
            type_factory=int,
            on_success=on_app_id_success,
            on_error=on_app_id_error,
        ),
        Back(Const("Назад")),
        state=PostSG.app_id,
    ),
    Window(
        Const("Куда отправлять пост?"),
        Multiselect(
            checked_text=Format("✔️ {item.title} ({item.channel_id})"),
            unchecked_text=Format("{item.title} ({item.channel_id})"),
            id="m_channels",
            items="channels",
            item_id_getter=lambda c: c.channel_id,
            type_factory=int,
        ),
        Button(Const("Далее"), id="ch_next", on_click=on_channels_next),
        Back(Const("Назад")),
        state=PostSG.channels,
        getter=channels_getter,
    ),
]

schedule_windows = [
    Window(
        Const("Отправить сейчас или запланировать?"),
        Row(
            Button(Const("Сейчас"), id="now", on_click=send_now),
            SwitchTo(Const("Запланировать"), id="sched", state=PostSG.calendar),
        ),
        SwitchTo(Const("Отмена"), id="s_cancel", state=PostSG.menu),
        state=PostSG.schedule,
    ),
    Window(
        Const("Выберите дату."),
        Const("Дату можно отправить собщением в формате: 21-06-2025"),
        Calendar(id="cal", on_click=on_date_selected),
        MessageInput(on_datetime_input),
        SwitchTo(Const("Отмена"), id="cal_cancel", state=PostSG.menu),
        state=PostSG.calendar,
    ),
    Window(
        Const("Выберите время."),
        Const("Время можно отправить собщением в формате: 17:30"),
        Select(
            Format("{item}"),
            id="sel_time",
            items="times",
            item_id_getter=lambda x: x,
            on_click=on_time_select,
        ),
        MessageInput(on_datetime_input),
        SwitchTo(Const("Отмена"), id="time_cancel", state=PostSG.menu),
        getter=time_options_getter,
        state=PostSG.time,
    ),
    Window(
        Format("Текст:\n{text}"),
        Format("\nApp ID: <code>{app_id}</code>"),
        Format("Каналы: {channels}"),
        Format("Отправка: {scheduled_at}", when=F["scheduled_at"]),
        Format("Картинка: ✅", when=F["image_id"]),
        Format("Картинка: ❌", when=~F["image_id"]),
        Row(
            Button(Const("Текст"), id="edit_text", on_click=start_edit_text),
            Button(Const("Картинка"), id="edit_image", on_click=start_edit_image),
        ),
        Row(
            Button(Const("App"), id="edit_app", on_click=start_edit_app),
            Button(Const("Каналы"), id="edit_channels", on_click=start_edit_channels),
            Button(Const("Время"), id="edit_time", on_click=start_edit_time),
        ),
        Row(
            Button(Const("Создать"), id="create_post", on_click=create_post),
            SwitchTo(Const("Отмена"), id="conf_cancel", state=PostSG.menu),
        ),
        parse_mode=ParseMode.HTML,
        state=PostSG.confirm,
        getter=confirm_getter,
    ),
]

review_windows = [
    Window(
        Const("Тут будет просмотр постов."),
        SwitchTo(Const("Назад"), id="rev_cancel", state=PostSG.menu),
        state=PostSG.review,
    ),
]

edit_windows = [
    Window(
        Const("Тут будет редактирование поста."),
        SwitchTo(Const("Назад"), id="edit_cancel", state=PostSG.menu),
        state=PostSG.edit,
    ),
    Window(
        Const("Тут будет перенос поста."),
        SwitchTo(Const("Назад"), id="res_cancel", state=PostSG.menu),
        state=PostSG.reschedule,
    ),
]



dialog = Dialog(
    Window(
        Const("Управление постами:"),
        Row(
            SwitchTo(Const("Создать"), id="create", state=PostSG.create),
            SwitchTo(Const("Просмотр"), id="review", state=PostSG.review),
        ),
        Row(
            SwitchTo(Const("Редактировать"), id="edit", state=PostSG.edit),
            SwitchTo(Const("Перенести"), id="reschedule", state=PostSG.reschedule),
        ),
        Cancel(Const("Назад")),
        state=PostSG.menu,
    ),
    *creation_windows,
    *schedule_windows,
    *review_windows,
    *edit_windows,
)
