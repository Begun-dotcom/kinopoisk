import asyncio
import random
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from loguru import logger

from app.api.api import Movies
from app.bot.kb.user_kb import start_kb
from app.config import setting
from app.dao.dao import BannerDao, UserDao
from app.utils.schemas import SUser, SUserLang
from app.utils.utils import language_text, main_text_ru, main_text_en, main_top_en, main_top_ru


# ---------------------------------select_language
async def language_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = (
            "<b>🎬 ДОБРО ПОЖАЛОВАТЬ В МИР КИНО! 👋</b>\n\n"
            "✨ <i>КИНОТЕАТР «CINEMA WORLD»</i> ✨\n\n"
            "📝 Для начала давайте выберем язык общения: 🌍"
        )
        user_id = dialog_manager.start_data.get("user_id")
        session = dialog_manager.middleware_data["session_with_commit"]
        btns = start_kb(data=language_text, user_id=user_id)
        image = MediaAttachment(ContentType.PHOTO, url="https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")
        get_banner = await BannerDao(session=session).get_banner(name="menu")
        if get_banner:
            image = MediaAttachment(ContentType.PHOTO,file_id=MediaId(get_banner))
        return {"caption": caption, "text": btns, "image": image}
    except Exception as e:
        logger.error(f"Ошибка в language_getter: {e}")

# ------------------------------main_getter

async def main_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("🎬 <b>Главное меню «CINEMA WORLD»</b>\n"
                   "Выберите способ поиска идеального фильма: 🍿")
        user_id = dialog_manager.start_data.get("user_id")
        language = dialog_manager.start_data.get("language")
        session = dialog_manager.middleware_data["session_with_commit"]
        user = UserDao(session=session)
        banner = BannerDao(session)
        image = MediaAttachment(ContentType.PHOTO,
                                url="https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")
        text_btn = []
        if language == "ru":
            text_btn = main_text_ru
        elif language == "en":
            text_btn = main_text_en
        btns = start_kb(data=text_btn, user_id=user_id)
        user, banner = await asyncio.gather(user.get(filters=SUser(telegram_id = user_id)),
                                    banner.get_banner(name="menu"))
        if user is None:
            await UserDao(session).add(filters=SUserLang(telegram_id = user_id, language = language))
        if banner:
            image = MediaAttachment(ContentType.PHOTO,file_id=MediaId(banner))
        return {"caption": caption, "text": btns, "image": image}
    except Exception as e:
        logger.error(f"Ошибка в main_getter: {e}")


#------------------------------category_getters

async def select_category_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = "Выберите категорию: 🎭"
        user_id = dialog_manager.start_data.get("user_id")
        session = dialog_manager.middleware_data["session_without_commit"]
        language = dialog_manager.start_data.get("language")
        client = Movies()
        banner_dao = BannerDao(session)
        get_category, banner = await asyncio.gather(client.get_category(language=language),
                                                    banner_dao.get_banner(name="cat"))
        image = MediaAttachment(ContentType.PHOTO, url="https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")
        if banner:
            image = MediaAttachment(ContentType.PHOTO,file_id=MediaId(banner))
        return {"caption": caption, "text": get_category, "image": image}
    except Exception as e:
        logger.error(f"Ошибка в select_category_getter: {e}")

async def show_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        genre_id = dialog_manager.dialog_data["category_id"]
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        client = Movies()
        content = await client.get_category_by_id(genre_id=genre_id, page= page, language=language)
        films = content.get("result", None)
        total_page = content.get("total_pages", None)
        dialog_manager.dialog_data["total_pages"] = total_page
        logger.debug(f"По id {genre_id} получено {total_page} страниц")
        logger.debug(f"Страница {page} из {total_page}")
        if films:
            page_len = len(films)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            film = films[current_page]
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            photo_url = setting.DEFAULT_IMG
            if film.get('poster_path'):
                photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}"
            dialog_manager.dialog_data["page_len"] = page_len
            title = film.get('title', 'Без названия')
            overview = film.get('overview', 'Описание отсутствует')
            rating = film.get('vote_average', '0')
            if len(overview) > 400:
                overview = overview[:397] + "..."
            text = (
                f"🎬 <b>Название:</b> {film.get('title', 'Отсутствует')}\n\n"
                f"<b>📝 Сюжет:</b>\n{overview}\n\n"
                f"<b>⭐ Рейтинг:</b> {'★' * min(5, int(float(rating) // 2))}{'☆' * (5 - min(5, int(float(rating) // 2)))} <code>({rating}/10)</code>"
            )
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "page": current_page + 1,
                    "total": len(films),
                    "text": text,
                    "show_button": True,
                    "show_button_next_page": True if current_page + 1 == page_len else False,
                    "show_button_previous_page": True if current_page + 1 == 1 and page > 1 else False,
                    "show_button_next": True if current_page + 1 < page_len else False,
                    "show_button_prev": True if current_page + 1 > 1 else False}
        else:
            text = (f"🎬 Фильмов не найден\n"
                    f"Попробуйте другой")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")),
                    "text": text,
                    "show_button": False,
                    "show_button_next_page": False,
                    "show_button_previous_page": False,
                    "show_button_next": False,
                    "show_button_prev": False}

    except Exception as e:
        logger.error(f"Ошибка в show_movies_getter: {e}")

