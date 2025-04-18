from rag.agents.base import BaseAgent


class GeneratorAgent(BaseAgent):

    async def process(self, message): ...
