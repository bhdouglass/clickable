from abc import ABC, abstractmethod


class Query(ABC):
    @abstractmethod
    def is_met(self):
        pass

    @abstractmethod
    def get_user_instructions(self):
        pass
