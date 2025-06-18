from aiogram_dialog import Dialog, Window, LaunchMode
from aiogram_dialog.widgets.text import Const
from aiogram_dialog.widgets.kbd import Row, Start

from ..states import AdminSG, MainMenuSG, PostSG, TemplateSG


main_menu_dialog = Dialog(
    Window(
        Const("Главное меню:"),
        Row(
            Start(Const("Посты"), id="posts", state=PostSG.menu),
        ),
        Row(
            Start(Const("Шаблоны"), id="templates", state=TemplateSG.menu),
        ),
        Row(
            Start(Const("Администрирование"), id="admin", state=AdminSG.menu),
        ),
        state=MainMenuSG.menu,
    ),
    launch_mode=LaunchMode.ROOT,
)
