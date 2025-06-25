import resend
from typing import List


resend.api_key = "re_QDXfGZ4Q_BcTWvKF6k19tXRHGeBu5na7X"

with open("content_fixed.html", "r", encoding="utf-8") as file:
    html_content = file.read()


params: List[resend.Emails.SendParams] = [
  {
    "from": "AI Loom <launch@updates.voxhunter.dev>",
  "to": ["vidyutsanthosh4@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
]

resend.Batch.send(params)

