from src.ai.faq.notify import FAQContext, send_handoff_email
from src.config.settings import Settings


class DummySMTP:
    last_msg = None

    def __init__(self, host, port):
        self.host, self.port = host, port

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def send_message(self, msg):
        DummySMTP.last_msg = msg


def test_send_handoff_email_builds_and_sends(monkeypatch):
    # Patch smtplib.SMTP to our dummy
    import smtplib

    monkeypatch.setattr(smtplib, "SMTP", DummySMTP)

    settings = Settings(
        smtp_host="localhost",
        smtp_port=1025,
        smtp_from="bot@local.test",
        handoff_to="founder@local.test",
    )
    ok = send_handoff_email(
        settings,
        user_question="What is the SLA?",
        top_faq=FAQContext(id="faq-001", question="SLA?", answer="99.9%"),
        score=0.42,
        threshold=0.60,
    )
    assert ok is True
    assert DummySMTP.last_msg["To"] == "founder@local.test"
    assert "Handoff triggered" in DummySMTP.last_msg["Subject"]
    assert "User question:" in DummySMTP.last_msg.get_content()
