import resend
from typing import List


resend.api_key = "re_QDXfGZ4Q_BcTWvKF6k19tXRHGeBu5na7X"

with open("content.html", "r", encoding="utf-8") as file:
    html_content = file.read()


params: List[resend.Emails.SendParams] = [
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["vidyutsanthosh4@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["tonyokemba2008@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["muhammadabdulsatar20@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["ruqayyah.khan10@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["hr568.sch@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
  {
    "from": "AI Loom <onboarding@updates.voxhunter.dev>",
  "to": ["iamapenguin64@gmail.com"],
  "subject": "You're In!",
  "html": html_content,
  },
]

resend.Batch.send(params)

