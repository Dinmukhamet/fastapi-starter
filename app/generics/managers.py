from typing import Generic, List, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

ModelType = TypeVar("ModelType")


class QuerySetMixin(Generic[ModelType]):
    model: Type[ModelType]

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self.query = select(self.model)

    def filter(self, *args, **kwargs):
        query = self.query.filter(*args)

        for field, criteria in kwargs.items():
            query = query.filter(operators.eq(getattr(self.model, field), criteria))

        self.query = query
        return self

    async def all(self, db: AsyncSession) -> List[ModelType]:
        return (await db.execute(self.query)).all()

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance
