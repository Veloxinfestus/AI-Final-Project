# Study Planner — Vercel-Ready API

## Project Purpose
This project generates a weekly study schedule from tasks, due dates, and daily availability. It is now finalized as a Python serverless API that deploys directly on Vercel.

## What Is Included
- Priority-aware study planning (`study_planner.py`)
- Serverless API entrypoint (`api/index.py`)
- Vercel config (`vercel.json`)
- Python dependency file (`requirements.txt`)

## Local Run
1. Install Python 3.11+.
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Run the API locally:
   - `python api/index.py`
4. Verify endpoints:
   - `GET http://127.0.0.1:5000/api/health`
   - `POST http://127.0.0.1:5000/api/plan`

## Deploy To Vercel
1. Push this repo to GitHub.
2. In Vercel, click **Add New Project** and import this repository.
3. Keep framework as **Other** (Vercel uses `vercel.json` + `@vercel/python`).
4. Deploy.

After deployment, call:
- `GET /api/health`
- `POST /api/plan`

## API Request Example
`POST /api/plan`

```json
{
  "week_of": "2026-04-20",
  "daily_study_hours": {
    "Monday": 2,
    "Tuesday": 2,
    "Wednesday": 1.5,
    "Thursday": 2,
    "Friday": 1,
    "Saturday": 4,
    "Sunday": 4
  },
  "tasks": [
    { "name": "Biology lab report", "due": "2026-04-23", "hours_needed": 5 },
    { "name": "Statistics problem set", "due": "2026-04-25", "hours_needed": 4 },
    { "name": "History reading quiz", "due": "2026-04-27", "hours_needed": 2 },
    { "name": "Physics midterm", "due": "2026-05-02", "hours_needed": 12 }
  ]
}
```

## API Response Shape
```json
{
  "week_of": "2026-04-20",
  "plan": {
    "Monday": { "Biology lab report": 2.0 },
    "Tuesday": { "Biology lab report": 2.0 },
    "Wednesday": { "Biology lab report": 1.0, "Statistics problem set": 0.5 },
    "Thursday": { "Statistics problem set": 2.0 },
    "Friday": { "Statistics problem set": 1.0 },
    "Saturday": { "History reading quiz": 2.0, "Physics midterm": 2.0 },
    "Sunday": { "Physics midterm": 4.0 }
  },
  "unallocated_hours": {
    "Physics midterm": 6.0
  }
}
```
