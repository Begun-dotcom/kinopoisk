from aiogram.fsm.state import StatesGroup, State


class SelectLanguageState(StatesGroup):
    select_language_state = State()

# -------------------------------------main_menu

class MainMenuState(StatesGroup):
    select_func_state = State()

# --------------------------------------cat_menu

class SelectCategoryState(StatesGroup):
    select_category_state = State()
    show_movies_by_category = State()
    show_info_by_movies = State()

#---------------------------------------search

class SelectSearchState(StatesGroup):
    input_search_state = State()
    show_movies_by_search = State()

# --------------------------------------top

class SelectTopMovies(StatesGroup):
    top_menu_state = State()
    show_movies_for_top = State()

# ---------------------------------------ramdom

class ShowRandomMovies(StatesGroup):
    show_random_state = State()

# ---------------------------------------actor
class SelectMoviesByActor(StatesGroup):
    input_name_state = State()
    show_all_actor = State()
    show_actor_movies = State()

#----------------------------------------room

class UserRoom(StatesGroup):
    user_menu_state = State()