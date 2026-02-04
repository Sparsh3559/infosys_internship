import resend
import os

# Resend API Key (set in Render ENV)
resend.api_key = os.getenv("RESEND_API_KEY")

# Sandbox sender (required by Resend)
FROM_EMAIL = "onboarding@resend.dev"


def send_magic_link(email: str, link: str, purpose: str):
    """
    Sends magic link email via Resend (HTTP-based, Render-safe)
    purpose: 'verify' | 'login'
    """

    if purpose == "verify":
        subject = "Verify your email to continue"
        button_text = "Verify Email"
        message = """
        <p>Your account has been created successfully.</p>
        <p>Please verify your email to continue.</p>
        <p>You will be redirected back to the application.</p>
        """
    elif purpose == "login":
        subject = "Login to your account"
        button_text = "Login Now"
        message = """
        <p>Click the button below to securely log in.</p>
        """
    else:
        raise ValueError("Invalid email purpose")

    html = f"""
    <div style="max-width:600px;margin:auto;font-family:Arial,sans-serif;">
        <h2>AI Content Studio</h2>
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
            This link expires in 10 minutes.
        </p>
    </div>
    """

    resend.Emails.send({
        "from": FROM_EMAIL,
        "to": email,
        "subject": subject,
        "html": html,
          
        "click_tracking": False,
        "open_tracking": False

    })