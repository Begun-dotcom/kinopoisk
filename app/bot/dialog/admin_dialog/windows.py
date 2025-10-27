from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput
from aiogram_dialog.widgets.kbd import Group, Select, Cancel

from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialog.admin_dialog.getters import admin_log_getter
from app.bot.dialog.admin_dialog.handlers import on_check_admin_menu, add_image_banner
from app.bot.dialog.admin_dialog.state import AdminPapel, AdminPanelBanner


def get_log_window():
    return Window(Format(text="{caption}"),
        Group(Select(Format(text="{item}"),
                     id="select_admin_items",
                     item_id_getter=lambda item: str(item),
                     items="text",
                     on_click= on_check_admin_menu),
              id="group_admin_items",
              width=1,
              ),
        Cancel(Const(text="Назад")),
        getter=admin_log_getter,
        state=AdminPapel.admin_menu
    )

def add_banner_windows():
    return Window(
        Const(text="Установите баннер рабочего стола"),
        MessageInput(content_types=ContentType.PHOTO, func=add_image_banner),
        Group(Cancel(Const(text="Отмена")) ),
        state=AdminPanelBanner.add_banner_state
    )
