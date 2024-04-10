"""
Copyright (c) Microsoft Corporation. All rights reserved.
Licensed under the MIT License.
"""

from __future__ import annotations

import json
from abc import ABC, abstractmethod
from copy import deepcopy
from typing import Any, Callable, List, Optional, Type, TypeVar, Union, overload

from botbuilder.core import Storage, TurnContext

from .todict import todict

T = TypeVar("T")


@overload
def state(_cls: None = ...) -> Callable[[Type[T]], Type[T]]: ...


@overload
def state(_cls: Type[T]) -> Type[T]: ...


def state(_cls: Optional[Type[T]] = None) -> Union[Callable[[Type[T]], Type[T]], Type[T]]:
    """
    @state\n
    class Example(State):
        ...
    """

    def wrap(cls: Type[T]) -> Type[T]:
        init = cls.__init__

        def __init__(self, *args, **kwargs) -> None:
            State.__init__(self, args, kwargs)

            if init is not None:
                init(self, *args, **kwargs)

        cls.__init__ = __init__  # type: ignore[method-assign]

        if not hasattr(cls, "save"):
            cls.save = State.save  # type: ignore[attr-defined]

        return cls

    if _cls is None:
        return wrap

    return wrap(_cls)


class State(dict, ABC):
    """
    State
    """

    __key__: str
    """
    The Storage Key
    """

    __deleted__: List[str]
    """
    Deleted Keys
    """

    def __init__(self, *args, **kwargs) -> None:  # pylint: disable=unused-argument
        super().__init__()
        self.__key__ = kwargs["__key__"] if "__key__" in kwargs else ""
        self.__deleted__ = []

        # copy public attributes that are not functions
        for name in dir(self):
            value = object.__getattribute__(self, name)

            if not name.startswith("_") and not callable(value):
                self[name] = deepcopy(value)

        for key, value in kwargs.items():
            if not key in ("__key__", "__deleted__"):
                self[key] = value

    async def save(self, _context: TurnContext, storage: Optional[Storage] = None) -> None:
        """
        Saves The State to Storage

        Args:
            context (TurnContext): the turn context.
            storage (Optional[Storage]): storage to save to.
        """
        if not storage or self.__key__ == "":
            return

        await storage.delete(self.__deleted__)
        await storage.write(
            {
                self.__key__: self.copy(),
            }
        )

        self.__deleted__ = []

    @classmethod
    @abstractmethod
    async def load(cls, context: TurnContext, storage: Optional[Storage] = None) -> "State":
        """
        Loads The State from Storage

        Args:
            context: (TurnContext): the turn context.
            storage (Optional[Storage]): storage to read from.
        """
        return cls()

    def __setitem__(self, key: str, item: Any) -> None:
        super().__setitem__(key, item)

        if key in self.__deleted__:
            self.__deleted__.remove(key)

    def __delitem__(self, key: str) -> None:
        if key in self and isinstance(self[key], State):
            self.__deleted__.append(self[key].__key__)

        super().__delitem__(key)

    def __setattr__(self, key: str, value: Any) -> None:
        if key.startswith("_") or callable(value):
            object.__setattr__(self, key, value)
            return

        self[key] = value

    def __getattr__(self, key: str) -> Any:
        return self[key]

    def __getattribute__(self, key: str) -> Any:
        if key in self:
            return self[key]

        return object.__getattribute__(self, key)

    def __delattr__(self, key: str) -> None:
        del self[key]

    def __str__(self) -> str:
        return json.dumps(todict(self))
