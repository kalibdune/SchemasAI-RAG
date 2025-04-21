import logging

from aio_pika import Message, connect
from aio_pika.abc import (
    AbstractChannel,
    AbstractConnection,
    AbstractIncomingMessage,
    AbstractQueue,
)

from rag.config import config

logger = logging.getLogger(__name__)


class RabbitServerService:
    connection: AbstractConnection
    channel: AbstractChannel
    queue: AbstractQueue

    def __init__(self, queue_name: str, url: str = config.rabbit.get_url) -> None:
        self.url = url
        self.queue_name = queue_name

    async def connect(self) -> "RabbitServerService":
        self.connection = await connect(self.url)
        self.channel = await self.connection.channel()
        self.queue = await self.channel.declare_queue(self.queue_name, durable=True)
        return self

    async def message_handler(self, callback) -> None:
        logger.info("Waiting for messages...")
        async with self.queue.iterator() as qiterator:
            message: AbstractIncomingMessage
            async for message in qiterator:
                try:
                    async with message.process(requeue=False):
                        assert message.reply_to is not None

                        response = await callback(message.body.decode("utf-8"))

                        await self.channel.default_exchange.publish(
                            Message(
                                body=response.encode("utf-8"),
                                correlation_id=message.correlation_id,
                                content_type="application/json",
                            ),
                            routing_key=message.reply_to,
                        )
                        print("Request completed")
                except Exception:
                    logging.exception("Processing error for message %r", message)
