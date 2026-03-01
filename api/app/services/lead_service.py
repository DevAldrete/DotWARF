import logging

import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import get_settings
from app.models.lead import Lead
from app.repositories.lead_repository import lead_repository
from app.schemas.lead import ContactFormCreate, LeadRead

logger = logging.getLogger(__name__)
settings = get_settings()


SERVICE_LABELS: dict[str, str] = {
    "chatbot": "Chatbot Development",
    "agent": "AI Agent",
    "workflow_automation": "Workflow / Automation",
    "model_finetuning": "Model Fine-tuning / Training",
    "website": "Website Creation",
    "api_development": "API Development",
    "freelance_hourly": "Freelance / Hourly Project",
    "other": "Other",
}

BUDGET_LABELS: dict[str, str] = {
    "under_1k": "Under $1,000",
    "1k_5k": "$1,000 – $5,000",
    "5k_15k": "$5,000 – $15,000",
    "15k_plus": "$15,000+",
    "not_sure": "Not sure yet",
}

TIMELINE_LABELS: dict[str, str] = {
    "asap": "As soon as possible",
    "1_month": "Within 1 month",
    "3_months": "Within 3 months",
    "flexible": "Flexible",
}


class LeadService:
    async def submit_contact(
        self, db: AsyncSession, data: ContactFormCreate
    ) -> LeadRead:
        """Save lead to DB and send notification email."""
        lead = await lead_repository.create(db, data)

        # Fire-and-forget email; don't fail the request if SMTP is misconfigured
        try:
            await self._send_notification_email(lead)
        except Exception as exc:
            logger.warning("Could not send notification email: %s", exc)

        return LeadRead.model_validate(lead)

    async def list_leads(
        self, db: AsyncSession, skip: int = 0, limit: int = 100
    ) -> list[LeadRead]:
        leads = await lead_repository.get_all(db, skip=skip, limit=limit)
        return [LeadRead.model_validate(l) for l in leads]

    async def get_lead(self, db: AsyncSession, lead_id: int) -> LeadRead | None:
        lead = await lead_repository.get_by_id(db, lead_id)
        return LeadRead.model_validate(lead) if lead else None

    # ------------------------------------------------------------------ helpers

    async def _send_notification_email(self, lead: Lead) -> None:
        if not settings.SMTP_USERNAME or not settings.CONTACT_RECIPIENT_EMAIL:
            logger.info("SMTP not configured – skipping notification email")
            return

        service_label = SERVICE_LABELS.get(lead.service_interest, lead.service_interest)
        budget_label = BUDGET_LABELS.get(
            lead.budget_range or "", lead.budget_range or "—"
        )
        timeline_label = TIMELINE_LABELS.get(lead.timeline or "", lead.timeline or "—")

        body_text = f"""New lead from the Dotwarf website!

Name:             {lead.name}
Email:            {lead.email}
Company:          {lead.company or "—"}
Service interest: {service_label}
Budget range:     {budget_label}
Timeline:         {timeline_label}

Message:
{lead.message}
"""

        body_html = f"""
<html><body style="font-family:sans-serif;color:#1a1a1a">
  <h2 style="color:#6c47ff">New lead – Dotwarf</h2>
  <table cellpadding="6" cellspacing="0" style="border-collapse:collapse">
    <tr><td><strong>Name</strong></td><td>{lead.name}</td></tr>
    <tr><td><strong>Email</strong></td><td><a href="mailto:{lead.email}">{lead.email}</a></td></tr>
    <tr><td><strong>Company</strong></td><td>{lead.company or "—"}</td></tr>
    <tr><td><strong>Service</strong></td><td>{service_label}</td></tr>
    <tr><td><strong>Budget</strong></td><td>{budget_label}</td></tr>
    <tr><td><strong>Timeline</strong></td><td>{timeline_label}</td></tr>
  </table>
  <h3>Message</h3>
  <p style="white-space:pre-wrap">{lead.message}</p>
</body></html>
"""

        msg = MIMEMultipart("alternative")
        msg["Subject"] = f"[Dotwarf] New lead: {lead.name} ({service_label})"
        msg["From"] = settings.SMTP_FROM_EMAIL or settings.SMTP_USERNAME
        msg["To"] = settings.CONTACT_RECIPIENT_EMAIL

        msg.attach(MIMEText(body_text, "plain"))
        msg.attach(MIMEText(body_html, "html"))

        await aiosmtplib.send(
            msg,
            hostname=settings.SMTP_HOST,
            port=settings.SMTP_PORT,
            username=settings.SMTP_USERNAME,
            password=settings.SMTP_PASSWORD,
            start_tls=True,
        )
        logger.info("Notification email sent for lead id=%s", lead.id)


lead_service = LeadService()
