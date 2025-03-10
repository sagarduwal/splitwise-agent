from crewai import Agent, Task, Crew, Process
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from dotenv import load_dotenv
import os
import json
import logging

# Load environment variables
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class BaseAgent(ABC):
    """Base class for all agents in the system"""

    def __init__(self, name: str, role: str, goal: Optional[str] = None):
        self.name = name
        self.role = role
        self.goal = goal or f"Assist with {role} tasks effectively and accurately"
        self._agent = None
        self._crew = None
        self._load_config()

    def _load_config(self) -> None:
        """Load agent configuration from environment variables"""
        try:
            self.config = {
                "model": os.getenv("AGENT_MODEL", "gpt-4"),
                "temperature": float(os.getenv("AGENT_TEMPERATURE", "0.5")),
                "max_iterations": int(os.getenv("AGENT_MAX_ITERATIONS", "3")),
                "verbose": os.getenv("DEBUG", "False").lower() == "true",
            }
        except ValueError as e:
            logger.error(f"Invalid configuration value: {str(e)}")
            raise ValueError(f"Invalid configuration value: {str(e)}")

    @abstractmethod
    def create_agent(self) -> Agent:
        """Create and return a CrewAI agent"""
        pass

    def create_base_agent(self, **kwargs) -> Agent:
        """Create a base agent with common configuration"""
        # Remove parameters that are set in __init__ or config to avoid conflicts
        self._remove_conflicting_params(kwargs)

        # Format tools as basic functions
        if "tools" in kwargs:
            kwargs["tools"] = self._format_tools(kwargs.pop("tools", []))

        try:
            return Agent(
                name=self.name,
                role=self.role,
                goal=self.goal,
                verbose=self.config["verbose"],
                allow_delegation=True,
                llm_model=self.config["model"],
                temperature=self.config["temperature"],
                max_iterations=self.config["max_iterations"],
                **kwargs,
            )
        except Exception as e:
            logger.error(f"Failed to create agent: {str(e)}. Config: {self.config}")
            raise Exception(f"Failed to create agent: {str(e)}. Config: {self.config}")

    def create_task(
        self,
        description: str,
        expected_output: Optional[str] = None,
        agent: Optional[str] = None,
        tools: Optional[List[str]] = None,
    ) -> Task:
        """Create a new task for the agent

        Args:
            description: Task description
            expected_output: Expected format and structure of the output
            agent: Optional agent to use for the task
            tools: Optional tools to use for the task

        Returns:
            Task: Configured task instance

        Raises:
            Exception: If task creation fails
        """
        self._validate_task_params(description, expected_output)

        task_args = self._prepare_task_args(description, expected_output, agent, tools)

        try:
            return Task(**task_args)
        except Exception as e:
            logger.error(f"Failed to create task: {str(e)}")
            raise Exception(f"Failed to create task: {str(e)}")

    def execute_tasks(self, tasks: List[Task]) -> List[str]:
        """Execute a sequence of tasks and return their results"""
        if not tasks:
            return []

        try:
            crew = self.get_crew(tasks)
            results = crew.kickoff()
            return self._handle_results(results)
        except Exception as e:
            logger.error(f"Tasks failed: {str(e)}")
            return [f"Tasks failed: {str(e)}"]

    @property
    def agent(self) -> Agent:
        """Get or create the CrewAI agent"""
        if self._agent is None:
            self._agent = self.create_agent()
        return self._agent

    def get_crew(self, tasks: List[Task]) -> Crew:
        """Create a crew with the agent and specified tasks

        Args:
            tasks: List of tasks to be executed by the crew

        Returns:
            Crew: Configured crew instance with the agent and tasks
        """
        crew = Crew(
            agents=[self.agent],
            tasks=tasks,
            verbose=self.config.get("verbose", False),
            process=Process.sequential,
        )
        return crew

    def execute_single_task(self, task: Task) -> str:
        """Execute a single task and return its result

        Args:
            task: Task to be executed

        Returns:
            str: Result of the task execution
        """
        try:
            crew = self.get_crew([task])
            result = crew.kickoff()
            return self._handle_single_result(result)
        except Exception as e:
            logger.error(f"Task execution failed: {str(e)}")
            raise Exception(f"Task execution failed: {str(e)}")

    def _remove_conflicting_params(self, kwargs):
        for param in [
            "name",
            "role",
            "goal",
            "verbose",
            "llm_model",
            "temperature",
            "max_iterations",
        ]:
            kwargs.pop(param, None)

    def _format_tools(self, tools):
        return [
            {"name": tool.__name__, "function": lambda *args, t=tool: t(*args)}
            for tool in tools
            if callable(tool)
        ]

    def _validate_task_params(self, description, expected_output):
        if not description:
            raise ValueError("Task description cannot be empty.")
        if expected_output and not isinstance(expected_output, str):
            raise ValueError("Expected output must be a string.")

    def _prepare_task_args(self, description, expected_output, agent, tools):
        task_args = {"description": description, "agent": agent or self.agent}
        if expected_output:
            task_args["expected_output"] = expected_output
        if tools:
            task_args["tools"] = tools
        return task_args

    def _handle_results(self, results):
        if isinstance(results, str):
            return [results]
        elif isinstance(results, list):
            return results
        else:
            return [str(results)]

    def _handle_single_result(self, result):
        if isinstance(result, list) and len(result) > 0:
            return result[0]
        elif isinstance(result, str):
            return result
        else:
            return str(result)
