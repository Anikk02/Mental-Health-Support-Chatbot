"""
Improved mailer helper.
Uses SMTP if credentials are configured.
Falls back to console output in development.
"""

import smtplib
from email.message import EmailMessage
from .config import (
    SMTP_HOST,
    SMTP_PORT,
    SMTP_USER,
    SMTP_PASS,
    FROM_EMAIL
)

def send_email(to: str, subject: str, body: str):
    print("SMTP_HOST:", SMTP_HOST)
    print("SMTP_USER:", SMTP_USER)
    print("SMTP_PASS SET:", bool(SMTP_PASS))
    """
    Sends an email using SMTP.
    Falls back to printing to console if SMTP is not configured.
    """

    # If SMTP is not configured → fallback for development
    if not SMTP_HOST or not SMTP_USER or not SMTP_PASS:
        print("\n[mailer DEV MODE]")
        print(f"To: {to}")
        print(f"Subject: {subject}")
        print("Body:")
        print(body)
        print("[end email]\n")
        return

    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_HOST, SMTP_PORT, timeout=10) as smtp:
            smtp.starttls()
            smtp.login(SMTP_USER, SMTP_PASS)
            smtp.send_message(msg)

        print(f"[mailer] Email successfully sent → {to}")

    except Exception as e:
        print(f"[mailer ERROR] Failed to send email → {to}. Error: {e}")
