from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import anthropic
import json
import os
from pathlib import Path
from dotenv import load_dotenv
from datetime import date
from typing import Any, List, Optional

load_dotenv()

app = FastAPI(title="CDL Job Tracker AI", docs_url=None, redoc_url=None)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_methods=["GET", "POST"],
    allow_headers=["Content-Type"],
)

BASE_DIR = Path(__file__).parent
DATA_FILE = BASE_DIR / "data" / "jobs.json"
FRONTEND_DIR = BASE_DIR / "frontend"


# ── Data helpers ──────────────────────────────────────────────────────────────

def load_jobs() -> dict:
    with open(DATA_FILE) as f:
        return json.load(f)


def save_jobs(data: dict) -> None:
    data["lastUpdated"] = date.today().isoformat()
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)


# ── Claude tools ──────────────────────────────────────────────────────────────

TOOLS = [
    {
        "name": "list_jobs",
        "description": (
            "Get all job applications in the tracker. Use this to answer questions "
            "about current status, counts, or to find a job by company name."
        ),
        "input_schema": {"type": "object", "properties": {}, "required": []},
    },
    {
        "name": "get_job",
        "description": "Get full details for a specific job by its ID slug.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Job ID slug, e.g. 'ryder-millsap'",
                }
            },
            "required": ["id"],
        },
    },
    {
        "name": "add_job",
        "description": "Add a new job application to the tracker.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "URL-friendly slug, e.g. 'company-name-city'",
                },
                "company": {"type": "string"},
                "title": {"type": "string"},
                "location": {"type": "string"},
                "status": {
                    "type": "string",
                    "enum": [
                        "Not Applied",
                        "Applied",
                        "Call Recruiter",
                        "Interview",
                        "Rejected",
                    ],
                },
                "date": {
                    "type": "string",
                    "description": "Application date YYYY-MM-DD, or omit if unknown",
                },
                "payRange": {
                    "type": "string",
                    "description": "Pay info, e.g. '$1,450+/wk' or '$23-25/hr'",
                },
                "notes": {"type": "string"},
            },
            "required": ["id", "company", "title", "location", "status"],
        },
    },
    {
        "name": "update_job",
        "description": (
            "Update one or more fields on an existing job. "
            "Use to change status, add notes, update pay info, etc."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Job ID slug to update",
                },
                "fields": {
                    "type": "object",
                    "description": (
                        'Key-value pairs to update, e.g. '
                        '{"status": "Rejected", "notes": "Pay too low"}'
                    ),
                },
            },
            "required": ["id", "fields"],
        },
    },
    {
        "name": "delete_job",
        "description": "Remove a job from the tracker entirely.",
        "input_schema": {
            "type": "object",
            "properties": {
                "id": {"type": "string", "description": "Job ID slug to delete"}
            },
            "required": ["id"],
        },
    },
]

SYSTEM_PROMPT = (
    "You are an AI assistant for a CDL-A truck driver job application tracker. "
    "You help manage and query job applications using the provided tools.\n\n"
    "Valid statuses: Not Applied, Applied, Call Recruiter, Interview, Rejected\n\n"
    "Guidelines:\n"
    "- Be concise — one or two sentences unless detail is requested.\n"
    "- When you modify data, briefly confirm what changed.\n"
    "- Use list_jobs first if you need to find a job by company name "
    "(IDs are slugs like 'ryder-millsap').\n"
    "- Dates use YYYY-MM-DD format."
)


# ── Tool executor ─────────────────────────────────────────────────────────────

def run_tool(name: str, tool_input: dict) -> str:
    try:
        data = load_jobs()
        jobs: list = data["jobs"]

        if name == "list_jobs":
            return json.dumps(jobs)

        if name == "get_job":
            job = next((j for j in jobs if j["id"] == tool_input["id"]), None)
            if not job:
                return json.dumps({"error": f"No job with id '{tool_input['id']}'"})
            return json.dumps(job)

        if name == "add_job":
            if any(j["id"] == tool_input["id"] for j in jobs):
                return json.dumps(
                    {"error": f"Job '{tool_input['id']}' already exists. Use update_job to modify it."}
                )
            job = {
                "id": tool_input["id"],
                "company": tool_input["company"],
                "title": tool_input["title"],
                "location": tool_input["location"],
                "status": tool_input["status"],
                "date": tool_input.get("date"),
                "payRange": tool_input.get("payRange", ""),
                "notes": tool_input.get("notes", ""),
            }
            jobs.append(job)
            data["jobs"] = jobs
            save_jobs(data)
            return json.dumps({"success": True, "added": job["id"]})

        if name == "update_job":
            job = next((j for j in jobs if j["id"] == tool_input["id"]), None)
            if not job:
                return json.dumps({"error": f"No job with id '{tool_input['id']}'"})
            job.update(tool_input["fields"])
            data["jobs"] = jobs
            save_jobs(data)
            return json.dumps(
                {"success": True,
                    "updated": tool_input["id"], "fields": tool_input["fields"]}
            )

        if name == "delete_job":
            original_count = len(jobs)
            data["jobs"] = [j for j in jobs if j["id"] != tool_input["id"]]
            if len(data["jobs"]) == original_count:
                return json.dumps({"error": f"No job with id '{tool_input['id']}'"})
            save_jobs(data)
            return json.dumps({"success": True, "deleted": tool_input["id"]})

        return json.dumps({"error": f"Unknown tool: {name}"})

    except Exception as exc:
        return json.dumps({"error": str(exc)})


# ── Content serialization ─────────────────────────────────────────────────────

def serialize_content(content) -> list:
    """Convert SDK content blocks to JSON-serializable dicts."""
    result = []
    for block in content:
        if block.type == "text":
            result.append({"type": "text", "text": block.text})
        elif block.type == "tool_use":
            result.append(
                {
                    "type": "tool_use",
                    "id": block.id,
                    "name": block.name,
                    "input": block.input,
                }
            )
    return result


# ── Routes ────────────────────────────────────────────────────────────────────

@app.get("/api/jobs")
def get_jobs():
    return load_jobs()


class ChatMessage(BaseModel):
    role: str
    content: Any  # str or list of content blocks


class ChatRequest(BaseModel):
    messages: List[ChatMessage]


@app.post("/api/chat")
def chat(req: ChatRequest):
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise HTTPException(
            status_code=503,
            detail="ANTHROPIC_API_KEY not configured. Add it to your .env file and restart the server.",
        )

    client = anthropic.Anthropic(api_key=api_key)
    messages = [{"role": m.role, "content": m.content} for m in req.messages]

    updated = False
    tools_used: list[str] = []

    while True:
        response = client.messages.create(
            model="claude-opus-4-5",
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        if response.stop_reason == "end_turn":
            text = next(
                (b.text for b in response.content if b.type == "text"), ""
            )
            return {"response": text, "updated": updated, "toolsUsed": tools_used}

        if response.stop_reason == "tool_use":
            serialized = serialize_content(response.content)
            messages.append({"role": "assistant", "content": serialized})

            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    result = run_tool(block.name, block.input)
                    tools_used.append(block.name)
                    if block.name in ("add_job", "update_job", "delete_job"):
                        updated = True
                    tool_results.append(
                        {
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        }
                    )

            messages.append({"role": "user", "content": tool_results})
            continue

        # Unexpected stop reason
        return {
            "response": "Unexpected response from AI.",
            "updated": False,
            "toolsUsed": tools_used,
        }


# ── Serve frontend (must be last) ─────────────────────────────────────────────

app.mount("/", StaticFiles(directory=str(FRONTEND_DIR), html=True), name="static")