async def show_info_getter(dialog_manager: DialogManager, **kwargs):
    try:
        movies_id = dialog_manager.dialog_data["movies_id"]
        language = dialog_manager.start_data.get("language", "ru")
        client = Movies()
        films = await client.get_info_by_movies(movies_id = movies_id, language=language)
        if films:
            actors_list = []
            actors = films["credits"]["cast"]
            for actor in actors:
                actors_list.append(actor.get('name'))
            image = setting.DEFAULT_IMG
            if films.get("poster_path"):
                image = f"https://image.tmdb.org/t/p/w500{films.get('poster_path')}"
            text = (
                    f"<b>📋 КАРТОЧКА ФИЛЬМА</b>\n\n"
                    f"<b>🎭 Название:</b> {films.get('title', 'Не указано')}\n"
                    f"<b>⭐ Оценка:</b> {'★' * round(float(films.get('vote_average', 0)) / 2)} {'☆' * (5 - round(float(films.get('vote_average', 0)) / 2))} <code>({films.get('vote_average', '0')}/10)</code>\n"
                    f"<b>📅 Год выхода:</b> {films.get('release_date', '?')[:4] if films.get('release_date') else '?'}\n\n"
                    f"<b>👤 В ролях:</b>\n" +
                    "\n".join([f"▫️ {actor}" for actor in actors_list[:8]])
            )

            if len(actors_list) > 8:
                text += f"\n▫️ ... и ещё {len(actors_list) - 8} актёров"
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(image)),
                    "text": text}
        else:
            text = (f"🎬 Фильмов не найден\n"
                    f"Попробуйте другой")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")),
                    "text": text}

    except Exception as e:
        logger.error(f"Ошибка в show_movies_getter: {e}")

# -------------------------------search

async def show_search_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        search_movies = dialog_manager.dialog_data.get("input_search")
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        client = Movies()
        content = await client.get_search_movies(query=search_movies, page=page, language=language)
        films = content.get("result", None)
        total_page = content.get("total_pages", None)
        dialog_manager.dialog_data["total_pages"] = total_page
        logger.debug(f"По запросу {search_movies} получено {total_page} страниц")
        logger.debug(f"Страница {page} из {total_page}")
        if films:
            page_len = len(films)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            film = films[current_page]
            photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}" if film.get('poster_path') else "https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg"
            dialog_manager.dialog_data["page_len"] = page_len
            text = (f"Название: {film.get('title', "Название отсутствует") if film.get('title') else "Название отсутствует"}\n "
                    f"Описание: {film.get('overview', 'Описание отсутствует') if film.get('overview') else 'Описание отсутствует'}\n "
                    )
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "page": current_page + 1,
                    "total": len(films),
                    "text": text,
                    "show_button": True,
                    "show_button_next_page": True if current_page + 1 == page_len else False,
                    "show_button_previous_page": True if current_page + 1 == 1 and page > 1 else False,
                    "show_button_next": True if current_page + 1 < page_len else False,
                    "show_button_prev": True if current_page + 1 > 1 else False}
        else:
            text = (f"🎬 Фильмов не найден\n"
                    f"Попробуйте другой")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")),
                    "text": text,
                    "show_button": False,
                    "show_button_next_page": False,
                    "show_button_previous_page": False,
                    "show_button_next": False,
                    "show_button_prev": False}
    except Exception as e:
        logger.error(f"Ошибка: {e}")

# -----------------------------top_getters

