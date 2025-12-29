import smtplib
from email.message import EmailMessage

SMTP_EMAIL = "your_email@gmail.com"
SMTP_PASSWORD = "your_app_password"

def send_magic_link(email: str, link: str):
    msg = EmailMessage()
    msg["Subject"] = "Your Login Link"
    msg["From"] = SMTP_EMAIL
    msg["To"] = email
    msg.set_content(f"Click to login:\n{link}")

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.send_message(msg)