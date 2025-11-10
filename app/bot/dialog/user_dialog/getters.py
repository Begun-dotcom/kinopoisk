import asyncio
import random
from aiogram.enums import ContentType
from aiogram_dialog import DialogManager
from aiogram_dialog.api.entities import MediaAttachment, MediaId
from loguru import logger

from app.api.api import Movies
from app.api.redis import MoviesCached
from app.bot.kb.user_kb import start_kb
from app.config import setting
from app.dao.dao import BannerDao, UserDao, FavoriteDao
from app.utils.schemas import SUser, SUserLang
from app.utils.utils import language_text, main_text_ru, main_text_en, main_top_en, main_top_ru, sponsor_text
from app.utils.utils_func import get_content_getter, get_default_content, create_complete_category_mapping, get_genres


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
        image = MediaAttachment(ContentType.PHOTO, url=setting.DEFAULT_IMG)
        get_banner = await BannerDao(session=session).get_banner(name="menu")
        if get_banner:
            image = MediaAttachment(ContentType.PHOTO,file_id=MediaId(get_banner))
        return {"caption": caption, "text": btns, "image": image}
    except Exception as e:
        logger.error(f"Ошибка в language_getter: {e}")
        return None

# ------------------------------main_getter

async def main_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("🎬 <b>Главное меню «CINEMA WORLD»</b>\n"
                   "Выберите способ поиска идеального фильма: 🍿\n"
                   "<i>Данные предоставлены The Movie Database (TMDb)</i>")
        user_id = dialog_manager.start_data.get("user_id")
        language = dialog_manager.start_data.get("language", "ru")
        session = dialog_manager.middleware_data["session_with_commit"]
        user = UserDao(session=session)
        banner = BannerDao(session)
        image = MediaAttachment(ContentType.PHOTO,url=setting.DEFAULT_IMG)
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
        return None


#------------------------------category_getters

async def select_category_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = "Выберите категорию: 🎭"
        session = dialog_manager.middleware_data["session_without_commit"]
        language = dialog_manager.start_data.get("language")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        banner_dao = BannerDao(session)
        get_category, banner = await asyncio.gather(client.get_category(language=language),
                                                    banner_dao.get_banner(name="category"))
        image = MediaAttachment(ContentType.PHOTO, url=setting.DEFAULT_IMG)
        if banner:
            image = MediaAttachment(ContentType.PHOTO,file_id=MediaId(banner))
        category_content = await create_complete_category_mapping(get_category)
        return {"caption": caption, "text": category_content, "image": image}
    except Exception as e:
        logger.error(f"Ошибка в select_category_getter: {e}")
        return None

async def show_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        genre_id = dialog_manager.dialog_data["category_id"]
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        client_cached = MoviesCached()
        content = await client_cached.get_content_by_category(genre_id=genre_id, page= page, language=language, client_movies=client)
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
            dialog_manager.dialog_data["page_len"] = page_len
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            content = await get_content_getter(film, current_page, page_len, total_page, page, films)
            return content
        else:
            default_content = await get_default_content()
            return default_content

    except Exception as e:
        logger.error(f"Ошибка в show_movies_getter: {e}")
        default_content = await get_default_content()
        return default_content

