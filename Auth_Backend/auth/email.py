import os
import resend

resend.api_key = os.getenv("RESEND_API_KEY")

FROM_EMAIL = os.getenv("FROM_EMAIL")


def send_magic_link(email: str, link: str, purpose: str):
    """
    Sends a magic link email using Resend (HTTPS-based, Render-safe)
    """

    subject = (
        "Verify your email"
        if purpose == "verify"
        else "Your login magic link"
    )

    html = f"""
        <p>Hello,</p>
        <p>Click the link below to continue:</p>
        <p><a href="{link}">{link}</a></p>
        <p>This link expires in 10 minutes.</p>
    """

    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": email,
        "subject": subject,
        "html": html
    })