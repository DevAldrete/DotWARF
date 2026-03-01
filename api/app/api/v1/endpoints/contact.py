from fastapi import APIRouter, Depends, Request, status
from slowapi import Limiter
from slowapi.util import get_remote_address
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.core.database import get_db
from app.schemas.lead import ContactFormCreate, LeadRead
from app.services.lead_service import lead_service

settings = get_settings()
limiter = Limiter(key_func=get_remote_address)
router = APIRouter()


@router.post("/", response_model=LeadRead, status_code=status.HTTP_201_CREATED)
@limiter.limit(settings.CONTACT_RATE_LIMIT)
async def submit_contact(
    request: Request,
    body: ContactFormCreate,
    db: AsyncSession = Depends(get_db),
) -> LeadRead:
    """
    Contact form submission.
    Stores the lead in the database and sends a notification email.
    Rate-limited per IP to prevent spam.
    """
    return await lead_service.submit_contact(db, body)
