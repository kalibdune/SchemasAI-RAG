import asyncio
import logging
from rag.agents.coordinator import CoordinatorAnswer, CoordinatorAgent
from rag.agents.schema_creator import SchemaCreatorAgent
from rag.model.regular_llm import RegularLLM
from rag.model.embedding import Embedding
from rag.store.vector import VectorStoreManager
from dataclasses import dataclass
from rag.config import config


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('rag.log'),
        logging.StreamHandler()
    ]
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


req = """Создай интеграцию, которая обращается к HTTP API по адресу https://api.example.com/data методом POST, передавая JSON {"userId": 12345, "includeDetails": true} с заголовками Authorization: Bearer abcdef123456 и Content-Type: application/json. Ответ от API представляет собой массив JSON-объектов с полями id, name, email, phone. Каждый объект должен быть преобразован в XML в виде: <userData><id>001</id><name>John Doe</name><email>john@example.com</email><phone>+1234567890</phone></userData>. Эти XML-сообщения необходимо отправлять в Kafka-брокер kafka-broker:9092 в топик user-xml-topic как строку без сериализации. При ошибке запроса к API необходимо сделать до 3 повторных попыток с интервалом 5 секунд между ними. Если отправка в Kafka не удалась, сообщение и текст ошибки должны быть записаны в файл error.log в формате: timestamp, XML-сообщение, текст ошибки. JSON-схема описывает структуру тела запроса: объект с полями userId (целое число) и includeDetails (булево значение), и структуру ответа: массив объектов с обязательными строковыми полями id, name, email, phone. XML-сообщения создаются строго по этой структуре. JSON-схема описывает только данные, а не конфигурацию интеграции."""

async def main():
    agents = setup_agent()
    coord_response: CoordinatorAnswer = await agents.coordinator.process({"query": req})
    logger.info(f"response from coordinator: {str(coord_response)}")

    if coord_response.action == "create":
        creator_response = await agents.creator.process({"query": coord_response.query})
        logger.info(f"response from creator: {creator_response}")
    else:
        logger.info("#########")
    
asyncio.run(main())