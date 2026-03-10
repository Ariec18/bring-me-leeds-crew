import os
import smtplib
import csv
from datetime import datetime
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class EmailSenderInput(BaseModel):
    to_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    body_html: str = Field(description="HTML body of the email")
    dry_run: bool = Field(
        default=False,
        description="If True, logs the email but does NOT send it. Safe for testing.",
    )


class EmailSenderTool(BaseTool):
    name: str = "Email Sender"
    description: str = (
        "Sends a personalized HTML email to a prospect via SMTP. "
        "Input: to_email, subject, body_html, dry_run (optional, default False). "
        "If dry_run=True — logs the email without sending. "
        "Returns send status (SUCCESS/DRY_RUN/FAILED) and appends to output/outreach_log.csv."
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
            smtp_host = os.getenv("SMTP_HOST", "smtp.gmail.com")
            smtp_port = int(os.getenv("SMTP_PORT", "587"))
            smtp_user = os.getenv("SMTP_USER")
            smtp_pass = os.getenv("SMTP_PASS")
            from_email = os.getenv("FROM_EMAIL", smtp_user)

            if not smtp_user or not smtp_pass:
                return "ERROR: SMTP_USER / SMTP_PASS not set in environment."

            msg = MIMEMultipart("alternative")
            msg["Subject"] = subject
            msg["From"] = from_email
            msg["To"] = to_email
            msg.attach(MIMEText(body_html, "html"))

            try:
                with smtplib.SMTP(smtp_host, smtp_port) as server:
                    server.starttls()
                    server.login(smtp_user, smtp_pass)
                    server.send_message(msg)
                status = "SUCCESS"
            except Exception as e:
                status = f"FAILED: {str(e)}"

        # Append to CSV log regardless of mode
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
