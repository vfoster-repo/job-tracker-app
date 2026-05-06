# Job Tracker — AI Assistant

A self-hostable job application tracker powered by an embedded AI assistant (Claude). Every aspect of the tracker — adding jobs, updating statuses, recording notes, organizing entries — is handled exclusively through conversation with the AI. The UI is a real-time dashboard: a clean, filterable table that lets you see the status of every opportunity at a glance, with a rich detail panel that surfaces pay, schedule, requirements, benefits, alerts, and recruiter info for any listing in a single click.

Built as a portfolio project. The demo is pre-loaded with sample data from a real CDL-A job search in the DFW/Weatherford TX area.

**[Live Demo →](https://vfoster-repo.github.io/job-tracker-app/)** *(AI disabled — read-only preview)*

---

## What It Does

The dashboard is a read-only view — you never fill out a form or edit a field directly. All interaction goes through the **AI Assistant**:

- *"Add Northside Tech in Austin TX, $95K/yr, status Applied, remote-friendly, contact is Sarah at 555-1234"*
- *"Mark Acme Corp as Call Recruiter and note they reached out — interview scheduled for next week"*
- *"What jobs am I still waiting to hear back from?"*
- *"Reject the Globex position — the salary is too low and it's fully on-site"*
- *"Update my profile — I have 5 years of experience and I'm targeting $90K+"*

The AI reads and writes `jobs.json` directly. The table re-renders live after every change.

---

## Features

- **AI-managed tracker** — All adds, edits, status changes, and notes happen through natural language chat. No forms, no manual data entry.
- **At-a-glance detail panel** — Click any row to see the full picture: pay range, schedule, requirements, benefits, recruiter contact, apply link, and industry-specific details.
- **Alert callouts** — Color-coded flags on each job: action items (amber), useful info (blue), disqualifiers and rejection reasons (red). Never lose track of why a job was skipped.
- **Flexible details field** — The AI stores any industry-specific data as key-value pairs (e.g. `Equipment: Flatbed`, `Endorsements: HazMat+Tanker`, or `Stack: React/Node` for tech jobs). Works for any industry.
- **User profile memory** — The AI remembers your background, qualifications, target salary, and preferences across every session. It uses this context to give relevant answers without re-explaining yourself every time.
- **Live table updates** — Tracker re-renders instantly after the AI modifies data.
- **Filter by status** — Interview / Call Recruiter / Applied / Rejected / Not Applied.
- **PWA-ready** — Installable on mobile via manifest.
- **Zero database** — Data lives in plain JSON files (`jobs.json`, `profile.json`).

---

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | Python · FastAPI · Uvicorn |
| AI       | Anthropic Claude (tool use / agentic loop) |
| Frontend | Vanilla HTML/CSS/JS — no framework |
| Data     | `data/jobs.json` + `data/profile.json` — flat files |

---

## Self-Host Setup

**Requirements:** Python 3.11+, an [Anthropic API key](https://console.anthropic.com/)

```bash
# 1. Clone
git clone https://github.com/vfoster-repo/job-tracker-app
cd job-tracker-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your key: ANTHROPIC_API_KEY=sk-ant-...

# 4. Start the server
uvicorn main:app --reload

# 5. Open http://localhost:8000
```

The tracker loads at `http://localhost:8000`. Click **AI Assistant** to open the chat panel and start talking.

---

## Project Layout

```
job-tracker-app/
├── main.py              ← FastAPI app (API + agentic loop + serves frontend)
├── requirements.txt
├── .env.example
├── data/
│   ├── jobs.json        ← All job data (AI reads and writes this)
│   └── profile.json     ← User profile (injected into every AI session)
├── frontend/
│   ├── index.html       ← Full app (tracker + live AI chat)
│   └── manifest.json    ← PWA manifest
└── docs/
    └── index.html       ← GitHub Pages static demo (AI disabled)
```

---

## AI Capabilities

The assistant has seven tools:

| Tool             | What it does |
|------------------|--------------|
| `list_jobs`      | Read all job entries |
| `get_job`        | Get full details for one job |
| `add_job`        | Add a new entry with all rich fields |
| `update_job`     | Change any field — status, pay, notes, alerts, details |
| `delete_job`     | Remove an entry |
| `get_profile`    | Read the saved user profile |
| `update_profile` | Update background, qualifications, salary target, preferences |

The system prompt is rebuilt on every request with the current profile injected at the top — the AI always has full context about who it's working with.

---

## Author

**Victor Foster**
- GitHub: [@vfoster-repo](https://github.com/vfoster-repo)
- LinkedIn: [Victor Foster](https://linkedin.com/in/vfoster-connect)
- Email: victorfoster@hotmail.com

---

## License

MIT
