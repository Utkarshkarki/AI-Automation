"""
services/email/smtp.py — Private: Gmail SMTP implementation.
Only used internally by EmailService. Not imported by any other domain.
"""
import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from core.config import GMAIL_ADDRESS, GMAIL_APP_PASSWORD
from core.exceptions import CredentialsNotConfiguredError, EmailDeliveryError

logger = logging.getLogger(__name__)


def smtp_send(to: str, subject: str, body: str, cc: str = None) -> None:
    """
    Send an email via Gmail SMTP with TLS.
    Raises CredentialsNotConfiguredError or EmailDeliveryError on failure.
    """
    if not GMAIL_ADDRESS or not GMAIL_APP_PASSWORD:
        raise CredentialsNotConfiguredError(
            "Gmail credentials not configured. "
            "Set GMAIL_ADDRESS and GMAIL_APP_PASSWORD in backend/.env"
        )

    if GMAIL_APP_PASSWORD == "your_app_password_here":
        raise CredentialsNotConfiguredError(
            "Gmail App Password is still the placeholder value. "
            "Generate a real App Password at myaccount.google.com/security"
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
        logger.info(f"[email.smtp] Sent to={to} subject={subject}")
    except smtplib.SMTPAuthenticationError:
        raise EmailDeliveryError(
            "Gmail authentication failed. "
            "Check that your App Password is correct and 2-Step Verification is enabled."
        )
    except smtplib.SMTPException as e:
        raise EmailDeliveryError(f"SMTP error: {e}")