async def show_info_getter(dialog_manager: DialogManager, **kwargs):
    try:
        movies_id = dialog_manager.start_data.get("movies_id")
        language = dialog_manager.start_data.get("language", "ru")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        client_cached = MoviesCached()
        films = await client_cached.get_content_for_fav(movies_id=movies_id,
                                                     language=language,
                                                     client_movies = client)
        if films:
            actors_list = []
            actors = films["credits"]["cast"]
            for actor in actors:
                actors_list.append(actor.get('name'))
            image = setting.DEFAULT_IMG
            overview = films.get("overview", "Описание отсутствует")
            if len(overview) > 400:
                overview = overview[:396] + "..."
            genres_list = films.get("genres", "Отсутствует")
            genres = await get_genres(genres_list=genres_list)
            if films.get("backdrop_path"):
                image = f"https://image.tmdb.org/t/p/w500{films.get('backdrop_path')}"
            text = (
                    f"<b>📋 КАРТОЧКА ФИЛЬМА</b>\n\n"
                    f"<b>🎬 Название:</b> {films.get('title', 'Не указано')}\n"
                    f"<b>📖 Описание:</b> <em> {overview}</em> \n\n "
                    f"<b>⏰ Продолжительность:</b> <em> {films.get('runtime', 'Не указано')} мин</em> \n "
                    f"<b>🎭 Жанр:</b> <em> {genres}</em> \n"
                    f"<b>⭐ Оценка:</b> {'★' * round(float(films.get('vote_average', 0)) / 2)} {'☆' * (5 - round(float(films.get('vote_average', 0)) / 2))} <code>({films.get('vote_average', '0')}/10)</code>\n"
                    f"<b>📅 Год выхода:</b> {films.get('release_date', '?')[:4] if films.get('release_date') else '?'}\n"
                    f"<b>💰 Сборы:</b> $ {films.get('revenue', 'Информация отсутствует')}\n\n"
                    f"<b>👤 В ролях:</b>\n" +
                    "\n".join([f"▫️ {actor}" for actor in actors_list[:8]])
            )

            if len(actors_list) > 8:
                text += f"\n▫️ ... и ещё {len(actors_list) - 8} актёров"
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(image)),
                    "text": text}
        else:
            text = (f"❌ Фильм не найден\n"
                    f"Попробуйте другой")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                    "text": text}

    except Exception as e:
        logger.error(f"Ошибка в show_movies_getter: {e}")
        text = (f"❌ Фильм не найден\n"
                f"Попробуйте другой")
        return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                "text": text}

# -------------------------------search

async def show_search_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        search_movies = dialog_manager.dialog_data.get("input_search")
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        client_cached = MoviesCached()
        content = await client_cached.get_content_search_movies(query=search_movies, page=page, language=language,
                                                              client_movies=client)
        films = content.get("result", None)
        total_page = content.get("total_pages", None)
        dialog_manager.dialog_data["total_pages"] = total_page
        logger.debug(f"По запросу {search_movies} получено {total_page} страниц")
        logger.debug(f"Страница {page} из {total_page}")
        if films:
            page_len = len(films)
            dialog_manager.dialog_data["page_len"] = page_len
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            film = films[current_page]
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            content = await get_content_getter(film, current_page, page_len, total_page, page, films)
            return content
        else:
            default_content = await get_default_content()
            return default_content
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        default_content = await get_default_content()
        return default_content

# -----------------------------top_getters

async def select_top_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("Выберите категорию топ 🔎:")
        session = dialog_manager.middleware_data["session_without_commit"]
        language = dialog_manager.start_data.get("language", "ru")
        image = setting.DEFAULT_IMG
        banner = await BannerDao(session).get_banner(name="category")
        if banner:
            image = banner
        text_for_app = ""
        if language == "ru":
            text_for_app = main_top_ru
        elif language == "en":
            text_for_app = main_top_en
        return {"caption": caption, "text": text_for_app, "photo" : MediaAttachment(type=ContentType.PHOTO,
                                                                                    file_id=MediaId(image))}
    except Exception as e:
        logger.error(f"Ошибка в select_top_getter: {e}")
        return None

async def show_top_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        top_movies = dialog_manager.dialog_data.get("select_top")
        page = dialog_manager.dialog_data.get("page", 1)
        language = dialog_manager.start_data.get("language", "ru")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        client_cached = MoviesCached()
        content = await client_cached.get_content_top_movies(top= top_movies, page=page, language=language,
                                                                client_movies=client)
        films = content.get("result", None)
        total_page = content.get("total_pages", None)
        dialog_manager.dialog_data["total_pages"] = total_page
        logger.debug(f"По {top_movies} получено {total_page} страниц")
        logger.debug(f"Страница {page} из {total_page}")
        if films:
            page_len = len(films)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            dialog_manager.dialog_data["page_len"] = page_len
            film = films[current_page]
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            content = await get_content_getter(film, current_page, page_len, total_page, page, films)
            return content
        else:
            default_content = await get_default_content()
            return default_content

    except Exception as e:
        logger.error(f"Ошибка в show_top_movies_getter: {e}")
        default_content = await get_default_content()
        return default_content

