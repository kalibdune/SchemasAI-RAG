import asyncio
import json
import logging
from dataclasses import dataclass

from rag.agents.coordinator import CoordinatorAgent, CoordinatorAnswer
from rag.agents.schema_creator import CreatorAnswer, SchemaCreatorAgent
from rag.config import config
from rag.message_broker.rabbit import RabbitServerService
from rag.model.embedding import Embedding
from rag.model.regular_llm import RegularLLM
from rag.store.vector import VectorStoreManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("rag.log"), logging.StreamHandler()],
)

logger = logging.getLogger(__name__)


@dataclass
class Agents:
    coordinator: CoordinatorAgent
    creator: SchemaCreatorAgent


def setup_agent():
    llm = RegularLLM()
    embedding = Embedding()
    store = VectorStoreManager(embedding)

    coordinator = CoordinatorAgent(llm, embedding)
    creator = SchemaCreatorAgent(llm, store)

    return Agents(coordinator, creator)


agents = setup_agent()
# req = """Создай интеграцию, которая обращается к HTTP API по адресу https://api.example.com/data методом POST, передавая JSON {"userId": 12345, "includeDetails": true} с заголовками Authorization: Bearer abcdef123456 и Content-Type: application/json. Ответ от API представляет собой массив JSON-объектов с полями id, name, email, phone. Каждый объект должен быть преобразован в XML в виде: <userData><id>001</id><name>John Doe</name><email>john@example.com</email><phone>+1234567890</phone></userData>. Эти XML-сообщения необходимо отправлять в Kafka-брокер kafka-broker:9092 в топик user-xml-topic как строку без сериализации. При ошибке запроса к API необходимо сделать до 3 повторных попыток с интервалом 5 секунд между ними. Если отправка в Kafka не удалась, сообщение и текст ошибки должны быть записаны в файл error.log в формате: timestamp, XML-сообщение, текст ошибки. JSON-схема описывает структуру тела запроса: объект с полями userId (целое число) и includeDetails (булево значение), и структуру ответа: массив объектов с обязательными строковыми полями id, name, email, phone. XML-сообщения создаются строго по этой структуре. JSON-схема описывает только данные, а не конфигурацию интеграции."""


async def target(message):
    message = json.loads(message)

    agents = setup_agent()
    coord_response: CoordinatorAnswer = await agents.coordinator.process(
        {"query": message["content"]}
    )
    logger.info(f"response from coordinator: {str(coord_response)}")

    if coord_response.action == "create":
        creator_response: CreatorAnswer = await agents.creator.process(
            {"query": coord_response.query}
        )
        logger.info(f"response from creator: {creator_response}")
        message = {
            "content": creator_response.raw_response,
            "sender_type": "ai",
            "chat_id": message["chat_id"],
        }
    else:
        message = {
            "content": "Мы пока не можем дать ответ 😏",
            "sender_type": "ai",
            "chat_id": message["chat_id"],
        }

    return json.dumps(message)


async def main():
    rabbit_server = await RabbitServerService(queue_name="message_queue").connect()
    await rabbit_server.message_handler(target)


asyncio.run(main())
