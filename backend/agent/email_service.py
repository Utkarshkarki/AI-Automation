import json
import logging
import os
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

logger = logging.getLogger(__name__)

GMAIL_ADDRESS = os.getenv("GMAIL_ADDRESS", "")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD", "")

# Local JSON file to log all sent emails
SENT_LOG_PATH = Path(__file__).parent.parent / "sent_emails.json"


def _load_log() -> list:
    """Load the sent emails log from disk."""
    if SENT_LOG_PATH.exists():
        try:
            with open(SENT_LOG_PATH, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return []
    return []


def _save_log(log: list) -> None:
    """Persist the sent emails log to disk."""
    with open(SENT_LOG_PATH, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2, default=str)


def send_real_email(to: str, subject: str, body: str, cc: str = None) -> dict:
    """
    Send a real email via Gmail SMTP with TLS.
    Requires GMAIL_ADDRESS and GMAIL_APP_PASSWORD env vars to be set.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise RuntimeError(
            "Gmail credentials not configured. "
            "Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in backend/.env"
        )

    if GMAIL_APP_PASSWORD == "your_app_password_here":
        raise RuntimeError(
            "Gmail App Password is still set to the placeholder value. "
            "Please generate a real App Password from myaccount.google.com/security"
        )

    msg = MIMEMultipart()
    msg["From"] = GMAIL_ADDRESS
    msg["To"] = to
    msg["Subject"] = subject
    if cc:
        msg["Cc"] = cc

    msg.attach(MIMEText(body, "plain"))

    recipients = [to] + ([cc] if cc else [])

    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.ehlo()
            server.starttls()
            server.login(GMAIL_ADDRESS, GMAIL_APP_PASSWORD)
            server.sendmail(GMAIL_ADDRESS, recipients, msg.as_string())

        logger.info(f"[email_service] Email sent successfully to={to} subject={subject}")

        # Log the sent email
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "from": GMAIL_ADDRESS,
            "to": to,
            "cc": cc,
            "subject": subject,
            "body_preview": body[:200],
            "status": "sent",
        }
        log = _load_log()
        log.append(entry)
        _save_log(log)

        return {
            "status": "sent",
            "to": to,
            "subject": subject,
            "from": GMAIL_ADDRESS,
        }

    except smtplib.SMTPAuthenticationError:
        raise RuntimeError(
            "Gmail authentication failed. "
            "Make sure your App Password is correct and 2-Step Verification is enabled."
        )
    except smtplib.SMTPException as e:
        raise RuntimeError(f"SMTP error while sending email: {e}")


def get_sent_emails(limit: int = 10) -> list:
    """Return the most recent sent emails from the local log."""
    log = _load_log()
    return log[-limit:]
