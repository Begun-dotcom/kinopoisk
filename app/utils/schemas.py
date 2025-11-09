from typing import Optional

from pydantic import BaseModel, Field, field_validator, model_validator


class SUser(BaseModel):
    telegram_id : int

class SUserLang(SUser):
    language : str

class SUserFav(BaseModel):
    telegram_id : int
    movies_id : int

class SSearchMovies(BaseModel):
    search: str = Field(
        min_length=2,
        max_length=80,
        description="Название фильма для поиска"
    )
    @model_validator(mode='before')
    @classmethod
    def validate_search_query(cls, values):
        if 'search' in values:
            search_text = values['search'].strip()

            if len(search_text) < 2:
                raise ValueError("🎬 Слишком короткое запрос. Введите хотя бы 2 символа")

            if len(search_text) > 80:
                raise ValueError("🎬 Слишком длинный запрос. Максимум 80 символов")

            values['search'] = search_text


        return values
