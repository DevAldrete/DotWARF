from datetime import datetime
from typing import Literal

from pydantic import BaseModel, EmailStr, field_validator


ServiceInterest = Literal[
    "chatbot",
    "agent",
    "workflow_automation",
    "model_finetuning",
    "website",
    "api_development",
    "freelance_hourly",
    "other",
]

BudgetRange = Literal[
    "under_1k",
    "1k_5k",
    "5k_15k",
    "15k_plus",
    "not_sure",
]

Timeline = Literal[
    "asap",
    "1_month",
    "3_months",
    "flexible",
]


class ContactFormCreate(BaseModel):
    name: str
    email: EmailStr
    company: str | None = None
    service_interest: ServiceInterest
    budget_range: BudgetRange | None = None
    timeline: Timeline | None = None
    message: str

    @field_validator("name")
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Name cannot be empty")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_not_empty(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Message cannot be empty")
        return v.strip()


class LeadRead(BaseModel):
    model_config = {"from_attributes": True}

    id: int
    name: str
    email: str
    company: str | None
    service_interest: str
    budget_range: str | None
    timeline: str | None
    message: str
    created_at: datetime
