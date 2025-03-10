from crewai import Agent, Task, Crew, Process
from abc import ABC, abstractmethod
from typing import Optional, Dict, Any, List, Union
from dotenv import load_dotenv
import os
import json

# Load environment variables
load_dotenv()


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
            raise ValueError(f"Invalid configuration value: {str(e)}")

    @abstractmethod
    def create_agent(self) -> Agent:
        """Create and return a CrewAI agent"""
        pass

    def create_base_agent(self, **kwargs) -> Agent:
        """Create a base agent with common configuration"""
        # Remove parameters that are set in __init__ or config to avoid conflicts
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

        # Format tools as basic functions
        if "tools" in kwargs:
            tools = kwargs.pop("tools", [])
            tool_functions = []
            for tool in tools:
                if callable(tool):
                    tool_functions.append(
                        {
                            "name": tool.__name__,
                            "function": lambda *args, t=tool: t(*args),
                        }
                    )
            kwargs["tools"] = tool_functions

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
            raise Exception(f"Failed to create agent: {str(e)}. Config: {self.config}")

    def create_task(
        self,
        description: str,
        expected_output: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        agent: Optional[str] = None,
        tools: Optional[List[str]] = None,
    ) -> Task:
        """Create a new task for the agent

        Args:
            description: Task description
            expected_output: Expected format and structure of the output
            context: Optional context data
            agent: Optional agent to use for the task
            tools: Optional tools to use for the task

        Returns:
            Task: Configured task instance

        Raises:
            Exception: If task creation fails
        """
        try:
            # Ensure context is a list with a single item containing content
            task_context = []
            if context:
                try:
                    # Try to convert to JSON string first
                    content = json.dumps(context)
                except:
                    # If JSON conversion fails, use string representation
                    content = str(context)
                task_context = [{"content": content}]

            # Create task with required fields
            task_args = {
                "description": description,
                "agent": agent or self.agent,
                "context": task_context,
            }

            # Add expected_output if provided
            if expected_output:
                task_args["expected_output"] = expected_output

            # Add tools if provided
            if tools:
                task_args["tools"] = tools

            return Task(**task_args)
        except Exception as e:
            raise Exception(f"Failed to create task: {str(e)}")

    def execute_tasks(self, tasks: List[Task]) -> List[str]:
        """Execute a sequence of tasks and return their results"""
        if not tasks:
            return []

        try:
            # Create a crew with the agent and tasks
            crew = self.get_crew(tasks)

            # Execute all tasks through the crew
            results = crew.kickoff()

            # Handle single result vs multiple results
            if isinstance(results, str):
                return [results]
            elif isinstance(results, list):
                return results
            else:
                return [str(results)]

        except Exception as e:
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
        # Create a new crew with the agent and tasks
        crew = Crew(
            agents=[self.agent],
            tasks=tasks,
            verbose=self.config.get("verbose", False),
            process=Process.sequential,  # Use sequential process for predictable execution
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

            # Handle different result types
            if isinstance(result, list) and len(result) > 0:
                return result[0]
            elif isinstance(result, str):
                return result
            else:
                return str(result)
        except Exception as e:
            raise Exception(f"Task execution failed: {str(e)}")
