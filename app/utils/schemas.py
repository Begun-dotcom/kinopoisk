from pydantic import BaseModel


class SUser(BaseModel):
    telegram_id : int

class SUserLang(SUser):
    language : str

class SUserFav(BaseModel):
    telegram_id : int
    movies_id : int