from __future__ import annotations

import smtplib
from email.message import EmailMessage
from dataclasses import dataclass

from src.config.settings import Settings


@dataclass
class FAQContext:
    id: str
    question: str
    answer: str


def _build_message(settings: Settings, to_addr: str, subject: str, body: str) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = settings.smtp_from or "bot@local.test"
    msg["To"] = to_addr
    msg["Subject"] = subject
    msg.set_content(body)
    return msg


def send_handoff_email(
    settings: Settings,
    user_question: str,
    top_faq: FAQContext,
    score: float,
    threshold: float,
) -> bool:
    """
    Send a handoff email. Returns True if we attempted to send; False if not configured.
    Designed to be easily monkeypatched in tests (no network).
    """
    if not (settings.smtp_host and settings.smtp_port and settings.handoff_to):
        # Not configured -> no-op
        return False

    subject = f"[FAQ Bot] Handoff triggered (score={score:.2f} < thr={threshold:.2f})"
    body = (
        "A low-confidence FAQ query needs human attention.\n\n"
        f"User question:\n{user_question}\n\n"
        "Top retrieved context:\n"
        f"- id: {top_faq.id}\n"
        f"- question: {top_faq.question}\n"
        f"- answer: {top_faq.answer}\n\n"
        f"Score: {score:.3f}\n"
        f"Threshold: {threshold:.3f}\n"
    )

    msg = _build_message(settings, settings.handoff_to, subject, body)

    with smtplib.SMTP(settings.smtp_host, int(settings.smtp_port)) as smtp:
        # MailHog requires no TLS/auth
        smtp.send_message(msg)

    return True
