# Job Tracker — AI Assistant

A self-hostable job application tracker with an embedded AI assistant (Claude) that can view, add, update, and remove entries via natural language chat.

Built as a portfolio project. The demo is pre-loaded with sample data from a real job search.

**[Live Demo →](https://vfoster-repo.github.io/cdl-job-tracker-app/)** *(AI disabled — read-only preview)*

---

## Features

- **AI chat panel** — Ask "what's my status?" or "mark Ryder as rejected" and it happens
- **Live table updates** — Tracker re-renders instantly after AI modifies data
- **Filter by status** — Interview / Call Recruiter / Applied / Rejected / Not Applied
- **PWA-ready** — Installable on mobile via manifest
- **Zero database** — Data lives in a plain `jobs.json` file

## Stack

| Layer    | Tech |
|----------|------|
| Backend  | Python · FastAPI · Uvicorn |
| AI       | Anthropic Claude (tool use) |
| Frontend | Vanilla HTML/CSS/JS — no framework |
| Data     | `data/jobs.json` — flat file |

---

## Self-Host Setup

**Requirements:** Python 3.11+, an [Anthropic API key](https://console.anthropic.com/)

```bash
# 1. Clone
git clone https://github.com/vfoster-repo/cdl-job-tracker-app
cd cdl-job-tracker-app

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure API key
cp .env.example .env
# Edit .env and add your key: ANTHROPIC_API_KEY=sk-ant-...

# 4. Start the server
uvicorn main:app --reload

# 5. Open http://localhost:8000
```

The tracker loads at `http://localhost:8000`. Click **Ask AI** to open the chat panel.

---

## Project Layout

```
cdl-job-tracker-app/
├── main.py              ← FastAPI app (API + serves frontend)
├── requirements.txt
├── .env.example
├── data/
│   └── jobs.json        ← All job data (AI reads and writes this)
├── frontend/
│   ├── index.html       ← Full app (tracker + live AI chat)
│   └── manifest.json    ← PWA manifest
└── docs/
    └── index.html       ← GitHub Pages demo (static, AI disabled)
```

## GitHub Pages Demo

The `docs/` folder is the static demo served by GitHub Pages. To enable it:

1. Go to your repo **Settings → Pages**
2. Source: **Deploy from a branch**
3. Branch: `main`, folder: `/docs`
4. Save — your demo will be live at `https://your-username.github.io/cdl-job-tracker-app/`

---

## AI Capabilities

The assistant has five tools:

| Tool          | What it does |
|---------------|--------------|
| `list_jobs`   | Read all job entries |
| `get_job`     | Get details for one job by ID |
| `add_job`     | Add a new entry |
| `update_job`  | Change status, notes, pay, etc. |
| `delete_job`  | Remove an entry |

Example prompts:
- *"How many jobs have I applied to?"*
- *"Add Acme Trucking in Azle TX, $25/hr, status Applied"*
- *"Mark the Hirschbach job as Rejected"*
- *"What are my Call Recruiter leads?"*

---

## License

MIT
