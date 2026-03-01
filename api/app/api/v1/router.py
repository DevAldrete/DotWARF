from fastapi import APIRouter

from app.api.v1.endpoints import chat, contact, leads

api_router = APIRouter()

api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(contact.router, prefix="/contact", tags=["contact"])
api_router.include_router(leads.router, prefix="/leads", tags=["leads"])
