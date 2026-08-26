import os
import json
from contextlib import asynccontextmanager
from datetime import date
from fastmcp import FastMCP
from sqlalchemy import func, select
from pydantic import Field
from typing import Annotated
from database import AsyncSessionLocal, Base, engine
from expense_schema import ExpenseTracker

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")
ExpenseDate = Annotated[
    str,
    Field(
        pattern=r"^\d{4}-\d{2}-\d{2}$",
        description="Date in exact YYYY-MM-DD format, for example 2026-08-27.",
    ),
]

@asynccontextmanager
async def app_lifespan(server):
    await create_tables()
    yield

async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

mcp = FastMCP("ExpenseTracker", lifespan=app_lifespan)

@mcp.tool()
async def add_expense(
    date: ExpenseDate,
    amount: Annotated[
        float,
        Field(gt=0, description="Expense amount. Must be greater than zero.")
    ],
    category: Annotated[
        str,
        Field(min_length=1, description="Expense category.")
    ],
    subcategory: str = "",
    note: str = "",
):
    """Add a new expense entry.

    Args:
        date: Date when the expense occurred, in YYYY-MM-DD format.
        amount: Expense amount.
        category: Expense category.
        subcategory: Optional expense subcategory.
        note: Optional note about the expense.
    """
    async with AsyncSessionLocal() as db:
        expense_date = _parse_expense_date(date)
        expense = ExpenseTracker(
            expense_date=expense_date,
            amount=amount,
            category=category,
            subcategory=subcategory,
            note=note,
        )
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return {"status": "ok", "id": expense.id}
    
@mcp.tool()
async def list_expenses(start_date: ExpenseDate, end_date: ExpenseDate):
    '''List expense entries within an inclusive date range.

       Args: 
       Start Date: Date when the expense occurred, in YYYY-MM-DD format.
       End Date: Date when the expense occurred, in YYYY-MM-DD format.
    '''
    start_date, end_date = _parse_date_range(start_date, end_date)
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ExpenseTracker)
            .where(ExpenseTracker.expense_date.between(start_date, end_date))
            .order_by(ExpenseTracker.id.asc())
        )
        return [_expense_to_dict(expense) for expense in result.scalars()]

@mcp.tool()
async def summarize(
    start_date: ExpenseDate,
    end_date: ExpenseDate,
    category: str | None = None,
):
    '''Summarize expenses by category within an inclusive date range.

       Args:
       Start Date: Date when the expense occurred, in YYYY-MM-DD format.
       End Date: Date when the expense occurred, in YYYY-MM-DD format.
       category: category of the request which the user wants to see. 
                 If no category is defined then sumarize the entire expense
    '''
    start_date, end_date = _parse_date_range(start_date, end_date)
    async with AsyncSessionLocal() as db:
        query = select(
            ExpenseTracker.category,
            func.sum(ExpenseTracker.amount).label("total_amount"),
        ).where(ExpenseTracker.expense_date.between(start_date, end_date))

        if category:
            query = query.where(ExpenseTracker.category == category)

        result = await db.execute(
            query.group_by(ExpenseTracker.category).order_by(ExpenseTracker.category.asc())
        )

        return [
            {"category": expense_category, "total_amount": total_amount}
            for expense_category, total_amount in result.all()
        ]


def _parse_expense_date(value: str) -> date:
    try:
        return date.fromisoformat(value)
    except ValueError as error:
        raise ValueError("date must be a valid date in YYYY-MM-DD format") from error


def _parse_date_range(start_date: str, end_date: str) -> tuple[date, date]:
    parsed_start = _parse_expense_date(start_date)
    parsed_end = _parse_expense_date(end_date)
    if parsed_start > parsed_end:
        raise ValueError("start_date must be on or before end_date")
    return parsed_start, parsed_end


def _expense_to_dict(expense: ExpenseTracker):
    return {
        "id": expense.id,
        "date": expense.expense_date.isoformat(),
        "amount": expense.amount,
        "category": expense.category,
        "subcategory": expense.subcategory,
        "note": expense.note,
    }

@mcp.resource("expense://categories", mime_type="application/json")
def categories():
    # Read fresh each time so you can edit the file without restarting
    with open(CATEGORIES_PATH, "r", encoding="utf-8") as f:
        return f.read()

@mcp.resource("info://server")
def server_info() -> str:
    '''Get the Server info'''
    info = {
        'name' : 'Expense Tracker Server',
        'version' : '1.0.0',
        'description' : 'A simple MCP server to track my day to day expenses',
        'tools' : ['add_expense','list_expenses','summarize'],
        'author' : 'Avanindra' 
    }

    return json.dumps(info,indent=2)

if __name__ == "__main__":
    mcp.run(transport='http', host = "0.0.0.0" , port = 8000)


# Commands to interact with the remote server
# To start the server: uv run python mcp_expense_tracker_remote_server.py (fastmcp run does not execute the __main__ block)
# to validate with inspector : npx -y @modelcontextprotocol/inspector@2.1.0 --server-url http://127.0.0.1:8000/mcp --transport http (make sure to provide the exact port)
# If using fastmcp run, explicitly specify the transport and port: fastmcp run mcp_simple_remote_server.py --transport http --port 8000