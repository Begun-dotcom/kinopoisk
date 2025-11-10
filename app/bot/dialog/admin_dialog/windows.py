from aiogram.enums import ContentType
from aiogram_dialog import Window
from aiogram_dialog.widgets.input import MessageInput, TextInput
from aiogram_dialog.widgets.kbd import Group, Select, Cancel

from aiogram_dialog.widgets.text import Const, Format

from app.bot.dialog.admin_dialog.getters import admin_log_getter, select_table_getter, get_status_getter
from app.bot.dialog.admin_dialog.handlers import on_check_admin_menu, add_image_banner, select_table, set_rec
from app.bot.dialog.admin_dialog.state import AdminPapel, AdminPanelBanner, AdminUserCount, AdminRec


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

def input_name_table_window():
    return Window(
        Const(text="Виберите стол"),
        Group(Select(Format(text="★ {item[name]}"),
                     id="select_category",
                     item_id_getter=lambda item: str(item["name"]),
                     items="text",
                     on_click=select_table),
              id="group_items",
              width=2,
              ),
        Cancel(Const("↩️ Назад")),
        getter=select_table_getter,
        state=AdminPanelBanner.select_table_state
    )


def add_banner_windows():
    return Window(
        Const(text="Установите баннер рабочего стола"),
        MessageInput(content_types=ContentType.PHOTO, func=add_image_banner),
        Group(Cancel(Const(text="Отмена")) ),
        state=AdminPanelBanner.add_banner_state
    )

def get_status_window():
    return Window(
        Format(text="{text}"),
        Cancel(Const(text="🏠 Главное меню")),
        getter=get_status_getter,
        state=AdminUserCount.get_user_state
    )


def set_rec_window():
    return Window(
        Format(text="Введите текст рекламы"),
        TextInput(id="input_search",
                  on_success=set_rec,
                  type_factory=str),
        Group(Cancel(Const("↩️ Назад")),
              ),
        state= AdminRec.set_rec_state

    )