# --------------------------------------------random

async def show_random_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        topics_films = await client.get_random_movies(language=language)
        if topics_films:
            count = len(topics_films)
            random_page = random.randint(0, count-1)
            film = topics_films[random_page]
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            photo_url = setting.DEFAULT_IMG
            if film.get('poster_path'):
                photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}"
            overview = film.get('overview', 'Описание отсутствует')
            rating = film.get('vote_average', '0')
            if len(overview) > 400:
                overview = overview[:397] + "..."
            text = (
                f"🎬 <b>Название:</b> {film.get('title', 'Отсутствует')}\n\n"
                f"<b>📝 Сюжет:</b>\n<em> {overview}</em> \n\n"
                f"<b>⭐ Рейтинг:</b> {'★' * min(5, int(float(rating) // 2))}{'☆' * (5 - min(5, int(float(rating) // 2)))} <code>({rating}/10)</code>\n"
                f"<b>📅 Год выхода:</b> {film.get('release_date', 'Отсутствует')[:4] if film.get('overview') else 'Отсутствует'}\n\n "
                f"{sponsor_text}")
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "text": text,
                    "show_button_next": True
                    }
        else:
            text = (f"❌ Раздел временно не доступен\n"
                    f"Попробуйте позже")
            return {"text" : text,
                    "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                    "show_button_next": False
                    }

    except Exception as e:
        logger.error(f"Ошибка в show_random_movies_getter: {e}")
        text = (f"❌ Раздел временно не доступен\n"
                f"Попробуйте позже")
        return {"text": text,
                "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                "show_button_next": False
                }
# ------------------------------------------actor
async def input_actor_getter(dialog_manager: DialogManager, **kwargs):
    try:
        session = dialog_manager.middleware_data["session_without_commit"]
        banner_dao = BannerDao(session)
        banner = await banner_dao.get_banner(name="category")
        image = setting.DEFAULT_IMG
        if banner:
            image = banner
        return {"image": MediaAttachment(ContentType.PHOTO,file_id=MediaId(image))}
    except Exception as e:
        logger.error(f"Ошибка в select_category_getter: {e}")
        return None


async def show_all_actor_getter(dialog_manager: DialogManager, **kwargs):
    try:
        caption = ("👤 *Выберите актера 👇*")
        session = dialog_manager.middleware_data["session_with_commit"]
        language = dialog_manager.start_data.get("language", "ru")
        actor = dialog_manager.dialog_data["actor_name"]
        image = setting.DEFAULT_IMG
        get_banner = await BannerDao(session=session).get_banner(name="menu")
        if get_banner:
            image = get_banner
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        result = await client.find_all_actor_by_search(actor_name=actor, language=language)
        return {"caption": caption, "text": result, "image" : MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(image))}
    except Exception as e:
        logger.error(f"Ошибка: {e}")
        return None

async def show_actor_movies_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        actor_id = dialog_manager.dialog_data["actor_id"]
        aio_session = dialog_manager.middleware_data["aiohttp_session"]
        client = Movies(aio_session)
        client_cached = MoviesCached()
        result = await client_cached.get_content_actor_movies(actor_id=actor_id, language=language, client_movies=client)
        all_by_actor = result.get("cast", None)
        if all_by_actor:
            page_len = len(all_by_actor)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            current_page = item_page if item_page < page_len else 0
            dialog_manager.dialog_data["page_len"] = page_len
            film = all_by_actor[current_page]
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            photo_url = setting.DEFAULT_IMG
            if film.get('poster_path'):
                photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}"

            overview = film.get('overview', 'Описание отсутствует')
            rating = film.get('vote_average', '0')
            if len(overview) > 400:
                overview = overview[:397] + "..."
            text = (
                f"🎬 <b>Название:</b> {film.get('title', 'Отсутствует')}\n\n"
                f"<b>📝 Сюжет:</b>\n<em> {overview}</em> \n\n"
                f"<b>⭐ Рейтинг:</b> {'★' * min(5, int(float(rating) // 2))}{'☆' * (5 - min(5, int(float(rating) // 2)))} <code>({rating}/10)</code>\n"
                f"<b>📅 Год выхода:</b> {film.get('release_date', 'Отсутствует')[:4] if film.get('overview') else 'Отсутствует'}\n\n"
                f"{sponsor_text}")
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
                    "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                    "show_button": False,
                    "show_button_next": False,
                    "show_button_prev": False
                    }

    except Exception as e:
        logger.error(f"Ошибка в show_actor_movies_getter: {e}")
        text = (f"🎬 Фильмов с выбраным актером не найдено\n"
                f"Попробуйте еще раз")
        return {"text": text,
                "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                "show_button": False,
                "show_button_next": False,
                "show_button_prev": False
                }

