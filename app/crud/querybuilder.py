from inspect import signature

import sqlalchemy
from app.schemas.search import ConditionType
from sqlalchemy import and_, or_

OPERATORS = {
    "equal": lambda f, a: f.__eq__(a),
    "not_equal": lambda f, a: f.__ne__(a),
    "less": lambda f, a: f.__lt__(a),
    "greater": lambda f, a: f.__gt__(a),
    "less_or_equal": lambda f, a: f.__le__(a),
    "greater_or_equal": lambda f, a: f.__ge__(a),
    "in": lambda f, a: f.in_(a),
    "not_in": lambda f, a: f.notin_(a),
    "ends_with": lambda f, a: f.like("%" + a),
    "begins_with": lambda f, a: f.like(a + "%"),
    "contains": lambda f, a: f.like("%" + a + "%"),
    "not_contains": lambda f, a: f.notlike("%" + a + "%"),
    "not_begins_with": lambda f, a: f.notlike(a + "%"),
    "not_ends_with": lambda f, a: f.notlike("%" + a),
    "is_empty": lambda f: f.__eq__(""),
    "is_not_empty": lambda f: f.__ne__(""),
    "is_null": lambda f: f.is_(None),
    "is_not_null": lambda f: f.isnot(None),
    "between": lambda f, a: f.between(a[0], a[1]),
}


class Filter(object):
    def __init__(self, model, query: sqlalchemy.orm.Query, operators=None):
        self.model = model
        self.query = query
        self.operators = operators if operators else OPERATORS

    def querybuilder(self, rules):
        query, cond_list = self._make_query(self.query, rules)

        if (
            str(rules["condition"]).upper() == "OR"
            or rules["condition"] == ConditionType.OR
        ):
            operator = or_
        elif (
            str(rules["condition"]).upper() == "AND"
            or rules["condition"] == ConditionType.AND
        ):
            operator = and_

        if not len(cond_list) == 0:
            return query.filter(operator(*cond_list))
        else:
            return query.filter()

    def _make_query(self, query: sqlalchemy.orm.Query, rules):
        cond_list = []
        for cond in rules["rules"]:
            if "condition" not in cond:
                operator = cond["operator"]
                if operator not in OPERATORS:
                    raise NotImplementedError
                # try:
                #     model = self.model[cond['field'].split('.')[0]]
                # except KeyError:
                #     raise TableNotFoundError(cond['field'].split('.')[0])
                for table in query.column_descriptions:
                    if table["entity"] == self.model:
                        break
                else:
                    query = query.add_entity(self.model)
                field = getattr(self.model, cond["field"])
                function = OPERATORS[operator]
                arity = len(signature(function).parameters)
                if arity == 1:
                    cond_list.append(function(field))
                elif arity == 2:
                    cond_list.append(function(field, cond["value"]))
            else:
                query, cond_subrule = self._make_query(query, cond)
                if (
                    str(cond["condition"]).upper() == "OR"
                    or cond["condition"] == ConditionType.OR
                ):
                    operator = or_
                else:
                    operator = and_
                cond_list.append(operator(*cond_subrule))
        return query, cond_list
