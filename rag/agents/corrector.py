from rag.agents.base import BaseAgent


class CorrectorAgent(BaseAgent):

    async def process(self, message): ...
