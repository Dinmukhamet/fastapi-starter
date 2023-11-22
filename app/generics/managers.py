import warnings
from typing import Generic, List, Type, TypeVar

from sqlalchemy import ClauseElement, delete, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql import operators

ModelType = TypeVar("ModelType")


class QuerySetMixin(Generic[ModelType]):
    model: Type[ModelType]
    _filter_conditions: List[ClauseElement]

    def __init__(self, model: Type[ModelType]):
        self.model = model
        self._filter_conditions = []

    def filter(self, *args, **kwargs):
        self._filter_conditions = list(*args)

        for field, criteria in kwargs.items():
            self._filter_conditions.append(
                operators.eq(getattr(self.model, field), criteria)
            )

        return self

    async def all(self, db: AsyncSession) -> List[ModelType]:
        query = select(self.model).filter(*self._filter_conditions)
        return (await db.execute(query)).all()

    async def create(self, db: AsyncSession, **kwargs) -> ModelType:
        instance = self.model(**kwargs)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(self, db: AsyncSession, **kwargs) -> ModelType:
        if not self._filter_conditions:
            warnings.warn("No filter conditions applied!")
        query = (
            update(self.model)
            .filter(*self._filter_conditions)
            .values(**kwargs)
            .returning(self.model)
        )
        return (await db.execute(query)).scalars().one_or_none()

    async def get(self, db: AsyncSession, *args, **kwargs) -> ModelType:
        self.filter(*args, **kwargs)
        query = select(self.model).filter(*self._filter_conditions)
        return (await db.execute(query)).one()

    async def delete(self, db: AsyncSession, *args, **kwargs) -> ModelType:
        self.filter(*args, **kwargs)
        query = delete(self.model).filter(*self._filter_conditions)
        return await db.execute(query)
