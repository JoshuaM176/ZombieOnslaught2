from abc import ABC, abstractmethod


class Equipment(ABC):
    def __init__(self) -> None: ...

    @property
    @abstractmethod
    def price(self) -> int: ...
