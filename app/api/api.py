import asyncio
import random
from datetime import datetime

from aiolimiter import AsyncLimiter
import aiohttp
from loguru import logger
from app.config import setting
TMDB_RATE_LIMITER = AsyncLimiter(50, 1.0)  # 50 запросов в секунду
TMDB_BURST_LIMITER = AsyncLimiter(40, 0.1)  # 40 запросов за 0.1 секунду

class Movies:
    def __init__(self, session : aiohttp.ClientSession):
        self.session = session
        self.api_key = setting.API_KEY
        self.base_url = "https://api.themoviedb.org/3"

    async def get_category(self, language : str):
        try:
            params = {
                "api_key": self.api_key,
                "language": language
            }
            url_category = f"{self.base_url}/genre/movie/list"
            data = await self._make_request(url=url_category, params=params)
            category = data.get("genres", None)
            return category
        except Exception as e:
            logger.error(f"🔥 ошибка в get_category: {e}")
            return None

    async def _make_request(self, url: str, params: dict):
        """Общий метод для HTTP-запросов"""
        try:
            attempt = 0
            attempt_max = 2
            while attempt < attempt_max:
                content_error = False
                try:
                    async with TMDB_RATE_LIMITER:
                        async with TMDB_BURST_LIMITER:
                            async with self.session.get(url=url,proxy=setting.PROXY,params=params) as response:
                                logger.info(f"Попытка подключения к URL {url}, с параметрами {params}")
                                if response.status == 200:
                                    logger.debug(f"Успешное подключения к URL {url}, с параметрами {params}")
                                    return await response.json()
                                elif response.status == 429:  # Rate Limit
                                    retry_after = int(response.headers.get('Retry-After', 5))
                                    logger.warning(f"🎯 Rate limit, жду {retry_after} сек")
                                    await asyncio.sleep(retry_after)
                                    content_error = True

                                elif response.status == 401:  # Unauthorized
                                    logger.error("🔑 Ошибка аутентификации API ключа")
                                    content_error = True

                                elif response.status == 404:  # Not Found
                                    logger.warning(f"📭 Ресурс не найден: {url}")
                                    content_error = True

                                else:
                                    logger.error(f"❌ HTTP ошибка {response.status} для {url}")
                                    content_error = True

                except asyncio.TimeoutError:
                        logger.error(f"⏰ Таймаут запроса к {url}")
                        content_error = True
                except Exception as e:
                        logger.error(f"⚠️ Ошибка соединения: {e}")
                        content_error = True
                if content_error:
                    attempt += 1
                    logger.debug(f"Попытка запроса {attempt} из {attempt_max}")
                    await asyncio.sleep(1)
            logger.error(f"🚫 Все попытки исчерпаны для {url}")
            return None
        except Exception as e:
            logger.error(f"🔥 ошибка в _make_request: {e}")
            return None


    async def get_category_by_id(self, genre_id : str, page : int, language : str):
        try:
            params = {
                "api_key": self.api_key,
                "language": language,
                "page": page,
                "with_genres" : genre_id
            }
            params_for_pages = {
                "api_key": self.api_key,
                "language": language,
                "with_genres": genre_id
            }
            url_category_by_id = f"{self.base_url}/discover/movie"
            total_pages, data = await asyncio.gather(self.get_page(url=url_category_by_id, params=params_for_pages),
                                                         self._make_request(url=url_category_by_id, params=params))
            result = data.get("results", None)
            return {"total_pages" : total_pages,
                        "result" : result}

        except Exception as e:
            logger.error(f"🔥 ошибка в get_category_by_id: {e}")
            return None

    async def get_search_movies(self, query : str, page : int, language : str):
        try:
            params = {
                "api_key": self.api_key,
                "language": language,
                "page": page,
                "query": query
            }
            params_for_pages = {
                "api_key": self.api_key,
                "language": language,
                "query" : query
            }
            url_search_movies = f"{self.base_url}/search/movie"
            total_pages, data = await asyncio.gather(self.get_page(url=url_search_movies, params=params_for_pages),
                                                     self._make_request(url=url_search_movies, params=params))
            result = data.get("results", None)
            return {"total_pages": total_pages,
                    "result": result}

        except Exception as e:
            logger.error(f"🔥 ошибка в get_search_movies: {e}")
            return None

    async def get_top_movies(self, top : str, page : int = 1, language : str = "ru"):
        try:
            params = {
                "api_key": self.api_key,
                "language": language,
                "page": page,
            }
            params_for_page = {
                "api_key": self.api_key,
                "language": language,
            }
            url_top_movies = f"{self.base_url}/movie/{top}"
            total_pages, data = await asyncio.gather(self.get_page(url=url_top_movies, params=params_for_page),
                                                     self._make_request(url=url_top_movies, params=params))
            result = data.get("results", None)
            return {"total_pages": total_pages,
                    "result": result}

        except Exception as e:
            logger.error(f"🔥 ошибка в get_top_movies: {e}")
            return None


    async def get_random_movies(self, language : str = "ru", count: int = 20):
        try:
            current_year = datetime.now().year
            random_year = random.randint(2000, current_year)
            min_votes = 1000
            discover_url = f"{self.base_url}/discover/movie"
            params = {
                "api_key": self.api_key,
                "language": language,
                "page": 1,
                "primary_release_year": random_year,
                "vote_count.gte": min_votes,
                "sort_by": "popularity.desc"
            }
            initial_data = await self._make_request(discover_url, params)
            if not initial_data:
                logger.error(f"❌ Не удалось получить данные для года {random_year}")
                return None

            total_pages = initial_data.get("total_pages", 0)
            total_results = initial_data.get("total_results", 0)

            logger.info(f"📊 Год {random_year}: {total_results} фильмов, {total_pages} страниц")
            if total_pages == 0 or total_results == 0:
                logger.warning(f"🎯 Нет фильмов для года {random_year}, пробую другой год")
                return await self.get_random_movies(language, count)  # Рекурсивный вызов

            max_page = min(total_pages, 500)  # TMDB обычно ограничивает 500 страниц
            random_page = random.randint(1, max_page)

            params["page"] = random_page
            movies_data = await self._make_request(discover_url, params)

            if not movies_data:
                logger.error(f"❌ Не удалось получить фильмы для страницы {random_page}")
                return None

            movies = movies_data.get("results", [])
            logger.info(f"✅ Получено {len(movies)} фильмов за {random_year} год, страница {random_page}")

            valid_movies = [movie for movie in movies if movie.get('poster_path')]
            logger.info(f"🎭 Из них {len(valid_movies)} с постером")

            return valid_movies[:count] if valid_movies else None
        except Exception as e:
            logger.error(f"🔥 ошибка в get_top_movies: {e}")
            return None

    async def get_page(self,url : str, params : dict):
        try:
            data = await self._make_request(url, params)
            total_page = data.get("total_pages", 1)
            logger.info(f"✅ Успешное получение количество страниц по URL: {url}, кол. стр. {total_page}")
            return total_page

        except Exception as e:
            logger.error(f"🔥 ошибка в get_page: {e}")
            return 1

    async def find_actor_id(self, actor_name: str, language : str = "ru", page : int = 1):
        try:
            url = f"{self.base_url}/search/person"
            params_for_search = {
                "api_key": self.api_key,
                "query": actor_name,
                "page" : page,
                "language": language
            }
            data = await self._make_request(url=url, params=params_for_search)
            result = data.get("results", None)
            return result
        except Exception as e:
            logger.error(f"🔥 ошибка в find_actor_id: {e}")
            return None

    async def find_all_actor_by_search(self, actor_name : str, language : str = "ru"):
        try:
            url = f"{self.base_url}/search/person"
            params = {
                "api_key": self.api_key,
                "query": actor_name,
                "language": language
            }
            total_page = await self.get_page(url=url, params=params)
            tasks = []
            for page in range(1, total_page + 1):
                tasks.append(asyncio.create_task(self.find_actor_id(actor_name=actor_name, page=page)))
            result = await asyncio.gather(*tasks)
            actor_list = []
            for item in result:
                for item_2 in item:
                    actor_list.append({"id": item_2["id"],
                                       "name": item_2["name"]})
            return actor_list
        except Exception as e:
            logger.error(f"🔥 ошибка в find_actor_id: {e}")
            return None

    async def get_actor_movies(self, actor_id: int, language: str = "ru"):
        try:
            url = f"{self.base_url}/person/{actor_id}/movie_credits"
            params = {
                "api_key": self.api_key,
                "language": language
            }
            data = await self._make_request(url=url, params=params)
            return data
        except Exception as e:
            logger.error(f"🔥 ошибка в find_actor_id: {e}")
            return None

    async def get_info_by_movies(self, movies_id : int, fav : bool = False, language : str = "ru"):
        try:
            # params = {}
            if fav:
                params = {
                    "api_key": self.api_key,
                    "language": language,
                }
            else:
                params = {
                    "api_key": self.api_key,
                    "language": language,
                    "append_to_response" : "credits"
                 }
            url_info_by_movies = f"{self.base_url}/movie/{movies_id}"

            request = await self._make_request(url=url_info_by_movies, params=params)
            return request
        except Exception as e:
            logger.error(f"🔥 ошибка в get_category_by_id: {e}")
            return None

