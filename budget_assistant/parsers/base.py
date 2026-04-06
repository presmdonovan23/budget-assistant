# Abstract base class with parse interface, parse(file_path, account_id) -> list[Transaction].

from abc import ABC, abstractmethod

from budget_assistant.models import Transaction

class Parser(ABC):
    # init method takes in file_path and account id. sets cursor to 0.
    def __init__(self, file_path: str, account_id: str):
        self.file_path = file_path
        self.account_id = account_id
        self.cursor = 0

    @abstractmethod
    def parse(self) -> list[Transaction]:
        pass