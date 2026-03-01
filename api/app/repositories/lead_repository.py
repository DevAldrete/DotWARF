from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.lead import Lead
from app.schemas.lead import ContactFormCreate


class LeadRepository:
    async def create(self, db: AsyncSession, data: ContactFormCreate) -> Lead:
        lead = Lead(**data.model_dump())
        db.add(lead)
        await db.flush()
        await db.refresh(lead)
        return lead

    async def get_all(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[Lead]:
        result = await db.execute(
            select(Lead).order_by(Lead.created_at.desc()).offset(skip).limit(limit)
        )
        return list(result.scalars().all())

    async def get_by_id(self, db: AsyncSession, lead_id: int) -> Lead | None:
        result = await db.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalars().first()


lead_repository = LeadRepository()
