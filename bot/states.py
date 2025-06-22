from aiogram.fsm.state import State, StatesGroup


class MainMenuSG(StatesGroup):
    """Main menu dialog states."""

    menu = State()


class PostSG(StatesGroup):
    """Post management dialog states."""

    menu = State()

    # creation
    create = State()
    image = State()
    app_id = State()
    channels = State()
    schedule = State()
    calendar = State()
    time = State()
    buttons = State()
    confirm = State()

    # management
    review = State()
    reschedule = State()
    edit = State()


class TemplateSG(StatesGroup):
    """Template management dialog states."""

    menu = State()
    create = State()
    manage = State()
    edit = State()


class AdminSG(StatesGroup):
    """Administration dialog states."""

    menu = State()
    channels = State()
    channel_info = State()
    create_channel = State()
    users = State()
    user_info = State()
    change_role = State()
    register_codes = State()
    show_codes = State()
    show_code = State()
