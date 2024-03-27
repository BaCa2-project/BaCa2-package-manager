import re
from abc import ABC, abstractmethod
from enum import Enum, auto
from pathlib import Path
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

    class Operator(Enum):
        AND = auto()
        OR = auto()
        XOR = auto()

    def __init__(self, operator: Operator, operands: Iterable[SettingsValidator]):
        match operator:
            case self.Operator.OR:
                self.operator = any
            case self.Operator.AND:
                self.operator = all
            case self.Operator.XOR:
                self.operator = lambda x: any(x) and not all(x)
            case _:
                raise NotImplemented
        self.operands = operands

    def validate(self, value: Any) -> bool:
        return self.operator(map(lambda validator: validator.validate(value), self.operands))


class ValidatorFunc(SettingsValidator):
    func_t = Callable[[Any], bool]

    def __init__(self, func: func_t, assert_type: type | tuple[type, ...] = None):
        self.assert_type = assert_type
        self.func = func

    @classmethod
    def decorate(cls, assert_type: type | tuple[type, ...] = None):
        return lambda func: cls(func, assert_type)

    def validate(self, value: Any) -> bool:
        if self.assert_type is not None and not isinstance(value, self.assert_type):
            return False
        return self.func(value)


# ========================================================================


class IsNone(SettingsValidator):

    def validate(self, value: Any) -> bool:
        return value is None


class IsNotEmpty(SettingsValidator):

    def validate(self, value: Any) -> bool:
        return bool(value)


class IsIn(SettingsValidator):

    def __init__(self, valid_values: Iterable):
        self.valid_values = valid_values

    def validate(self, value: Any) -> bool:
        return value in self.valid_values


class IsType(SettingsValidator):

    def __init__(self, type_: type | tuple[type, ...]):
        self.type_ = type_

    def validate(self, value: Any) -> bool:
        return isinstance(value, self.type_)


class IsExactly(SettingsValidator):

    def __init__(self, value: Any):
        self.value = value

    def validate(self, value: Any) -> bool:
        return value == self.value


class IsRegexMatch(IsType):

    def __init__(self, regex: str):
        super().__init__(str)
        self.regex = re.compile(regex)

    def validate(self, value: Any) -> bool:
        return super().validate(value) and bool(self.regex.match(value))


class IsAlphanumeric(IsRegexMatch):

    def __init__(self):
        super().__init__(r'^[a-zA-Z0-9]+$')


class IsPath(SettingsValidator):

    def validate(self, value: Any) -> bool:
        if isinstance(value, str):
            value = Path(value)
        return isinstance(value, Path) and value.exists()


class IsRestrictedList(SettingsValidator):

    def __init__(self, validator: SettingsValidator):
        self.validator = validator

    def validate(self, value: Any) -> bool:
        if not isinstance(value, (list, tuple)):
            return False
        return all(map(self.validator.validate, value))
