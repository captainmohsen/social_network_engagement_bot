from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar

from pydantic import BaseModel


class ConditionType(str, Enum):
    OR = "or"
    AND = "and"


class OperatorType(str, Enum):
    EQUAL = "equal"
    NOT_EQUAL = "not_equal"
    LESS = "less"
    GREATER = "greater"
    LESS_OR_EQUAL = "less_or_equal"
    GREATER_OR_EQUAL = "greater_or_equal"
    IN = "in"
    NOT_IN = "not_in"
    ENDS_WITH = "ends_with"
    BEGINS_WITH = "begins_with"
    CONTAINS = "contains"
    NOT_CONTAINS = "not_contains"
    NOT_BEGINS_WITH = "not_begins_with"
    NOT_ENDS_WITH = "not_ends_with"
    IS_EMPTY = "is_empty"
    IS_NOT_EMPTY = "is_not_empty"
    IS_NULL = "is_null"
    IS_NOT_NULL = "is_not_null"
    BETWEEN = "between"


class RuleType(BaseModel):
    field: str
    operator: OperatorType
    value: Any = None


class FilterRuleType(BaseModel):
    condition: ConditionType = ConditionType.OR
    rules: List[RuleType]


class Search(BaseModel):
    filter: FilterRuleType
    page_number: int = 1
    page_size: int = 100
    item_sort: Optional[str]
    direction_sort: Optional[str]


ModelType = TypeVar("ModelType", bound=BaseModel)


class SearchResponse(BaseModel, Generic[ModelType]):
    result: List[ModelType]
    total: int
