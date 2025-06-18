from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, SwitchTo, Cancel

from ..states import TemplateSG


templates_dialog = Dialog(
    Window(
        Const("Управление шаблонами:"),
        Row(
            SwitchTo(Const("Создать"), id="create", state=TemplateSG.create),
            SwitchTo(Const("Управлять"), id="manage", state=TemplateSG.manage),
        ),
        Cancel(Const("Назад")),
        state=TemplateSG.menu,
    ),
    Window(
        Const("Тут будет создание шаблона."),
        Cancel(Const("Назад")),
        state=TemplateSG.create,
    ),
    Window(
        Const("Тут будет управление шаблонами."),
        Cancel(Const("Назад")),
        state=TemplateSG.manage,
    ),
    Window(
        Const("Тут будет редактирование шаблона."),
        Cancel(Const("Назад")),
        state=TemplateSG.edit,
    ),
)
