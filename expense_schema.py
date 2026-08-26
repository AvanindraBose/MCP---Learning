from sqlalchemy import Date, DateTime, Float, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column
from database import Base
from datetime import datetime, timezone
from zoneinfo import ZoneInfo

class ExpenseTracker(Base):
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    date: Mapped[datetime.date] = mapped_column(
        Date,
        nullable=False
    )

    amount: Mapped[float] = mapped_column(
        Float,
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