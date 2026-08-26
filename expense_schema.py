from sqlalchemy import Date, DateTime, Integer, Text, Numeric
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import date, datetime, timezone
from zoneinfo import ZoneInfo
from decimal import Decimal

class ExpenseTracker(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    expense_date: Mapped[date] = mapped_column(
        Date,
        nullable=False
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(12,2),
        nullable=False
    )

    category: Mapped[str] = mapped_column(
        Text,
        nullable=False
    )

    subcategory: Mapped[str | None] = mapped_column(
        Text,
        default=""
    )

    note: Mapped[str | None] = mapped_column(
        Text,
        default=""
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc).astimezone(ZoneInfo("Asia/Kolkata")),
        nullable=False
    )