from typing import Any, Dict, Generic, List, Optional, Type, TypeVar, Union

from app.db.base_class import Base
from app.schemas.search import FilterRuleType
from fastapi.encoders import jsonable_encoder
from pydantic import UUID4, BaseModel
from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import desc,asc
from fastapi import HTTPException

from .querybuilder import Filter

ModelType = TypeVar("ModelType", bound=Base)
CreateSchemaType = TypeVar("CreateSchemaType", bound=BaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=BaseModel)





class CRUDBase(Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    def __init__(self, model: Type[ModelType]):
        """
        CRUD object with default methods to Create, Read, Update, Delete (CRUD).

        **Parameters**

        * `model`: A SQLAlchemy model class
        * `schema`: A Pydantic model (schema) class
        """
        self.model = model

    async def get(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        result = await db.execute(select(self.model).where(self.model.id == id))
        return result.scalar_one_or_none()

    async def get_multi(
        self, db: AsyncSession, *, skip: int = 0, limit: int = 1000000
    ) -> List[ModelType]:
        result = await db.execute(select(self.model).offset(skip).limit(limit))
        return result.scalars().all()

    async def search(
            self,
            db: AsyncSession,
            *,
            page_number: int = 1,
            page_size: int = 10,
            item_sort: str,
            direction_sort: str,
            rules: FilterRuleType
    ) -> tuple[int, List[ModelType]]:
        # Initialize the query using the async session
        query = Filter(self.model, select(self.model))
        result = query.querybuilder(rules)

        # Handle sorting direction and perform the query
        if direction_sort == "desc" and hasattr(self.model, item_sort):
            total_count = await db.scalar(select(func.count('*')).select_from(result))
            items_query = result.order_by(desc(getattr(self.model, item_sort))).offset(
                (page_number - 1) * page_size
            ).limit(page_size)
            items = (await db.execute(items_query)).scalars().all()

        elif direction_sort == "asc" and hasattr(self.model, item_sort):
            total_count = await db.scalar(select(func.count('*')).select_from(result))
            items_query = result.order_by(asc(getattr(self.model, item_sort))).offset(
                (page_number - 1) * page_size
            ).limit(page_size)
            items = (await db.execute(items_query)).scalars().all()

        else:
            total_count = await db.scalar(select(func.count('*')).select_from(result))
            items_query = result.offset((page_number - 1) * page_size).limit(page_size)
            items = (await db.execute(items_query)).scalars().all()

        return total_count, items

    async def create(self, db: AsyncSession, *, obj_in: CreateSchemaType) -> ModelType:
        obj_in_data = jsonable_encoder(obj_in.dict())

        db_obj = self.model(**obj_in_data)  # type: ignore
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def update(
        self,
        db: AsyncSession,
        *,
        db_obj: ModelType,
        obj_in: Union[UpdateSchemaType, Dict[str, Any]]
    ) -> ModelType:
        obj_data = jsonable_encoder(db_obj)
        if isinstance(obj_in, dict):
            update_data = obj_in
        else:
            update_data = obj_in.dict(exclude_unset=True)
        for field in obj_data:
            if field in update_data:
                setattr(db_obj, field, update_data[field])
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def remove(self, db: AsyncSession, *, id: str) -> ModelType:
        # Fetch the object from the database
        query = select(self.model).where(self.model.id == id)
        result = await db.execute(query)
        obj = result.scalar_one_or_none()

        if obj is None:
            raise HTTPException(status_code=404, detail=f"{self.model.__name__} with ID {id} not found")

        # Delete the object
        await db.delete(obj)
        await db.commit()
        return obj