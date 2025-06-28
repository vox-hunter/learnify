import resend
from typing import List


resend.api_key = "re_QDXfGZ4Q_BcTWvKF6k19tXRHGeBu5na7X"

with open("content_fixed.html", "r", encoding="utf-8") as file:
    html_content = file.read()

# Replace the unsubscribe URL placeholder with a proper HTML link
html_content = html_content.replace(
    "{{{RESEND_UNSUBSCRIBE_URL}}}", 
    '<a href="{{{RESEND_UNSUBSCRIBE_URL}}}" style="color: #4f46e5;">here</a>'
)

params: resend.Broadcasts.SendParams = {
  "broadcast_id": "73ef9c34-e4a1-44b4-bb36-8d08f37b6bb7",
}

resend.Broadcasts.send(params)