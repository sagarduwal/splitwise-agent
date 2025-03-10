from crewai import Agent, Task
from .base_agent import BaseAgent
from ..config.splitwise_config import get_splitwise_client
from typing import Dict, List, Optional, Any, Union, Callable
from datetime import datetime
import json


class SplitwiseAgent(BaseAgent):
    """Agent responsible for interacting with the Splitwise API"""

    def __init__(self):
        super().__init__(
            name="Splitwise Manager",
            role="Financial Transaction Manager",
            goal="Efficiently manage and organize Splitwise expenses with intelligent categorization and fair splitting",
        )
        self.splitwise = get_splitwise_client()

    def create_agent(self) -> Agent:
        def expense(data):
            return self.create_expense(**data)

        def expenses(data):
            return self.get_expenses(**data)

        def analyze(data):
            return self._analyze_expense_data(data)

        def split(data):
            return self._suggest_split_strategy(data)

        return self.create_base_agent(
            backstory=(
                "I am an expert financial manager specializing in group expenses and cost sharing. "
                "I understand various expense types, can suggest fair splitting strategies, "
                "and help maintain transparent financial records among groups. I excel at "
                "categorizing expenses and determining optimal sharing arrangements."
            ),
            tools=[expense, expenses, analyze, split],
        )

    def create_expense(
        self,
        description: str,
        amount: float,
        group_id: Optional[int] = None,
        split_equally: bool = True,
        users: Optional[List[Dict]] = None,
        analyze: bool = True,
    ) -> dict:
        """
        Create a new expense in Splitwise

        Args:
            description: Description of the expense
            amount: Total amount of the expense
            group_id: Optional group ID to create expense in
            split_equally: Whether to split the expense equally
            users: Optional list of user splits if not equal

        Returns:
            dict: Created expense details
        """
        try:
            expense = self.splitwise.createExpense(
                description=description,
                amount=amount,
                group_id=group_id,
                split_equally=split_equally,
                users=users or [],
            )
            expense_data = {
                "id": expense.getId(),
                "description": expense.getDescription(),
                "amount": expense.getCost(),
                "date": expense.getDate(),
            }

            if analyze:
                # Analyze the expense for better categorization and splitting
                analysis = self._analyze_expense_data(expense_data)
                expense_data.update(analysis)

            return expense_data
        except Exception as e:
            raise Exception(f"Failed to create expense: {str(e)}")

    def get_groups(self) -> List[dict]:
        """Get all Splitwise groups for the current user"""
        try:
            groups = self.splitwise.getGroups()
            return [
                {
                    "id": group.getId(),
                    "name": group.getName(),
                    "members": [
                        {"id": member.getId(), "name": member.getFirstName()}
                        for member in group.getMembers()
                    ],
                }
                for group in groups
            ]
        except Exception as e:
            raise Exception(f"Failed to get groups: {str(e)}")

    def get_friends(self) -> List[dict]:
        """Get all Splitwise friends for the current user"""
        try:
            friends = self.splitwise.getFriends()
            return [
                {
                    "id": friend.getId(),
                    "first_name": friend.getFirstName(),
                    "last_name": friend.getLastName(),
                    "email": friend.getEmail(),
                }
                for friend in friends
            ]
        except Exception as e:
            raise Exception(f"Failed to get friends: {str(e)}")

    def get_expenses(
        self, group_id: Optional[int] = None, limit: int = 20, analyze: bool = False
    ) -> List[dict]:
        """
        Get recent expenses, optionally filtered by group

        Args:
            group_id: Optional group ID to filter expenses
            limit: Maximum number of expenses to return
            analyze: Whether to perform intelligent analysis on expenses

        Returns:
            List[dict]: List of expense details with optional analysis
        """
        try:
            expenses = self.splitwise.getExpenses(group_id=group_id, limit=limit)
            expense_list = [
                {
                    "id": expense.getId(),
                    "description": expense.getDescription(),
                    "amount": expense.getCost(),
                    "date": expense.getDate(),
                    "created_by": {
                        "id": expense.getCreatedBy().getId(),
                        "name": expense.getCreatedBy().getFirstName(),
                    },
                }
                for expense in expenses
            ]

            if analyze:
                # Process expenses in batch for efficiency
                return self.process_expense_batch(expense_list)
            return expense_list

        except Exception as e:
            raise Exception(f"Failed to get expenses: {str(e)}")

    def create_task(
        self,
        description: str,
        expected_output: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None,
        agent: Optional[Agent] = None,
        tools: Optional[List[Any]] = None,
        expense_data: Optional[Dict[str, Any]] = None,
        group_data: Optional[Dict[str, Any]] = None,
        splitwise_functions: Optional[List[Callable]] = None,
    ) -> Task:
        """
        Create a new task for the Splitwise agent with financial data context
        
        Args:
            description: Task description
            expected_output: Expected format and structure of the output
            context: Optional context data
            agent: Optional agent to use for the task
            tools: Optional tools to use for the task
            expense_data: Optional expense data to include in context
            group_data: Optional group data to include in context
            splitwise_functions: Optional Splitwise API functions to include as tools
            
        Returns:
            Task: Configured task instance
            
        Raises:
            Exception: If task creation fails
        """
        try:
            # Prepare context with financial data if provided
            task_context = context or {}
            
            if expense_data:
                task_context["expense_data"] = expense_data
                
            if group_data:
                task_context["group_data"] = group_data
                
            # Add Splitwise API functions as tools if provided
            task_tools = tools or []
            
            if splitwise_functions:
                for func in splitwise_functions:
                    if callable(func):
                        task_tools.append(func)
            
            # Call the parent class's create_task method with our modifications
            return super().create_task(
                description=description,
                expected_output=expected_output,
                context=task_context,
                agent=agent,
                tools=task_tools
            )
        except Exception as e:
            raise Exception(f"Failed to create Splitwise task: {str(e)}")
            
    def _analyze_expense_data(self, expense_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze expense data to provide intelligent categorization and insights"""
        analysis_task = self.create_task(
            description=(
                "Analyze this expense and provide the following insights:\n"
                "1. Expense category (e.g., food, transport, utilities)\n"
                "2. Suggested tags for better organization\n"
                "3. Any patterns or recurring expense indicators\n"
                "4. Budget category suggestion\n\n"
                f"Expense data: {json.dumps(expense_data, indent=2)}"
            ),
            expense_data=expense_data,
        )

        try:
            result = self.execute_single_task(analysis_task)
            return json.loads(result)
        except Exception as e:
            return {"analysis_error": str(e), "category": "uncategorized", "tags": []}

    def _suggest_split_strategy(
        self, expense_data: Dict[str, Any], group_info: Optional[Dict] = None
    ) -> Dict[str, Any]:
        """Suggest an optimal splitting strategy based on expense and group data"""
        split_task = self.create_task(
            description=(
                "Analyze this expense and group information to suggest the optimal splitting strategy:\n"
                "1. Determine if equal split is appropriate\n"
                "2. Suggest alternative splitting methods if relevant\n"
                "3. Provide reasoning for the suggestion\n"
                "4. Consider any special circumstances\n\n"
            ),
            expense_data=expense_data,
            group_data=group_info or {},
        )

        try:
            result = self.execute_single_task(split_task)
            return json.loads(result)
        except Exception as e:
            return {
                "strategy": "equal",
                "reasoning": f"Default to equal split due to error: {str(e)}",
            }

    def process_expense_batch(
        self, expenses: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Process a batch of expenses with intelligent analysis"""
        tasks = [
            self.create_task(
                description=(
                    "Process this expense with detailed analysis:\n"
                    "1. Categorize the expense\n"
                    "2. Suggest optimal splitting\n"
                    "3. Identify any patterns or special handling needed\n"
                ),
                expense_data=expense,
            )
            for expense in expenses
        ]

        return self.execute_tasks(tasks)
