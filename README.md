# Bring Me Leeds Crew 🚀

Automated B2B lead generation pipeline built on [CrewAI](https://github.com/crewAIInc/crewAI).

**Pipeline:** Google Maps → Business Analysis → Demo Website → Proposal → Cold Outreach

---

## How It Works

5 AI agents run sequentially:

| Agent | Job |
|---|---|
| **Lead Scout** | Finds local businesses via Serper Maps API. Filters: 4★+, 50+ reviews, no/weak website |
| **Business Analyst** | Enriches each lead: scrapes their site, finds email & socials, identifies digital gaps |
| **Website Creator** | Generates a personalized HTML demo site and deploys it to GitHub Pages |
| **Proposal Writer** | Writes a personalized email/proposal with the demo link in the prospect's language |
| **Outreach Manager** | Sends emails via SMTP. **Requires human approval before sending** (safety gate) |

---

## Quick Start

### 1. Install dependencies
```bash
# Install uv (if you don't have it)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install project
uv sync
```

### 2. Configure environment
```bash
cp .env.example .env
# Edit .env with your API keys
```

Required keys:
- `OPENAI_API_KEY` — or `ANTHROPIC_API_KEY`
- `SERPER_API_KEY` — from [serper.dev](https://serper.dev) (2500 free requests)
- `SMTP_USER` + `SMTP_PASS` — Gmail App Password
- `GITHUB_TOKEN` — for GitHub Pages deployment of demo sites

### 3. Run

```bash
# Dry run (no emails sent — safe for testing all other steps)
uv run python src/lead_hunter/main.py --dry-run

# Live run (will pause for human approval before sending emails)
uv run python src/lead_hunter/main.py
```

---

## Project Structure

```
bring-me-leeds-crew/
├── .env.example                    # Copy to .env and fill in keys
├── pyproject.toml
├── knowledge/
│   ├── proposal_template.md        # KP template for proposal agent
│   ├── website_templates.json      # Template metadata
│   └── templates/                  # Jinja2 HTML templates
│       ├── restaurant.html         # Amber/warm — restaurants & cafes
│       ├── spa.html                # Purple/elegant — spa & wellness
│       ├── fitness.html            # Red/dark — gyms & martial arts
│       └── general.html            # Blue/clean — any business
└── src/lead_hunter/
    ├── config/
    │   ├── agents.yaml             # Agent definitions
    │   └── tasks.yaml              # Task definitions
    ├── tools/
    │   ├── google_maps_tool.py     # Serper Maps API search
    │   ├── website_generator.py    # HTML demo generator (Jinja2)
    │   ├── github_pages_deployer.py # Deploy demo to GitHub Pages
    │   └── email_sender.py         # SMTP sender + CSV log
    ├── crew.py                     # Crew orchestration
    └── main.py                     # Entry point
```

---

## Output

After a run, check `output/`:
- `output/demos/` — generated HTML demo sites (local copies)
- `output/outreach_log.csv` — log of all emails (sent/failed/dry_run)
- `output/outreach_report.md` — final pipeline summary

---

## Safety Features

- **`--dry-run` flag**: runs the full pipeline except actual email sending
- **`human_input=True`** on outreach task: pauses before sending and asks for confirmation
- **`MAX_EMAILS_PER_RUN`** env var: hard cap on emails per run (default: 10)
- All emails logged to CSV regardless of mode

---

## Development Phases

- [x] Phase 0: Project setup & structure
- [ ] Phase 1: Lead Scout + Analyst (just scraping, no emails)
- [ ] Phase 2: Website Creator + GitHub Pages deployment
- [ ] Phase 3: Proposal Writer + Outreach Manager
- [ ] Phase 4: Follow-up agent + Google Sheets CRM integration

---

*Powered by [CrewAI](https://github.com/crewAIInc/crewAI) · Built by ARS / Palm York Co., Ltd.*
