from datetime import datetime

from sqlalchemy import DateTime, func
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.orm import Mapped, mapped_column, registry

from .managers import QuerySetMixin

mapper_registry = registry()


class QuerySetMeta(DeclarativeMeta):
    @property
    def objects(self):
        return QuerySetMixin(self)


class Base(metaclass=QuerySetMeta):
    __abstract__ = True

    registry = mapper_registry
    metadata = mapper_registry.metadata
    __init__ = mapper_registry.constructor


class Model(AsyncAttrs, Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.timezone("Asia/Bishkek", func.now()),
    )
    objects: QuerySetMixin
