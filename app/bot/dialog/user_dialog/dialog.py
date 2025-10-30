from aiogram_dialog import Dialog

from app.bot.dialog.user_dialog.windows import language_window, main_window, select_category_window, \
    show_category_by_id, input_search_window, show_search_movies_window, select_top_window, show_top_window, \
    show_random_window, show_actor_movies_window, select_name_actor_window, show_all_actor_window, \
    show_info_by_movies_windows, user_menu_windows, show_user_fav_window

select_language = Dialog(
    language_window()
)

main_menu = Dialog(
    main_window()
)

select_category = Dialog(
    select_category_window(),
    show_category_by_id(),

)

input_search = Dialog(
    input_search_window(),
        show_search_movies_window()
)

select_top = Dialog(
    select_top_window(),
    show_top_window()

)
show_random = Dialog(
    show_random_window()

)

show_movies_actor = Dialog(
select_name_actor_window(),
    show_all_actor_window(),
    show_actor_movies_window()
)

user_room = Dialog(
    user_menu_windows(),
)

user_fav_room = Dialog(
    show_user_fav_window()
)

show_info = Dialog(
    show_info_by_movies_windows()
)
