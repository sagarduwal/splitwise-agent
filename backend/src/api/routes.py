from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import List, Optional
from src.agents.receipt_agent import ReceiptAgent
from src.agents.splitwise_agent import SplitwiseAgent
from typing import Dict, Optional
from pydantic import BaseModel

router = APIRouter()
receipt_agent = ReceiptAgent()
splitwise_agent = SplitwiseAgent()


@router.post("/receipts/process")
async def process_receipt(file: UploadFile = File(...)):
    """
    Process a receipt image and extract information
    """
    try:
        contents = await file.read()
        result = receipt_agent.process_receipt(contents)
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


class ExpenseCreateRequest(BaseModel):
    description: str
    amount: float
    group_id: Optional[int] = None
    split_equally: bool = True
    receipt_data: Optional[Dict] = None


@router.post("/expenses")
async def create_expense(request: ExpenseCreateRequest):
    """
    Create a new Splitwise expense
    """
    try:
        result = splitwise_agent.create_expense(
            description=request.description,
            amount=request.amount,
            group_id=request.group_id,
            split_equally=request.split_equally,
            receipt_data=request.receipt_data,
        )
        return {"status": "success", "data": result}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/groups")
async def get_groups():
    """
    Get all Splitwise groups
    """
    try:
        groups = splitwise_agent.get_groups()
        return {"status": "success", "data": groups}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/friends")
async def get_friends():
    """
    Get all Splitwise friends
    """
    try:
        friends = splitwise_agent.get_friends()
        return {"status": "success", "data": friends}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/expenses")
async def get_expenses(group_id: Optional[int] = None, limit: int = 20):
    """
    Get recent Splitwise expenses
    """
    try:
        expenses = splitwise_agent.get_expenses(group_id=group_id, limit=limit)
        return {"status": "success", "data": expenses}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
