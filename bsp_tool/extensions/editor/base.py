from __future__ import annotations
import re
from typing import Callable, Dict, Union


# TODO: caches & write-once members
# -- lock _regex etc. to class definition
# -- store results of properties / MetaPattern regex generators


class Pattern:
    regex: str
    ValueType: Callable[str, object]
    value: object

    def __init__(self, *args, **kwargs):
        self.value = self.ValueType(*args, **kwargs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self!s}")'

    def __str__(self) -> str:
        return str(self.value)

    @classmethod
    def from_string(cls, string: str):
        match = re.match(cls.regex, string)
        assert match is not None, "string doesn't match regex"
        return cls(string)


def escape(string: str) -> str:
    special = ".?*+^$[](){}|\\"
    return "".join([(f"\\{c}" if c in special else c) for c in string])


class AttrMap:
    """mutable dict-like object"""

    def __init__(self, **kwargs):
        self._keys = tuple(kwargs.keys())
        for a, v in kwargs.items():
            setattr(self, a, v)

    def __eq__(self, other: AttrMap) -> bool:
        if isinstance(other, AttrMap):
            return self.as_dict() == other.as_dict()
        return False

    def __repr__(self) -> str:
        values = ", ".join([f"{k}={getattr(self, k)}" for k in self._keys])
        return f"{self.__class__.__name__}({values})"

    def as_dict(self) -> Dict[str, object]:
        return {k: getattr(self, k) for k in self._keys}


class MetaPattern:
    """container for regex patterns"""
    spec: str
    # ^ "SYMBOL name1 name2 name3"
    patterns: Dict[str, Union[Pattern, MetaPattern]]
    # ^ {"name1": PatternSubclass, "name2": MetaPattern}
    ValueType: Callable[Dict[str, object], object] = AttrMap
    value: object  # type should be ValueType
    # ^ value = ValueType(**{"key": value})

    def __init__(self, *args, **kwargs):
        attrs = {t: self.patterns[t]().value for t in self.spec.split() if t in self.patterns}
        attrs.update(dict(zip((t for t in self.spec.split() if t in self.patterns), args)))
        attrs.update(kwargs)
        self.value = self.ValueType(**attrs)

    def __repr__(self) -> str:
        return f'{self.__class__.__name__}("{self!s}")'

    def __str__(self) -> str:
        return " ".join([
            str(getattr(self.value, t)) if t in self.patterns else t
            for t in self.spec.split()])

    @classmethod
    def from_string(cls, string: str) -> MetaPattern:
        matches = re.match(cls.regex_groups(), string)
        assert matches is not None, f"string does not match pattern: {cls.regex_groups()}"
        return cls(**{t: cls.patterns[t].from_string(m).value for t, m in matches.groupdict().items()})

    # REGEX ASSEMBLERS

    @classmethod
    def regex(cls):
        """no groups; for matching"""
        regexes = list()
        for token in cls.spec.split(" "):
            if token in cls.patterns:
                pattern = cls.patterns[token]
                if issubclass(pattern, Pattern):
                    regexes.append(pattern.regex)
                elif issubclass(pattern, MetaPattern):
                    regexes.append(pattern.regex())
                else:
                    raise TypeError(f"{token}: {pattern} is invalid")
            else:  # symbol / keyword
                regexes.append(escape(token))
        return r"\s*".join(regexes)

    @classmethod
    def regex_groups(cls):
        """named top-level groups only"""
        regexes = list()
        for token in cls.spec.split(" "):
            if token in cls.patterns:
                pattern = cls.patterns[token]
                if issubclass(pattern, Pattern):
                    regexes.append(f"(?P<{token}>{pattern.regex})")
                elif issubclass(pattern, MetaPattern):
                    regexes.append(f"(?P<{token}>{pattern.regex()})")
                else:
                    raise TypeError()
            else:  # symbol / keyword
                regexes.append(escape(token))
        return r"\s*".join(regexes)
