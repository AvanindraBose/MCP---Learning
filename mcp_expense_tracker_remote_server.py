import os
import asyncio
from datetime import date
from fastmcp import FastMCP
from sqlalchemy import func, select

from database import AsyncSessionLocal, Base, engine
from expense_schema import ExpenseTracker

CATEGORIES_PATH = os.path.join(os.path.dirname(__file__), "categories.json")

mcp = FastMCP("ExpenseTracker")

# ******************************** Server ***********************************
async def create_tables():
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.create_all)

asyncio.run(create_tables())

@mcp.tool()
async def add_expense(date: date, amount: float, category: str, subcategory: str = "", note: str = ""):
    """Add a new expense entry.

    Args:
        date: Date when the expense occurred, in YYYY-MM-DD format.
        amount: Expense amount.
        category: Expense category.
        subcategory: Optional expense subcategory.
        note: Optional note about the expense.
    """
    async with AsyncSessionLocal() as db:
        expense = ExpenseTracker(
            date=date,
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
async def list_expenses(start_date: date, end_date: date):
    '''List expense entries within an inclusive date range.'''
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(ExpenseTracker)
            .where(ExpenseTracker.date.between(start_date, end_date))
            .order_by(ExpenseTracker.id.asc())
        )
        return [_expense_to_dict(expense) for expense in result.scalars()]

@mcp.tool()
async def summarize(start_date: date, end_date: date, category: str | None = None):
    '''Summarize expenses by category within an inclusive date range.'''
    async with AsyncSessionLocal() as db:
        query = select(
            ExpenseTracker.category,
            func.sum(ExpenseTracker.amount).label("total_amount"),
        ).where(ExpenseTracker.date.between(start_date, end_date))

        if category:
            query = query.where(ExpenseTracker.category == category)

        result = await db.execute(
            query.group_by(ExpenseTracker.category).order_by(ExpenseTracker.category.asc())
        )

        return [
            {"category": expense_category, "total_amount": total_amount}
            for expense_category, total_amount in result.all()
        ]

def _expense_to_dict(expense: ExpenseTracker):
    return {
        "id": expense.id,
        "date": expense.date.isoformat(),
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

if __name__ == "__main__":
    mcp.run(transport='http', host = "0.0.0.0" , port = 8000)


# Commands to interact with the remote server
# To start the server: uv run python mcp_simple_remote_server.py (fastmcp run does not execute the __main__ block)
# to validate with inspector : npx -y @modelcontextprotocol/inspector@2.1.0 --server-url http://127.0.0.1:8000/mcp --transport http (make sure to provide the exact port)
# If using fastmcp run, explicitly specify the transport and port: fastmcp run mcp_simple_remote_server.py --transport http --port 8000