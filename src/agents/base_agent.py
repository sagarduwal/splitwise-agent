from crewai import Agent
from abc import ABC, abstractmethod

class BaseAgent(ABC):
    """Base class for all agents in the system"""
    
    def __init__(self, name: str, role: str):
        self.name = name
        self.role = role
        self._agent = None

    @abstractmethod
    def create_agent(self) -> Agent:
        """Create and return a CrewAI agent"""
        pass

    @property
    def agent(self) -> Agent:
        """Get or create the CrewAI agent"""
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent
