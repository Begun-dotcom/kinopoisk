from aiogram_dialog import Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Group, Select, Row, Button, Back, Cancel
from aiogram_dialog.widgets.media import DynamicMedia
from aiogram_dialog.widgets.text import Format, Const

from app.bot.dialog.user_dialog.getters import language_getter, main_getter, select_category_getter, show_movies_getter, \
    show_search_movies_getter, select_top_getter, show_top_movies_getter, show_random_movies_getter, \
    show_actor_movies_getter, show_all_actor_getter
from app.bot.dialog.user_dialog.handler_dialog import on_check_language, on_check_main, on_check_category, \
    on_page_change, input_search, select_top_movies, next_movies, on_page_change_for_actor, \
    get_actor_name_handler, get_actor_id_handler
from app.bot.dialog.user_dialog.state import SelectLanguageState, MainMenuState, SelectCategoryState, SelectSearchState, \
    SelectTopMovies, ShowRandomMovies, SelectMoviesByActor


def language_window():
    return Window(
            DynamicMedia(selector="image"),
            Format(text="{caption}"),
            Group(Select(Format(text="{item}"),
                         id="select_language",
                         item_id_getter=lambda item: str(item),
                         items="text",
                         on_click= on_check_language),
                  id="group_items",
                  width=1,
                  ),
            getter=language_getter,
            state=SelectLanguageState.select_language_state
        )
# -------------------------------main_window

def main_window():
    return Window(
            DynamicMedia(selector="image"),
            Format(text="{caption}"),
            Group(Select(Format(text="{item}"),
                         id="select_main",
                         item_id_getter=lambda item: str(item),
                         items="text",
                         on_click= on_check_main),
                  id="group_items",
                  width=1,
                  ),
            getter=main_getter,
            state=MainMenuState.select_func_state
        )

# -------------------------for category

def select_category_window():
    return Window(
            DynamicMedia(selector="image"),
            Format(text="{caption}"),
            Group(Select(Format(text="★ {item[name]}"),
                         id="select_category",
                         item_id_getter=lambda item: str(item["id"]),
                         items="text",
                         on_click= on_check_category),
                  id="group_items",
                  width=2,
                  ),
            Cancel(Const("◀️ Назад")),
            getter=select_category_getter,
            state=SelectCategoryState.select_category_state
        )

def show_category_by_id():
    return Window(
        Format(text="{text}"),
        DynamicMedia(selector="photo"),
        Row(Button(Const(text="◀️"), id= "prev", on_click= on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_prev"]),
            Button(Const(text="Пред. стр◀️"), id="prev_page", on_click=on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_previous_page"]),
            Button(Format(text=f"{{page}}/{{total}}"), id="page",
                   when= lambda data, widget, manager:
                   data["show_button"]),
            Button(Const(text="▶️"), id= "next", on_click= on_page_change,
                   when= lambda data, widget, manager:
                   data["show_button_next"]),
            Button(Const(text="Сл. стр▶️"), id="next_page", on_click=on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_next_page"]),
            ),
        Back(Const("◀️ Назад")),
        getter=show_movies_getter,
        state=SelectCategoryState.show_movies_by_category
    )

# --------------------------------search

def input_search_window():
    return Window(
        Format(text="Введите название фильма:"),
        TextInput(id="input_search",
                  on_success=input_search,
                  type_factory=str),
        Group(Cancel(Const("◀️ Назад")),
              ),
        state= SelectSearchState.input_search_state

    )

def show_search_movies_window():
    return Window(
        Format(text="{text}"),
        DynamicMedia(selector="photo"),
        Row(
            Button(Const(text="◀️"), id= "prev", on_click= on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_prev"]),
                    Button(Const(text="Пред. стр◀️"), id="prev_page", on_click=on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_previous_page"]),
                    Button(Format(text=f"{{page}}/{{total}}"), id="page",
                    when= lambda data, widget, manager:
                    data["show_button"]),
                    Button(Const(text="▶️"), id= "next", on_click= on_page_change,
                    when= lambda data, widget, manager:
                    data["show_button_next"]),
                    Button(Const(text="Сл. стр▶️"), id= "next_page", on_click= on_page_change,
                    when= lambda data, widget, manager:
                    data["show_button_next_page"])
        ),
        Back(Const("◀️ Назад")),
        getter=show_search_movies_getter,
        state=SelectSearchState.show_movies_by_search
    )

# ----------------------------------top
def select_top_window():
    return Window(
            Format(text="{caption}"),
            Group(Select(Format(text="{item[name]}"),
                         id="select_top",
                         item_id_getter=lambda item: str(item["id"]),
                         items="text",
                         on_click= select_top_movies),
                  id="group_items_top",
                  width=1,
                  ),
            Cancel(Const("◀️ Назад")),
            getter=select_top_getter,
            state=SelectTopMovies.top_menu_state
        )

def show_top_window():
    return Window(
        Format(text="{text}"),
        DynamicMedia(selector="photo"),
        Row(Button(Const(text="◀️"), id= "prev", on_click= on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_prev"]),
            Button(Const(text="Пред. стр◀️"), id="prev_page", on_click=on_page_change,
                   when=lambda data, widget, manager:
                   data["show_button_previous_page"]),
            Button(Format(text=f"{{page}}/{{total}}"), id="page",
                   when= lambda data, widget, manager:
                   data["show_button"]),
            Button(Const(text="▶️"), id= "next", on_click= on_page_change,
                   when= lambda data, widget, manager:
                   data["show_button_next"]),
        Button(Const(text="Сл. стр▶️"), id= "next_page", on_click= on_page_change,
                   when= lambda data, widget, manager:
                   data["show_button_next_page"])
        ),
        Back(Const("Назад")),
        getter=show_top_movies_getter,
        state=SelectTopMovies.show_movies_for_top
    )

# --------------------------------------random

def show_random_window():
    return Window(
        Format(text="{text}"),
        DynamicMedia(selector="photo"),
        Button(Const(text="Следующий фильм▶️"), id= "next_movies", on_click= next_movies),
        Cancel(Const("Назад")),
        getter=show_random_movies_getter,
        state=ShowRandomMovies.show_random_state
    )
# -------------------------------------actor
def select_name_actor_window():
    return Window(
        Format(text="Введите имя актера:"),
        TextInput(id="input_search",
                  on_success=get_actor_name_handler,
                  type_factory=str),
        Group(Cancel(Const("Назад")),
              ),
        state= SelectMoviesByActor.input_name_state
    )

def show_all_actor_window():
    return Window(
            Format(text="{caption}"),
            Group(Select(Format(text="{item[name]}"),
                         id="select_top",
                         item_id_getter=lambda item: str(item["id"]),
                         items="text",
                         on_click= get_actor_id_handler),
                  id="group_items_top",
                  width=2,
                  ),
            getter=show_all_actor_getter,
            state=SelectMoviesByActor.show_all_actor
        )

def show_actor_movies_window():
    return Window(
        Format(text="{text}"),
        DynamicMedia(selector="photo"),
        Row(Button(Const(text="◀️"), id= "prev", on_click= on_page_change_for_actor,
                   when=lambda data, widget, manager:
                   data["show_button_prev"]),
            Button(Format(text=f"{{page}}/{{total}}"), id="page",
                   when= lambda data, widget, manager:
                   data["show_button"]),
            Button(Const(text="▶️"), id= "next", on_click= on_page_change_for_actor,
                   when= lambda data, widget, manager:
                   data["show_button_next"])
        ),
        Back(Const("Назад")),
        getter=show_actor_movies_getter,
        state=SelectMoviesByActor.show_actor_movies
    )


