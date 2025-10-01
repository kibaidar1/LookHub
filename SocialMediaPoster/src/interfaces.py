from abc import ABC, abstractmethod

from src.entities.looks import LookRead


class ServiceInterface(ABC):

    @abstractmethod
    async def send_new_post(self, look: LookRead) -> bool:
        raise NotImplementedError
