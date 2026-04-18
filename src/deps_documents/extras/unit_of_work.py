from abc import ABC, abstractmethod


class IUoW(ABC):
    def __enter__(self):
        self.open_transaction()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close_transaction()

    @abstractmethod
    def commit(self):
        pass

    @abstractmethod
    def rollback(self):
        pass

    @abstractmethod
    def open_transaction(self):
        pass

    @abstractmethod
    def close_transaction(self):
        pass
