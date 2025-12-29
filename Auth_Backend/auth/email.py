import resend
import os

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = "onboarding@resend.dev"

def send_magic_link(email: str, link: str, purpose: str):
    """
    Sends a magic link email using Resend.
    purpose: 'verify' | 'login'
    """

    if purpose == "verify":
        subject = "Verify your email"
        html = f"""
        <p>Welcome 👋</p>
        <p>Please verify your email by clicking the link below:</p>
        <p><a href="{link}">Verify Email</a></p>
        """
    elif purpose == "login":
        subject = "Your magic login link"
        html = f"""
        <p>Click the link below to log in:</p>
        <p><a href="{link}">Log in</a></p>
        """
    else:
        raise ValueError("Invalid email purpose")

    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": email,
        "subject": subject,
        "html": html
    })