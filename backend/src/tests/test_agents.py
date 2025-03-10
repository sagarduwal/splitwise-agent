import os
import pytest
from .agents.base_agent import BaseAgent
from .agents.receipt_agent import ReceiptAgent
from .agents.splitwise_agent import SplitwiseAgent


class TestBaseAgent(BaseAgent):
    def create_agent(self):
        return None  # Implement a mock agent for testing purposes

    def test_initialization(self):
        agent = TestBaseAgent(name="TestAgent", role="Tester")
        assert agent.name == "TestAgent"
        assert agent.role == "Tester"

    def test_load_config(self):
        os.environ["AGENT_MODEL"] = "gpt-4"
        os.environ["AGENT_TEMPERATURE"] = "0.7"
        os.environ["AGENT_MAX_ITERATIONS"] = "5"
        agent = TestBaseAgent(name="TestAgent", role="Tester")
        agent._load_config()
        assert agent.config["model"] == "gpt-4"
        assert agent.config["temperature"] == 0.7
        assert agent.config["max_iterations"] == 5

    def test_create_task(self):
        agent = TestBaseAgent(name="TestAgent", role="Tester")
        task = agent.create_task(description="Test task")
        assert task.description == "Test task"


class TestReceiptAgent(ReceiptAgent):
    def create_agent(self):
        return None  # Implement a mock agent for testing purposes

    def test_receipt_agent_initialization(self):
        agent = TestReceiptAgent()
        assert agent.name == "Receipt Analyzer"
        assert agent.role == "Expert Receipt Analyst and Data Extractor"


class TestSplitwiseAgent(SplitwiseAgent):
    def create_agent(self):
        return None  # Implement a mock agent for testing purposes

    def test_splitwise_agent_initialization(self):
        agent = TestSplitwiseAgent()
        assert agent.name == "Splitwise Manager"
        assert agent.role == "Financial Transaction Manager"


# Run the tests if this file is executed directly
if __name__ == "__main__":
    pytest.main()
