from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column
from app.core.base import Base

class Users(Base):
    telegram_id : Mapped[int] = mapped_column(BigInteger, unique=True)
    user_name : Mapped[str|None]
    first_name : Mapped[str|None]
    language: Mapped[str | None]

    def __repr__(self) -> str:
        return f"User(id={self.telegram_id}, {self.user_name}-{self.first_name}, language {self.language})"

class Banner(Base):
    name : Mapped[str] = mapped_column(String(50))
    image : Mapped[str | None]

    def __repr__(self):
        return f"<Banner(name={self.name}, image{self.image})>"

class Favorites(Base):
    telegram_id : Mapped[int] = mapped_column(BigInteger)
    movies_id : Mapped[int | None]

    def __repr__(self):
        return f"<Banner(name={self.telegram_id}, image{self.movies_id})>"