from aiogram.enums import ContentType
from aiogram_dialog.api.entities import MediaAttachment, MediaId

from app.config import setting
from app.utils.utils import full_categories


def select_func(language : str):
    real_language_for_app = ""
    if language == "🇷🇺 Русский":
        real_language_for_app = "ru"
    else:
        real_language_for_app = "en"
    return real_language_for_app

async def get_content_getter(film, current_page, page_len, total_page, page, films):
    photo_url = setting.DEFAULT_IMG
    if film.get('poster_path'):
        photo_url = f"https://image.tmdb.org/t/p/w500{film.get('poster_path')}"
    overview = film.get('overview', 'Описание отсутствует')
    rating = film.get('vote_average', '0')
    if len(overview) > 400:
        overview = overview[:100] + "..."
    text = (
        f"🎬 <b>Название:</b> {film.get('title', 'Без названия')}\n\n"
        f"<b>📝 Сюжет:</b>\n<em> {overview}</em> \n\n"
        f"<b>⭐ Рейтинг:</b> {'★' * min(5, int(float(rating) // 2))}{'☆' * (5 - min(5, int(float(rating) // 2)))} <code>({rating}/10)</code>\n"
        f"<b>📅 Год выхода:</b> {film.get('release_date', 'Отсутствует')[:4] if film.get('overview') else 'Отсутствует'}\n ")
    return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(photo_url)),
            "page": current_page + 1,
            "total": len(films),
            "text": text,
            "show_button": True,
            "show_button_next_page": True if current_page + 1 == page_len and page < total_page else False,
            "show_button_previous_page": True if current_page + 1 == 1 and page > 1 else False,
            "show_button_next": True if current_page + 1 < page_len else False,
            "show_button_prev": True if current_page + 1 > 1 else False}

async def get_default_content():
    text = (f"❌ Фильм не найден\n"
            f"Попробуйте другой")
    return {"photo": MediaAttachment(type=ContentType.PHOTO, file_id=MediaId(setting.DEFAULT_IMG)),
            "text": text,
            "show_button": False,
            "show_button_next_page": False,
            "show_button_previous_page": False,
            "show_button_next": False,
            "show_button_prev": False}

def extract_chat_id_from_update(update_data: dict) -> int | None:
    """Извлекает chat_id из различных типов обновлений"""
    if not update_data:
        return None

    try:
        # Для обычного сообщения
        if 'message' in update_data:
            return update_data['message']['chat']['id']
        # Для callback query
        elif 'callback_query' in update_data:
            return update_data['callback_query']['message']['chat']['id']
        # Для других типов обновлений...
        elif 'edited_message' in update_data:
            return update_data['edited_message']['chat']['id']
    except (KeyError, TypeError):
        return None
    return None


async def create_complete_category_mapping(api_genres):
    result = []
    for genre in api_genres:
        genre_name = genre['name']
        beautiful_name = full_categories.get(genre_name, genre_name)
        result.append({
            'id': genre['id'],
            'name': beautiful_name,
            'original_name': genre_name,
            'callback_data': f"genre_{genre['id']}"
        })
    return result

async def get_genres(genres_list : list):
    genres_name = []
    if genres_list:
        for gen in genres_list:
            genres_name.append(gen.get("name", None))
    all_genres = ", ".join(genres_name)
    return all_genres