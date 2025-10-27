from typing import Any

from aiogram import types
from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Button
from loguru import logger

from app.bot.dialog.admin_dialog.state import AdminPapel
from app.bot.dialog.user_dialog.state import MainMenuState, SelectCategoryState, SelectSearchState, SelectTopMovies, \
    ShowRandomMovies, SelectMoviesByActor
from app.utils.utils_func import select_func


async def on_check_language(call : types.CallbackQuery, widget : Any, dialog_manager : DialogManager, item_id : str):
    try:
        language = item_id
        real_language_for_app = select_func(language=language)
        if language == "⚙️ Адм.панель":
            await dialog_manager.start(state=AdminPapel.admin_menu)
        else:
            user_id = dialog_manager.start_data.get("user_id")
            await dialog_manager.start(state=MainMenuState.select_func_state, data={"language" : real_language_for_app,
                                                                                    "user_id" : user_id})

    except Exception as e:
        logger.error(f"Ошибка в on_check_language : {e}")

# --------------------------------------main_handler

async def on_check_main(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, select_menu: str):
    try:
        menu = select_menu
        select_language = dialog_manager.start_data.get("language")
        if menu in ["🎭 По жанрам","🎭 By Genres"]:
            await dialog_manager.start(state=SelectCategoryState.select_category_state,
                                       data={"language": select_language})
        elif menu in ["🔍 Поиск", "🔍 Search"]:
            await dialog_manager.start(state=SelectSearchState.input_search_state,
                                       data={"language": select_language})
        elif menu in ["🏆 Топ фильмов", "🏆 Top Movies"]:
            await dialog_manager.start(state=SelectTopMovies.top_menu_state,
                                       data={"language": select_language})
        elif menu in ["🎲 Случайный фильм", "🎲 Random Movie"]:
            await dialog_manager.start(state=ShowRandomMovies.show_random_state,
                                       data={"language": select_language})
        elif menu in ["👥 По персонам", "👥 By People"]:
            await dialog_manager.start(state=SelectMoviesByActor.input_name_state, data={"language": select_language})
        else:
            user_id = dialog_manager.start_data.get("user_id")


    except Exception as e:
        logger.error(f"Ошибка в on_check_main : {e}")

# ------------------------------------category_handler

async def on_check_category(call: types.CallbackQuery, widget: Any, dialog_manager: DialogManager, select_category: str):
    try:
        dialog_manager.dialog_data["category_id"] = select_category
        dialog_manager.dialog_data["item_page"] = 0
        await dialog_manager.switch_to(SelectCategoryState.show_movies_by_category)
    except Exception as e:
        logger.error(f"Ошибка в on_check_category : {e}")


async def on_page_change(call: types.CallbackQuery, widget: Button, dialog_manager: DialogManager):
    try:
         page = dialog_manager.dialog_data.get("page", 1)
         currant_page = dialog_manager.dialog_data.get("item_page", 0)
         page_len = dialog_manager.dialog_data["page_len"]
         total_page = dialog_manager.dialog_data["total_pages"]
         if widget.widget_id == "next":
                dialog_manager.dialog_data["item_page"] = min(currant_page + 1, page_len - 1)
         elif widget.widget_id == "prev":
                dialog_manager.dialog_data["item_page"] = max(currant_page - 1, 0)
         elif widget.widget_id == "next_page":
             if page < total_page:
                 dialog_manager.dialog_data["item_page"] = 0
                 dialog_manager.dialog_data["page"] = max(page + 1, 0)
         elif widget.widget_id == "prev_page":
             if page > 1:
                 dialog_manager.dialog_data["item_page"] = 19
                 dialog_manager.dialog_data["page"] = max(page - 1, 0)


    except Exception as e:
                logger.error(f"Ошибка в on_page_change : {e}")

# -----------------------------------search

async def input_search(message: types.Message, dialog_: Any, manager: DialogManager, data: str):
    try:
        manager.dialog_data["item_page"] = 0
        manager.dialog_data["page"] = 1
        manager.dialog_data["input_search"] = data
        await manager.switch_to(SelectSearchState.show_movies_by_search)
    except Exception as e:
        await message.answer("Не корректные данные!!!")
        logger.error(f"Ошибка в input_search : {e}")

# --------------------------------------top

async def select_top_movies(call : types.CallbackQuery, widget : Any, dialog_manager : DialogManager, top : str):
    try:
        dialog_manager.dialog_data["item_page"] = 0
        dialog_manager.dialog_data["page"] = 1
        dialog_manager.dialog_data["select_top"] = top
        await dialog_manager.switch_to(SelectTopMovies.show_movies_for_top)

    except Exception as e:
        logger.error(f"Ошибка в select_top_movies : {e}")

# ---------------------------------------random

async def next_movies(call: types.CallbackQuery, widget: Button, dialog_manager: DialogManager):
    try:
        pass

    except Exception as e:
                logger.error(f"Ошибка в next_movies : {e}")

# ---------------------------------------actor
async def get_actor_name_handler(message: types.Message, dialog_: Any, manager: DialogManager, data: str):
    try:
        manager.dialog_data["actor_name"] = data
        await manager.switch_to(SelectMoviesByActor.show_all_actor)
    except Exception as e:
        await message.answer("Не корректные данные!!!")
        logger.error(f"Ошибка в get_actor_name_handler : {e}")


async def get_actor_id_handler(call : types.CallbackQuery, widget : Any, dialog_manager : DialogManager, actor_id : str):
    try:
        dialog_manager.dialog_data["actor_id"] = actor_id
        await dialog_manager.switch_to(SelectMoviesByActor.show_actor_movies)
    except Exception as e:
        await call.answer("Не корректные данные!!!")
        logger.error(f"Ошибка в get_actor_id_handler : {e}")

async def on_page_change_for_actor(call: types.CallbackQuery, widget: Button, dialog_manager: DialogManager):
    try:
         currant_page = dialog_manager.dialog_data.get("item_page", 0)
         page_len = dialog_manager.dialog_data["page_len"]
         if widget.widget_id == "next":
                dialog_manager.dialog_data["item_page"] = min(currant_page + 1, page_len - 1)
         elif widget.widget_id == "prev":
                dialog_manager.dialog_data["item_page"] = max(currant_page - 1, 0)



    except Exception as e:
                logger.error(f"Ошибка в on_page_change : {e}")