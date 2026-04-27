#!/usr/bin/env python3

from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, Iterable, List, Tuple

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


@dataclass
class Task:
    name: str
    hours_needed: float
    due: date | None = None


def start_of_week(any_day: date) -> date:
    return any_day - timedelta(days=any_day.weekday())


def _task_sort_key(task: Task, week_start: date) -> Tuple[int, float]:
    due_offset = 999 if task.due is None else max(0, (task.due - week_start).days)
    # Urgent tasks first, then larger tasks.
    return (due_offset, -task.hours_needed)


def build_plan(tasks: Iterable[Task], daily_hours: Dict[str, float], week_of: date | None = None):
    effective_week = week_of or start_of_week(date.today())
    ordered_tasks = sorted(list(tasks), key=lambda t: _task_sort_key(t, effective_week))
    remaining = {task.name: float(task.hours_needed) for task in ordered_tasks}
    plan: Dict[str, Dict[str, float]] = {day: {} for day in WEEKDAYS}

    for day_idx, day_name in enumerate(WEEKDAYS):
        available = max(0.0, float(daily_hours.get(day_name, 0.0)))
        if available <= 0:
            continue

        day_date = effective_week + timedelta(days=day_idx)
        eligible_tasks: List[Task] = []
        for task in ordered_tasks:
            if remaining[task.name] <= 0:
                continue
            # Prefer tasks that are due now/soon, but still allow undated tasks.
            if task.due is None or task.due >= day_date:
                eligible_tasks.append(task)

        if not eligible_tasks:
            eligible_tasks = [task for task in ordered_tasks if remaining[task.name] > 0]

        for task in eligible_tasks:
            if available <= 0:
                break
            take = min(available, remaining[task.name])
            if take <= 0:
                continue
            plan[day_name][task.name] = round(plan[day_name].get(task.name, 0.0) + take, 2)
            remaining[task.name] = round(remaining[task.name] - take, 2)
            available = round(available - take, 2)

    return {
        "week_of": effective_week.isoformat(),
        "plan": plan,
        "unallocated_hours": {name: hours for name, hours in remaining.items() if hours > 0},
    }


def load_config(config_path: str):
    raw = Path(config_path).read_text(encoding="utf-8")
    payload = json.loads(raw)
    week_of = date.fromisoformat(payload["week_of"]) if payload.get("week_of") else None
    daily_hours = payload.get("daily_study_hours", {})
    tasks = [
        Task(
            name=item["name"],
            hours_needed=float(item["hours_needed"]),
            due=date.fromisoformat(item["due"]) if item.get("due") else None,
        )
        for item in payload.get("tasks", [])
    ]
    return tasks, daily_hours, week_of


def print_plan(result):
    print("\nWeekly Study Plan\n")
    for day in WEEKDAYS:
        print(f"{day}:")
        day_plan = result["plan"][day]
        if not day_plan:
            print("  (no study)")
        else:
            for task, hrs in day_plan.items():
                print(f"  {task}: {hrs:.1f}h")
        print()
    if result["unallocated_hours"]:
        print("Unallocated hours (increase daily availability to fit all work):")
        for task, hrs in result["unallocated_hours"].items():
            print(f"  {task}: {hrs:.1f}h")


def main():
    tasks, daily_hours, week_of = load_config("example_config.json")
    result = build_plan(tasks, daily_hours, week_of)
    print_plan(result)


if __name__ == "__main__":
    main()
