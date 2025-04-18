from rag.agents.base import BaseAgent


class CoordinatorAgent(BaseAgent):

    async def process(self, message): ...
