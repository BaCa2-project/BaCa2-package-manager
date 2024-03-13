from abc import ABC, abstractmethod
from typing import Any, Iterable, Callable


class SettingsValidator(ABC):

    @abstractmethod
    def validate(self, value: Any) -> bool:
        pass

    def __call__(self, value: Any) -> bool:
        return self.validate(value)


# ========================================================================

class ValidatorNot(SettingsValidator):

    def __init__(self, validator: SettingsValidator):
        self.validator = validator

    def validate(self, value: Any) -> bool:
        return not self.validator.validate(value)


class ValidatorSeries(SettingsValidator):
    operator_t = Callable[[Iterable[bool]], bool]

    def __init__(self, operator: operator_t, operands: Iterable[SettingsValidator]):
        self.operator = operator
        self.operands = operands

    def validate(self, value: Any) -> bool:
        return self.operator(map(lambda validator: validator.validate(value), self.operands))


class ValidatorFunc(SettingsValidator):
    func_t = Callable[[Any], bool]

    def __init__(self, func: func_t):
        self.func = func

    def validate(self, value: Any) -> bool:
        return self.func(value)


# ========================================================================

def type_validator(types: type | tuple[type]) -> ValidatorFunc:
    return ValidatorFunc(lambda value: isinstance(value, types))


def range_validator(start: Any, stop: Any, include_start: bool = True, include_stop: bool = False) -> ValidatorFunc:
    return ValidatorFunc(lambda value: start < value < stop
                         or (include_start and value == start)
                         or (include_stop and value == stop))
