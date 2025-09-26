from typing import Dict, Any
from orchestrator.registry import get_agent
from orchestrator.schemas import Task

class Orchestrator:
    def __init__(self):
        self._agents = {"customer_service": get_agent("customer_service")}

    def handle(self, message: str, agent_name: str = "customer_service") -> Dict[str, Any]:
        agent = self._agents[agent_name]
        return agent.handle(message)

    def run(self, task: Task) -> Dict[str, Any]:
        """Minimal task router to satisfy smoke tests.
        Currently routes all task types to the customer_service agent with a composed message.
        """
        try:
            message = f"Task={task.type}; payload={task.payload}"
        except Exception:
            message = str(task)
        return self.handle(message, agent_name="customer_service")
