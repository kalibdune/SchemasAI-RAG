from abc import ABC, abstractmethod


class MessageServiceInterface(ABC):

    @abstractmethod
    async def connect(self, host: str, port: int, username: str, password: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish_message(self, queue: str, message: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def acknowledge_message(self, delivery_tag: str) -> None:
        raise NotImplementedError

    @abstractmethod
    async def message_dispatcher(self, message: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def close_connection(self) -> None:
        raise NotImplementedError
