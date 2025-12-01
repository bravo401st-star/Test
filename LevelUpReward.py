import Entity
from abc import ABC, abstractmethod
from typing import Self

class Reward():
    def __init__(self) -> None:
        super().__init__()
        self.description = ""

    def SetDescription(self, desc: str) -> Self:
        self.description = desc
        return self

        