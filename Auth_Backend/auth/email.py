import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --------------------------------------------------
# ENV VARIABLES (SET ON RENDER)
# --------------------------------------------------
SMTP_EMAIL = os.getenv("SMTP_EMAIL")       # your gmail address
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")  # gmail app password
SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", 587))

if not SMTP_EMAIL or not SMTP_PASSWORD:
    raise RuntimeError("SMTP_EMAIL or SMTP_PASSWORD not set")


def send_magic_link(email: str, link: str, purpose: str):
    """
    Sends verification or login email via Gmail SMTP
    purpose: 'verify' | 'login'
    """

    if purpose == "verify":
        subject = "Verify your email – AI Content Studio"
        button_text = "Verify Email"
        message = """
        <p>Your account has been created successfully.</p>
        <p>Please verify your email to continue.</p>
        <p>After verification, you will be redirected to login.</p>
        """

    elif purpose == "login":
        subject = "Login to AI Content Studio"
        button_text = "Login Now"
        message = """
        <p>You requested to log in.</p>
        <p>Click the button below to access your account.</p>
        """

    else:
        raise ValueError("Invalid email purpose")

    html = f"""
    <div style="max-width:600px;margin:auto;font-family:Arial,sans-serif;">
        <h2 style="color:#111;">AI Content Studio</h2>
        {message}
        <a href="{link}"
           style="
             display:inline-block;
             margin-top:16px;
             padding:12px 20px;
             background:#2563eb;
             color:white;
             text-decoration:none;
             border-radius:6px;
             font-weight:600;
           ">
           {button_text}
        </a>
        <p style="margin-top:24px;color:#555;font-size:12px;">
            This link will expire in 10 minutes.
        </p>
    </div>
    """

    msg = MIMEMultipart("alternative")
    msg["From"] = SMTP_EMAIL
    msg["To"] = email
    msg["Subject"] = subject
    msg.attach(MIMEText(html, "html"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_EMAIL, SMTP_PASSWORD)
        server.sendmail(SMTP_EMAIL, email, msg.as_string())