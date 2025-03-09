from crewai import Agent
from .base_agent import BaseAgent
from ..config.splitwise_config import get_splitwise_client
from typing import Dict, List, Optional

class SplitwiseAgent(BaseAgent):
    """Agent responsible for interacting with the Splitwise API"""

    def __init__(self):
        super().__init__(
            name="Splitwise Manager",
            role="Manages interactions with Splitwise API"
        )
        self.splitwise = get_splitwise_client()

    def create_agent(self) -> Agent:
        return Agent(
            name=self.name,
            role=self.role,
            goal="Efficiently manage Splitwise expenses and group interactions",
            backstory="I handle all interactions with Splitwise, including creating "
                     "expenses, managing groups, and handling user data.",
            tools=[
                self.create_expense,
                self.get_groups,
                self.get_friends,
                self.get_expenses
            ]
        )

    def create_expense(self, 
                      description: str,
                      amount: float,
                      group_id: Optional[int] = None,
                      split_equally: bool = True,
                      users: Optional[List[Dict]] = None) -> dict:
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
                users=users or []
            )
            return {
                "id": expense.getId(),
                "description": expense.getDescription(),
                "amount": expense.getCost(),
                "date": expense.getDate()
            }
        except Exception as e:
            raise Exception(f"Failed to create expense: {str(e)}")

    def get_groups(self) -> List[dict]:
        """Get all Splitwise groups for the current user"""
        try:
            groups = self.splitwise.getGroups()
            return [{
                "id": group.getId(),
                "name": group.getName(),
                "members": [
                    {"id": member.getId(), "name": member.getFirstName()}
                    for member in group.getMembers()
                ]
            } for group in groups]
        except Exception as e:
            raise Exception(f"Failed to get groups: {str(e)}")

    def get_friends(self) -> List[dict]:
        """Get all Splitwise friends for the current user"""
        try:
            friends = self.splitwise.getFriends()
            return [{
                "id": friend.getId(),
                "first_name": friend.getFirstName(),
                "last_name": friend.getLastName(),
                "email": friend.getEmail()
            } for friend in friends]
        except Exception as e:
            raise Exception(f"Failed to get friends: {str(e)}")

    def get_expenses(self, 
                    group_id: Optional[int] = None, 
                    limit: int = 20) -> List[dict]:
        """
        Get recent expenses, optionally filtered by group
        
        Args:
            group_id: Optional group ID to filter expenses
            limit: Maximum number of expenses to return
            
        Returns:
            List[dict]: List of expense details
        """
        try:
            expenses = self.splitwise.getExpenses(
                group_id=group_id,
                limit=limit
            )
            return [{
                "id": expense.getId(),
                "description": expense.getDescription(),
                "amount": expense.getCost(),
                "date": expense.getDate(),
                "created_by": {
                    "id": expense.getCreatedBy().getId(),
                    "name": expense.getCreatedBy().getFirstName()
                }
            } for expense in expenses]
        except Exception as e:
            raise Exception(f"Failed to get expenses: {str(e)}")
