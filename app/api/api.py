import asyncio
import json
import random
from datetime import datetime
from typing import Optional

import aiohttp
from aiohttp import ClientTimeout
from loguru import logger
from app.config import setting
# ?language = {language} & api_key = {self.api_key}


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
                    async with self.session.get(url=url,proxy=setting.PROXY,params=params) as response:
                        logger.info(f"Попытка подключения к URL {url}, с параметрами {params}")
                        if response.status == 200:
                            logger.debug(f"Успешное подключения к URL {url}, с параметрами {params}")
                            return await response.json()
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


    async def get_random_movies(self, language : str = "ru"):
        try:
            current_year = datetime.now().year
            random_year = random.randint(2000, current_year)
            page = 1
            min_votes = 1000
            test_query = f"{self.base_url}/discover/movie?api_key={self.api_key}&language={language}&page=1&primary_release_year={random_year}&vote_count.gte={min_votes}&sort_by=popularity.desc"
            try:
                async with self.session.get(url=test_query, proxy=setting.PROXY) as response:
                    logger.info(f"🔄 Попытка получения количество страниц рандомного фильма, год {random_year}")
                    if response.status == 200:
                        request = await response.json()
                        page = request.get("total_pages", 1)
                        logger.info(f"✅ Успешное получение количество страниц рандомного фильма, год {random_year}, стр. {page}")
                    else:
                        logger.error(f"❌ Ошибка получения страниц в get_top_movies: {response.status}")
            except asyncio.TimeoutError:
                logger.error(f"⏰ Таймаут запроса получения страниц в get_top_movies")
            except Exception as e:
                logger.error(f"⚠️ Неизвестная ошибка получения страниц при соединении: {e}")

            try:
                random_page = random.randint(1, page)
                url_random_movies = f"{self.base_url}/discover/movie?api_key={self.api_key}&language={language}&page={random_page}&primary_release_year={random_year}&vote_count.gte={min_votes}&sort_by=popularity.desc"
                async with self.session.get(url=url_random_movies, proxy=setting.PROXY) as response:
                    logger.info(f"🔄 Попытка получения рандомного фильма, год {random_year}, стр. {random_page}")
                    if response.status == 200:
                        request = await response.json()
                        logger.info(f"✅ Успешное получение рандомного фильма, год {random_year}, стр. {random_page}")
                        return request.get("results", None)
                    else:
                        logger.error(f"❌ Ошибка получения данных в get_top_movies: {response.status}")
                        return None
            except asyncio.TimeoutError:
                logger.error(f"⏰ Таймаут запроса в get_top_movies")
            except Exception as e:
                logger.error(f"⚠️ Неизвестная ошибка соединения: {e}")
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
            params = {}
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
#
# async def main():
#     try:
#         client = Movies()
#         # get_cat = await client.find_all_actor_by_search(actor_name="арнольд")
#         movie_data = await client.get_info_by_movies(movies_id=507244)
#         print(movie_data)
#         print(movie_data["title"])  # Название фильма
#         actors = movie_data["credits"]["cast"]
#         for actor in actors:
#             print(actor["name"])
#
#
#
#
#
#         # for a in get_cat:
#         #     print(a.get("name"))
#     except Exception as e:
#         logger.error(f"💥 Ошибка в main: {e}")
# #
# #119893
# #
# if __name__ == "__main__":
#     try:
#         asyncio.run(main())
#     except KeyboardInterrupt:
#         print("👋 Программа прервана пользователем")
#     except Exception as e:
#         print(f"💥 Критическая ошибка: {e}")
