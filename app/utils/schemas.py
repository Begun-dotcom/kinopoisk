from pydantic import BaseModel


class SUser(BaseModel):
    telegram_id : int

class SUserLang(SUser):
    language : str