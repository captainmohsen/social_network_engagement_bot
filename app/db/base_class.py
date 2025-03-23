from datetime import datetime
from typing import Any
import typing

from sqlalchemy import (
    Column,
    DateTime,
    event,
    func,
    inspect,
    orm,
)
from sqlalchemy.ext.declarative import as_declarative, declared_attr



class SoftDeleteMixin:
    deleted_at = Column(DateTime(timezone=True), nullable=True)

    def delete(self, deleted_at: datetime = None):
        self.deleted_at = deleted_at or datetime.now()

    def restore(self):
        self.deleted_at = None


@event.listens_for(orm.Query, "before_compile", retval=True)
def before_compile(query):
    include_deleted = query._execution_options.get("include_deleted", False)
    if include_deleted:
        return query

    for column in query.column_descriptions:
        entity = column["entity"]
        if entity is None:
            continue

        inspector = inspect(column["entity"])
        mapper = getattr(inspector, "mapper", None)
        if mapper and issubclass(mapper.class_, SoftDeleteMixin):
            query = query.enable_assertions(False).filter(entity.deleted_at.is_(None),)

    return query


@event.listens_for(SoftDeleteMixin, "load", propagate=True)
def load(obj, context):
    include_deleted = context.query._execution_options.get("include_deleted", False)
    if obj.deleted_at and not include_deleted:
        raise TypeError(
            f"Deleted object {obj} was loaded, did you use joined eager loading?"
        )


@as_declarative()
class Base(SoftDeleteMixin):
    id: Any
    created_at = Column(DateTime, nullable=False, server_default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    __name__: str

    def to_response_convention_dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)

        return d

    def to_dict(row):
        d = {}
        for column in row.__table__.columns:
            d[column.name] = getattr(row, column.name)

        return d

    # Generate __tablename__ automatically
    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()

    
    def _repr(self, **fields: typing.Dict[str, typing.Any]) -> str:
        '''
        Helper for __repr__
        '''
        field_strings = []
        at_least_one_attached_attribute = False
        for key, field in fields.items():
            try:
                field_strings.append(f'{key}={field!r}')
            except orm.exc.DetachedInstanceError:
                field_strings.append(f'{key}=DetachedInstanceError')
            else:
                at_least_one_attached_attribute = True
        if at_least_one_attached_attribute:
            return f"<{self.__class__.__name__}({','.join(field_strings)})>"
        return f"<{self.__class__.__name__} {id(self)}>"
