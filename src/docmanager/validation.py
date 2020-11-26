import pydantic
from functools import wraps
from horseman.response import Response
from typing import List, Dict


def validate_partial_model(data, model, *fieldnames):

    class Validator:
        __config__ = pydantic.BaseConfig
        __fields__: Dict[str, pydantic.fields.ModelField] = {
            name: field for name, field in model.__fields__.items()
            if name in fieldnames
        }
        __pre_root_validators__: List = []
        __post_root_validators__: List = []

    return pydantic.validate_model(Validator, data)


class ValidationError(Response, Exception):
    pass


def catch_pydantic_exception(func):
    @wraps(func)
    def exceptions_catcher(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except pydantic.ValidationError as exc:
            error = {
                'type': 'Model validation',
                'name': f'{exc.model.__module__}.{exc.model.__name__}',
                'errors': exc.errors()
            }
            raise ValidationError.to_json(400, error)
    return exceptions_catcher
