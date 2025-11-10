from loguru import logger
from pydantic import BaseModel
from sqlalchemy import select, update, delete, func
from sqlalchemy.exc import SQLAlchemyError

from app.dao.base import BaseDao
from app.dao.models import Users, Banner, Favorites  # Убедитесь, что models импортирует Base из core

class UserDao(BaseDao):
    model = Users

    async def add(self, filters: BaseModel):
        try:
            filter_dict = filters.model_dump(exclude_unset=True)
            self._session.add(self.model(**filter_dict))
            await self._session.flush()
            logger.info(f"Данные в {self.model.__name__} добавлены успешно")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка добавления в таблицу {self.model}: {e}")

    async def get(self, filters : BaseModel):
        try:
            filter_dict = filters.model_dump(exclude_unset=True)
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Данные из {self.model.__name__} с параметрами {filters} получены успешно")
            return result.scalar_one_or_none()

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения данных из {self.model.__name__}: {e}")
            return None

    async def get_all_user(self, filters : BaseModel | None = None):
        try:
            filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
            query = select(func.count(self.model.id)).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Данные из {self.model.__name__} с параметрами {filters} получены успешно")
            return result.scalar()

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения данных из {self.model.__name__}: {e}")
            return None

    async def get_user_id(self, filters : BaseModel | None = None):
        try:
            filter_dict = filters.model_dump(exclude_unset=True) if filters else {}
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Данные из {self.model.__name__} с параметрами {filters} получены успешно")
            all_user = result.scalars().all()
            return [user.telegram_id for user in all_user]

        except SQLAlchemyError as e:
            logger.error(f"Ошибка получения данных из {self.model.__name__}: {e}")
            return None
        except Exception as e:
            logger.error(f"Ошибка получения данных из {self.model.__name__}: {e}")
            return None

class BannerDao(BaseDao):
    model = Banner

    async def add_banner(self, data: list):
        try:
            self._session.add_all([self.model(**name) for name in data])
            await self._session.commit()
            logger.info(f"Данные в {self.model.__name__} добавлены успешно")
        except SQLAlchemyError as e:
            await self._session.rollback()
            logger.error(f"Ошибка добавления в таблицу {self.model.__name__}: {e}")

    async def get_banner(self, name : str):
        try:
            query = select(self.model).filter_by(name=name)
            result = await self._session.execute(query)
            all_row = result.scalar_one_or_none()
            logger.info(f"Данные из {self.model.__name__} получены успешно")
            return all_row.image
        except Exception as e:
            logger.error(f"Ошибка получения из таблицы {self.model.__name__}: {e}")
            return None

    async def update(self, name : str, values : str):
        try:
            query = update(self.model).filter_by(name = name).values(image = values)
            await self._session.execute(query)
            await self._session.flush()
            logger.info(f"Данные в {self.model.__name__} с параметрами {values} обновлены успешно")
        except SQLAlchemyError as e:
            logger.error(f"Ошибка добавления в таблицу {self.model.__name__}: {e}")

class FavoriteDao(BaseDao):
    model = Favorites

    async def get_fav_mov(self, filters : BaseModel):
        try:
            filter_dict = filters.model_dump(exclude_unset=True)
            query = select(self.model).filter_by(**filter_dict)
            result = await self._session.execute(query)
            logger.info(f"Данные из {self.model.__name__} с параметрами {filters} получены успешно!!!")
            result = result.scalars().all()
            return [movies.movies_id for movies in result]
        except Exception as e:
            logger.error(f"Ошибка получения данных из {self.model.__name__}: {e}")
            return None

    async def delete_fav_mov(self, filters : BaseModel):
        try:
            filter_dict = filters.model_dump(exclude_unset=True)
            query = delete(self.model).filter_by(**filter_dict)
            await self._session.execute(query)
            logger.info(f"Данные из {self.model.__name__} с параметрами {filters} успешно удалены!!!")
            await self._session.flush()
        except Exception as e:
            logger.error(f"Ошибка удаления из {self.model.__name__}: {e}")
            return None

