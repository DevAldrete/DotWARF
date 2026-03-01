from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Lead(Base):
    __tablename__ = "leads"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(120))
    email: Mapped[str] = mapped_column(String(255), index=True)
    company: Mapped[str | None] = mapped_column(String(120), nullable=True)
    service_interest: Mapped[str] = mapped_column(String(120))
    budget_range: Mapped[str | None] = mapped_column(String(60), nullable=True)
    timeline: Mapped[str | None] = mapped_column(String(60), nullable=True)
    message: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