# ---------------------------------------------room
async def user_room_getter(dialog_manager: DialogManager, **kwargs):
    try:
        session = dialog_manager.middleware_data["session_with_commit"]
        caption = f"{sponsor_text}"
        banner = setting.DEFAULT_IMG
        get_banner = await BannerDao(session=session).get_banner(name="menu")
        if get_banner:
            banner = get_banner
        image = MediaAttachment(ContentType.PHOTO, file_id=MediaId(banner))
        return {"caption": caption, "image": image}

    except Exception as e:
        logger.error(f"Ошибка в user_room_getter: {e}")
        return None

async def show_fav_getter(dialog_manager: DialogManager, **kwargs):
    try:
        language = dialog_manager.start_data.get("language", "ru")
        user_id = dialog_manager.start_data.get("user_id")
        session = dialog_manager.middleware_data["session_with_commit"]
        user_fav = await FavoriteDao(session=session).get_fav_mov(filters=SUser(telegram_id = user_id))
        if user_fav:
            aio_session = dialog_manager.middleware_data["aiohttp_session"]
            client = Movies(aio_session)
            client_cached = MoviesCached()
            len_movies_id = len(user_fav)
            item_page = dialog_manager.dialog_data.get("item_page", 0)
            page = item_page if item_page < len_movies_id else 0
            movies_id = user_fav[item_page]
            film = await client_cached.get_user_fav(movies_id=movies_id,
                                                        language=language,
                                                        client_movies=client,
                                                        user_id=user_id)
            dialog_manager.dialog_data["movies_id"] = film.get("id")
            dialog_manager.dialog_data["page_len"] = len_movies_id
            photo_url = setting.DEFAULT_IMG
            overview = film.get("overview", "Описание отсутствует")
            if len(overview) > 400:
                overview = overview[:396] + "..."
            if film.get('poster_path'):
                photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}"
            text = (
                    f"<b>📋 КАРТОЧКА ФИЛЬМА</b>\n\n"
                    f"<b>🎭 Название:</b> {film.get('title', 'Не указано')}\n\n"
                    f"<b>📖 Описание:</b> <em> {overview}</em> \n\n "
                    f"<b>⭐ Оценка:</b> {'★' * round(float(film.get('vote_average', 0)) / 2)} {'☆' * (5 - round(float(film.get('vote_average', 0)) / 2))} <code>({film.get('vote_average', '0')}/10)</code>\n"
                    f"<b>📅 Год выхода:</b> {film.get('release_date', '?')[:4] if film.get('release_date') else '?'}\n\n"
                    f"{sponsor_text}"
                    )
            return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
                    "page": page + 1,
                    "total": len_movies_id,
                    "text": text,
                    "show_button": True,
                    "show_button_next": True if page + 1 < len_movies_id else False,
                    "show_button_prev": True if page + 1 > 1 else False,
                    "show_button_delete" : True}


        else:
            text = f"❌ Список пуст\n"
            return {"text" : text,
                    "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                    "show_button": False,
                    "show_button_next": False,
                    "show_button_prev": False,
                    "show_button_delete" : False}

    except Exception as e:
        logger.error(f"Ошибка: {e}")
        text = (f"🎬 Произошла ошибка\n"
                f"Попробуйте еще раз")
        return {"text": text,
                "photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
                "show_button": False,
                "show_button_next": False,
                "show_button_prev": False
                }
