#!/usr/bin/env python
"""
Bring Me Leeds Crew — Lead Hunter Pipeline
Usage:
  uv run python src/lead_hunter/main.py              # live mode
  uv run python src/lead_hunter/main.py --dry-run    # no emails sent
"""
import sys
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


def run(dry_run: bool = False) -> None:
    # Ensure output directories exist before agents try to write to them
    Path("output/demos").mkdir(parents=True, exist_ok=True)
    Path("output/proposals").mkdir(parents=True, exist_ok=True)

    inputs = {
        "location": os.getenv("TARGET_LOCATION", "Koh Samui, Thailand"),
        "business_type": os.getenv("TARGET_BUSINESS_TYPE", "restaurants"),
        "max_leads": int(os.getenv("MAX_LEADS", "20")),
        "max_emails_per_run": int(os.getenv("MAX_EMAILS_PER_RUN", "10")),
        "dry_run": dry_run,
    }

    mode_label = "DRY RUN (emails will NOT be sent)" if dry_run else "LIVE"

    print("\n" + "=" * 60)
    print("  Bring Me Leeds Crew — Lead Hunter")
    print("=" * 60)
    print(f"  Location     : {inputs['location']}")
    print(f"  Business type: {inputs['business_type']}")
    print(f"  Max leads    : {inputs['max_leads']}")
    print(f"  Max emails   : {inputs['max_emails_per_run']}")
    print(f"  Mode         : {mode_label}")
    print("=" * 60 + "\n")

    # Import here so dotenv is loaded first
    from lead_hunter.crew import LeadHunterCrew

    LeadHunterCrew().crew().kickoff(inputs=inputs)


if __name__ == "__main__":
    dry_run_flag = "--dry-run" in sys.argv
    run(dry_run=dry_run_flag)
