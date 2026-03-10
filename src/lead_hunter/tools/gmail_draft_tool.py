import os
import base64
import json
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path
from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

CREDENTIALS_FILE = Path("credentials.json")
TOKEN_FILE = Path("token.json")
SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]


def _get_gmail_service():
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from google.auth.transport.requests import Request
    from googleapiclient.discovery import build

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            if not CREDENTIALS_FILE.exists():
                raise FileNotFoundError(
                    "credentials.json not found. "
                    "Download it from Google Cloud Console → APIs → Gmail API → Credentials."
                )
            flow = InstalledAppFlow.from_client_secrets_file(
                str(CREDENTIALS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)

        TOKEN_FILE.write_text(creds.to_json())

    return build("gmail", "v1", credentials=creds)


class GmailDraftInput(BaseModel):
    to_email: str = Field(description="Recipient email address")
    subject: str = Field(description="Email subject line")
    body_html: str = Field(description="HTML body of the email")


class GmailDraftTool(BaseTool):
    name: str = "Gmail Draft Creator"
    description: str = (
        "Creates a Gmail draft for a prospect email — does NOT send it. "
        "You review and send manually from Gmail. "
        "Input: to_email, subject, body_html. "
        "Returns draft ID and Gmail link."
    )
    args_schema: Type[BaseModel] = GmailDraftInput

    def _run(self, to_email: str, subject: str, body_html: str) -> str:
        try:
            service = _get_gmail_service()
        except FileNotFoundError as e:
            return f"ERROR: {e}"
        except Exception as e:
            return f"ERROR: Gmail auth failed — {e}"

        # Wrap plain text in HTML if needed
        if not body_html.strip().startswith("<"):
            body_html = body_html.replace("\n", "<br>")

        msg = MIMEMultipart("alternative")
        msg["To"] = to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body_html, "html"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()

        try:
            draft = service.users().drafts().create(
                userId="me",
                body={"message": {"raw": raw}},
            ).execute()

            draft_id = draft["id"]
            return (
                f"SUCCESS: Draft created for {to_email} | "
                f"Subject: '{subject}' | "
                f"Open: https://mail.google.com/mail/#drafts/{draft_id}"
            )
        except Exception as e:
            return f"ERROR: Could not create draft — {e}"
