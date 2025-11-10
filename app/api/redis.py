import json
from loguru import logger

from app.config import setting
import redis.asyncio as redis

class MoviesCached:
    def __init__(self):
        self.host = setting.REDIS_HOST
        self.port = setting.REDIS_PORT
        self.base_url = "https://api.themoviedb.org/3"

    async def get_redis_client(self):
        redis_client = redis.Redis(host=self.host,
                                   port=self.port,
                                   db=0,
                                   decode_responses=True)
        return redis_client

    async def get_content_for_fav(self, movies_id : int, language : str, client_movies):
        try:
            redis_key = f"{self.base_url}/movie/{movies_id}/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_info_by_movies(movies_id=movies_id, language=language)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_info_by_movies(movies_id=movies_id, language=language)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None

    async def get_user_fav(self, movies_id : int, language : str, client_movies, user_id : int):
        try:
            redis_key = f"{self.base_url}/movie/{movies_id}/{user_id}/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_info_by_movies(movies_id=movies_id, language=language, fav=True)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_info_by_movies(movies_id=movies_id, language=language, fav=True)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None

    async def get_content_by_category(self, genre_id : str, page : int, language : str, client_movies):
        try:
            redis_key = f"{self.base_url}/discover/movie/{genre_id}/{page}/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_category_by_id(genre_id=genre_id, page= page, language=language)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_category_by_id(genre_id=genre_id, page= page, language=language)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None

    async def get_content_search_movies(self, query : str, page : int, language : str, client_movies):
        try:
            redis_key = f"{self.base_url}/search/movie/{query}/{page}/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_search_movies(query=query, page=page, language=language)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_search_movies(query=query, page=page, language=language)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None

    async def get_content_top_movies(self, top : str, page : int, language : str, client_movies):
        try:
            redis_key = f"{self.base_url}/movie/{top}/{page}/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_top_movies(top= top, page=page, language=language)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_top_movies(top= top, page=page, language=language)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None

    async def get_content_actor_movies(self, actor_id: int, language: str, client_movies):
        try:
            redis_key = f"{self.base_url}/person/{actor_id}/movie_credits/{language}"
            async with await self.get_redis_client() as redis_client:
                cached_movies = await redis_client.get(redis_key)
                if cached_movies:
                    logger.debug("Данные получены из хэш")
                    return json.loads(cached_movies)
                else:
                    films = await client_movies.get_actor_movies(actor_id=actor_id, language=language)
                    await redis_client.set(name=redis_key, value=json.dumps(films), ex=3600)
                    logger.debug("Данные получены из api")
                    return films
        except Exception as e:
            try:
                films = await client_movies.get_actor_movies(actor_id=actor_id, language=language)
                return films
            except Exception as e:
                print(f"Ошибка в get_content_for_fav: {e}")
                return None