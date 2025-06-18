from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, SwitchTo, Cancel

from ..states import PostSG


post_dialog = Dialog(
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
    Window(
        Const("Тут будет создание поста."),
        Cancel(Const("Назад")),
        state=PostSG.create,
    ),
    Window(
        Const("Тут будет просмотр постов."),
        Cancel(Const("Назад")),
        state=PostSG.review,
    ),
    Window(
        Const("Тут будет редактирование поста."),
        Cancel(Const("Назад")),
        state=PostSG.edit,
    ),
    Window(
        Const("Тут будет перенос поста."),
        Cancel(Const("Назад")),
        state=PostSG.reschedule,
    ),
)
