import smtplib
from email.mime.text import MIMEText
from app.config import settings

def send_verification_email(to_email: str, token: str):
    verify_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
    body = f"""Welcome to AutoInsight AI!

Click to verify your email:
{verify_url}

This link expires in 24 hours.
"""
    msg = MIMEText(body)
    msg["Subject"] = "Verify your AutoInsight AI account"
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email

    try:
        with smtplib.SMTP(settings.SMTP_HOST, settings.SMTP_PORT) as server:
            server.starttls()
            server.login(settings.SMTP_USER, settings.SMTP_PASS)
            server.send_message(msg)
    except Exception as e:
        print(f"[Email] Failed to send verification: {e}")
        # Don't block signup if email fails — log and continue