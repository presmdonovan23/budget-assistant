# Abstract base class with parse interface, parse(file_path, account_id) -> list[Transaction].

from abc import ABC, abstractmethod

from budget_assistant.models import Transaction

class Parser(ABC):
    @abstractmethod
    def parse(self, file_path: str, account_id: str) -> list[Transaction]:
        pass