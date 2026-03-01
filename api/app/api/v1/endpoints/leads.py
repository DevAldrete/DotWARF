from fastapi import APIRouter, Depends, Header, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.lead import LeadRead
from app.services.lead_service import lead_service

settings = get_settings()
router = APIRouter()


def verify_admin_key(x_admin_key: str = Header(...)) -> None:
    """Simple static API-key guard for the admin leads endpoint."""
    if x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid admin key",
        )


@router.get(
    "/", response_model=list[LeadRead], dependencies=[Depends(verify_admin_key)]
)
async def list_leads(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(get_db),
) -> list[LeadRead]:
    """
    List all submitted leads (newest first).
    Requires `X-Admin-Key` header.
    """
    return await lead_service.list_leads(db, skip=skip, limit=limit)


@router.get(
    "/{lead_id}", response_model=LeadRead, dependencies=[Depends(verify_admin_key)]
)
async def get_lead(
    lead_id: int,
    db: AsyncSession = Depends(get_db),
) -> LeadRead:
    """
    Get a single lead by ID.
    Requires `X-Admin-Key` header.
    """
    lead = await lead_service.get_lead(db, lead_id)
    if not lead:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found"
        )
    return lead
