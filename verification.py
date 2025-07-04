import resend

resend.api_key = "re_QDXfGZ4Q_BcTWvKF6k19tXRHGeBu5na7X"

with open("verification.html", "r", encoding="utf-8") as file:
    html_template = file.read()


def verify_email(email: str, code: int):
    # Replace the {code} placeholder in the HTML template with the actual verification code
    html_content = html_template.replace("{code}", str(code))
    
    params: resend.Emails.SendParams = {
    "from": "AI Loom <verification@ailoom.me>",
    "to": [email],
    "subject": f"AI Loom Verification Code: {code}",
    "html": html_content
    }

    email_send = resend.Emails.send(params)
    return email_send