async def select_top_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("Выберите категорию топ 🔎:")
        language = dialog_manager.start_data.get("language", "ru")
        text_for_app = ""
        if language == "ru":
            text_for_app = main_top_ru
        elif language == "en":
            text_for_app = main_top_en
        user_id = dialog_manager.start_data.get("user_id")
        return {"caption": caption, "text": text_for_app}


    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def show_top_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        top_movies = dialog_manager.dialog_data.get("select_top")
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        client = Movies()
        content = await client.get_top_movies(top= top_movies, page=page, language=language)
        films = content.get("result", None)
        total_page = content.get("total_pages", None)
        dialog_manager.dialog_data["total_pages"] = total_page
        logger.debug(f"По {top_movies} получено {total_page} страниц")
        logger.debug(f"Страница {page} из {total_page}")
        if films:
            page_len = len(films)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            film = films[current_page]
            photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}" if film.get('poster_path') else "https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg"
            dialog_manager.dialog_data["page_len"] = page_len
            text = (f"Название: {film.get('title', "Название отсутствует") if film.get('title') else "Название отсутствует"}\n "
                    f"Описание: {film.get('overview', 'Описание отсутствует') if film.get('overview') else 'Описание отсутствует'}\n "
                    )
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "page": current_page + 1,
                    "total": len(films),
                    "text": text,
                    "show_button": True,
                    "show_button_next_page": True if current_page + 1 == page_len else False,
                    "show_button_previous_page": True if current_page + 1 == 1 and page > 1 else False,
                    "show_button_next": True if current_page + 1 < page_len else False,
                    "show_button_prev": True if current_page + 1 > 1 else False}
        else:
            text = (f"🎬 Фильмов не найден\n"
                    f"Попробуйте другой")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")),
                    "text": text,
                    "show_button": False,
                    "show_button_next_page": False,
                    "show_button_previous_page": False,
                    "show_button_next": False,
                    "show_button_prev": False}

    except Exception as e:
        logger.error(f"Ошибка: {e}")

# --------------------------------------------random

async def show_random_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        client = Movies()
        topics_films = await client.get_random_movies(language=language)
        if topics_films:
            count = len(topics_films)
            random_page = random.randint(0, count-1)
            film = topics_films[random_page]
            photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}" if film.get('poster_path') else "https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg"
            text = (f"📺 Название: {film.get('title', "Название отсутствует") if film.get('title') else "Название отсутствует"}\n "
                    f"📖 Описание: {film.get('overview', 'Описание отсутствует') if film.get('overview') else 'Описание отсутствует'}\n "
                    f"⭐ Рейтинг: {film.get('vote_average', 'Рейтинг отсутствует') if film.get('overview') else 'Рейтинг отсутствует'} /10\n "
                    f"📅 Год: {film.get('release_date', 'Отсутствует') if film.get('overview') else 'Отсутствует'}\n ")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "text": text,
                    }
        else:
            text = (f"🎬 Фильмов не найден\n"
                    f"Попробуйте еще раз")
            return {"text" : text,
                    "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg"))
                    }

    except Exception as e:
        logger.error(f"Ошибка: {e}")

# ------------------------------------------actor

async def show_all_actor_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("Выберите актера:")
        language = dialog_manager.start_data.get("language", "ru")
        actor = dialog_manager.dialog_data["actor_name"]
        user_id = dialog_manager.start_data.get("user_id")
        client = Movies()
        result = await client.find_all_actor_by_search(actor_name=actor, language=language)
        return {"caption": caption, "text": result}


    except Exception as e:
        logger.error(f"Ошибка: {e}")

async def show_actor_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        actor_id = dialog_manager.dialog_data["actor_id"]
        client = Movies()
        result = await client.get_actor_movies(actor_id=actor_id, language=language)
        all_by_actor = result.get("cast", None)
        if all_by_actor:
            page_len = len(all_by_actor)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            film = all_by_actor[current_page]
            photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}" if film.get('poster_path') else "https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg"
            dialog_manager.dialog_data["page_len"] = page_len
            text = (f"Название: {film.get('title', 'Название отсутствует') if film.get('title') else 'Название отсутствует'}\n "
                    f"Описание: {film.get('overview', 'Описание отсутствует') if film.get('overview') else 'Описание отсутствует'}\n "
                    )
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "page": current_page + 1,
                    "total": len(all_by_actor),
                    "text": text,
                    "show_button": True,
                    "show_button_next": True if current_page + 1 < page_len else False,
                    "show_button_prev": True if current_page + 1 > 1 else False}
        else:
            text = (f"🎬 Фильмов с выбраным актером не найдено\n"
                    f"Попробуйте еще раз")
            return {"text" : text,
                    "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId("https://i.pinimg.com/originals/b5/d4/30/b5d4300ae81c9252ca5d534aef1b4f3d.jpg")),
                    "show_button": False,
                    "show_button_next": False,
                    "show_button_prev": False
                    }

    except Exception as e:
        logger.error(f"Ошибка: {e}")

# ---------------------------------------------room
async def user_room_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        session = dialog_manager.middleware_data["session_with_commit"]
        caption = "Спонсор MTDb"
        banner = setting.DEFAULT_IMG
        get_banner = await BannerDao(session=session).get_banner(name="menu")
        if get_banner:
            banner = get_banner
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(banner))
        return {"caption": caption, "image": image}

    except Exception as e:
        logger.error(f"Ошибка в user_room_getter: {e}")