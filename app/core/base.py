from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, declared_attr

class Base(DeclarativeBase):
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    created: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now())
    updated: Mapped[str] = mapped_column(TIMESTAMP, server_default=func.now(), onupdate=func.now())

    @declared_attr.directive
    def __tablename__(self):
        name = self.__name__.lower()
        if name.endswith('s'):
            return name + 'es'
        return name + 's'