from typing import Any, Callable, Generic, Optional, Type, TypeVar, Union

T = TypeVar("T")


class _ClassProperty(Generic[T]):
    """
    A property on a class (rather than on an instance), holding a value of type `T`.
    """

    def __init__(
        self,
        fget: "classmethod[Any, [], T]",
        fset: "Optional[classmethod[Any, [T], None]]" = None,
    ):
        self.fget = fget
        self.fset = fset

    def __get__(self, obj: Any, klass: Optional[Type] = None) -> T:
        if klass is None:
            klass = type(obj)
        return self.fget.__get__(obj, klass)()

    def __set__(self, obj: Any, value: T) -> None:
        if self.fset is None:
            raise AttributeError("Can't set class property (no setter)")
        klass = type(obj)
        return self.fset.__get__(obj, klass)(value)

    def setter(
        self, fset: "Union[Callable[[Any, T], None], classmethod[Any, [T], None]]"
    ) -> "_ClassProperty[T]":
        """
        Defines the setter for a class property
        """
        if not isinstance(fset, classmethod):
            fset = classmethod(fset)
        self.fset = fset
        return self


def classproperty(
    fget: "Union[Callable[[Any], T], classmethod[Any, [], T]]",
) -> _ClassProperty[T]:
    """
    Declares a new class property with the decorated getter.
    """
    if not isinstance(fget, classmethod):
        fget = classmethod(fget)
    return _ClassProperty(fget)


class _ClassPropertyMeta(type):
    def __setattr__(self, key: str, value: Any) -> None:
        obj = getattr(self, key, None)
        if isinstance(obj, _ClassProperty):
            return obj.__set__(self, value)

        return super().__setattr__(key, value)
