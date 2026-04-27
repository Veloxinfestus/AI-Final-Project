from __future__ import annotations

from datetime import date

from flask import Flask, jsonify, request

from study_planner import Task, build_plan

app = Flask(__name__)


@app.get("/")
def home():
    return jsonify(
        {
            "name": "AI Final Project Study Planner API",
            "status": "ok",
            "usage": {
                "health": "GET /api/health",
                "plan": "POST /api/plan",
            },
        }
    )


@app.get("/api/health")
def health():
    return jsonify({"status": "healthy"})


@app.post("/api/plan")
def plan():
    payload = request.get_json(silent=True) or {}
    week_of_raw = payload.get("week_of")
    week_of = date.fromisoformat(week_of_raw) if week_of_raw else None
    daily_hours = payload.get("daily_study_hours", {})
    tasks_payload = payload.get("tasks", [])

    tasks = [
        Task(
            name=item["name"],
            hours_needed=float(item["hours_needed"]),
            due=date.fromisoformat(item["due"]) if item.get("due") else None,
        )
        for item in tasks_payload
    ]

    result = build_plan(tasks=tasks, daily_hours=daily_hours, week_of=week_of)
    return jsonify(result)


if __name__ == "__main__":
    app.run(debug=True)
