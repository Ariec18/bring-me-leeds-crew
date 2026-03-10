import os
import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Type

import requests
from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EmailSenderInput(BaseModel):
    to_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    body_html: str = Field(description="HTML or plain text body of the email")
    dry_run: bool = Field(
        default=False,
        description="If True, logs the email but does NOT send it.",
    )


class EmailSenderTool(BaseTool):
    name: str = "Email Sender"
    description: str = (
        "Sends a personalized email via Resend API. "
        "Input: to_email, subject, body_html, dry_run (optional, default False). "
        "If dry_run=True — logs without sending. "
        "Returns send status and appends to output/outreach_log.csv."
    )
    args_schema: Type[BaseModel] = EmailSenderInput

    def _run(
        self,
        to_email: str,
        subject: str,
        body_html: str,
        dry_run: bool = False,
    ) -> str:
        log_path = Path("output/outreach_log.csv")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        timestamp = datetime.now().isoformat()
        status = "DRY_RUN"

        if not dry_run:
            api_key = os.getenv("RESEND_API_KEY")
            from_email = os.getenv("FROM_EMAIL", "onboarding@resend.dev")

            if not api_key:
                return "ERROR: RESEND_API_KEY not set in environment."

            # Plain text → wrap in minimal HTML if needed
            if not body_html.strip().startswith("<"):
                body_html = body_html.replace("\n", "<br>")

            response = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": from_email,
                    "to": [to_email],
                    "subject": subject,
                    "html": body_html,
                },
                timeout=15,
            )

            if response.status_code in (200, 201):
                status = "SUCCESS"
            else:
                status = f"FAILED: {response.status_code} — {response.text}"

        # Append to CSV log
        file_exists = log_path.exists()
        with open(log_path, "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            if not file_exists:
                writer.writerow(["timestamp", "to_email", "subject", "status", "mode"])
            writer.writerow([
                timestamp,
                to_email,
                subject,
                status,
                "dry_run" if dry_run else "live",
            ])

        return f"{status}: to={to_email} | log={log_path}"
