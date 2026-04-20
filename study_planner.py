#!/usr/bin/env python3
"""
Weekly study planner: assignments/exams with due dates + availability after work
→ suggested hours per task per day for the chosen week.
Uses only the Python standard library.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Iterable


WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]


def parse_date(s: str) -> date:
    s = s.strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date: {s!r}. Use YYYY-MM-DD, MM/DD/YYYY, or DD/MM/YYYY.")


def week_start_on(d: date, start_on_monday: bool = True) -> date:
    """First day of the calendar week containing d."""
    if start_on_monday:
        return d - timedelta(days=d.weekday())
    # Sunday-start week
    return d - timedelta(days=(d.weekday() + 1) % 7)


@dataclass
class Task:
    """Something to prepare for (assignment, exam, etc.)."""

    name: str
    due: date
    hours_needed: float = 3.0

    def days_until(self, from_day: date) -> int:
        return max(0, (self.due - from_day).days)


@dataclass
class WeekPlan:
    week_of: date
    daily_capacity: dict[str, float]
    # task_name -> day_name -> hours
    allocation: dict[str, dict[str, float]] = field(default_factory=dict)

    def total_allocated(self, task: str) -> float:
        return sum(self.allocation.get(task, {}).values())

    def day_total(self, day: str) -> float:
        return sum(t.get(day, 0.0) for t in self.allocation.values())


def _priority_score(task: Task, day: date) -> float:
    """Higher = more deserving of time on this day."""
    d = task.days_until(day)
    if d == 0:
        return task.hours_needed * 1_000.0
    # Softer urgency curve; still favors nearer due dates
    return task.hours_needed / (d**1.5 + 0.5)


def generate_weekly_plan(
    week_start: date,
    tasks: Iterable[Task],
    daily_hours: dict[str, float],
) -> WeekPlan:
    """
    Greedy day-by-day allocation: each day, assign hours to tasks by priority
    until daily capacity is used or all remaining need is covered.
    """
    tasks = list(tasks)
    remaining = {t.name: float(t.hours_needed) for t in tasks}
    allocation: dict[str, dict[str, float]] = {t.name: {d: 0.0 for d in WEEKDAYS} for t in tasks}

    for i, day_name in enumerate(WEEKDAYS):
        day = week_start + timedelta(days=i)
        cap = max(0.0, float(daily_hours.get(day_name, 0.0)))
        left = cap

        # Include due day; ignore tasks that ended before this week
        active = [
            t
            for t in tasks
            if t.due >= week_start and day <= t.due and remaining[t.name] > 1e-6
        ]
        while left > 1e-6 and active:
            scores = [(t, _priority_score(t, day)) for t in active]
            total = sum(s for _, s in scores) or 1.0
            # Proposed slice for this iteration (small steps for smoother spread)
            step = min(left, 0.5)
            for t, s in scores:
                if left <= 1e-6:
                    break
                share = step * (s / total)
                take = min(share, remaining[t.name], left)
                if take <= 1e-9:
                    continue
                allocation[t.name][day_name] += take
                remaining[t.name] -= take
                left -= take
            active = [
                t
                for t in tasks
                if t.due >= week_start and day <= t.due and remaining[t.name] > 1e-6
            ]

    return WeekPlan(week_of=week_start, daily_capacity=dict(daily_hours), allocation=allocation)


def print_plan(plan: WeekPlan, tasks: list[Task]) -> None:
    print(f"\nStudy plan for week of {plan.week_of.isoformat()} (Mon–Sun)\n")
    col_w = 12
    header = f"{'Task':<28}" + "".join(f"{d[:3]:>4}" for d in WEEKDAYS) + f"{'Tot':>6}"
    print(header)
    print("-" * len(header))

    by_name = {t.name: t for t in tasks}
    for name in sorted(plan.allocation.keys(), key=lambda n: (by_name[n].due, n)):
        row = plan.allocation[name]
        cells = "".join(f"{row[d]:>4.1f}" if row[d] > 0 else f"{'—':>4}" for d in WEEKDAYS)
        tot = plan.total_allocated(name)
        due = by_name[name].due.isoformat()
        print(f"{name[:26]:<28}{cells}{tot:>6.1f}  (due {due})")

    print("-" * len(header))
    cap = "".join(f"{plan.daily_capacity.get(d, 0):>4.1f}" for d in WEEKDAYS)
    used = "".join(f"{plan.day_total(d):>4.1f}" for d in WEEKDAYS)
    print(f"{'Capacity (h)':<28}{cap}{sum(plan.daily_capacity.get(d, 0) for d in WEEKDAYS):>6.1f}")
    print(f"{'Allocated (h)':<28}{used}{sum(plan.day_total(d) for d in WEEKDAYS):>6.1f}")

    # Warnings: under-allocated tasks
    short = []
    for t in tasks:
        got = plan.total_allocated(t.name)
        if got + 1e-3 < t.hours_needed:
            short.append((t.name, t.hours_needed - got))
    if short:
        print("\nNote: weekly capacity was not enough to cover all estimated hours.")
        for n, gap in sorted(short, key=lambda x: -x[1]):
            print(f"  • {n}: about {gap:.1f} h still unscheduled this week (add capacity or spread over earlier weeks).")


def load_config(path: Path) -> tuple[date, dict[str, float], list[Task]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    week_of = parse_date(data["week_of"])
    week_start = week_start_on(week_of, start_on_monday=True)
    daily = data.get("daily_study_hours", {})
    missing = [d for d in WEEKDAYS if d not in daily]
    if missing:
        raise ValueError(f"daily_study_hours missing keys: {missing}")
    tasks = []
    for item in data.get("tasks", []):
        tasks.append(
            Task(
                name=item["name"],
                due=parse_date(item["due"]),
                hours_needed=float(item.get("hours_needed", 3)),
            )
        )
    if not tasks:
        raise ValueError("config must include a non-empty 'tasks' list")
    return week_start, daily, tasks


def interactive_config() -> tuple[date, dict[str, float], list[Task]]:
    print("Study planner — enter your week, availability, and tasks.\n")
    raw = input("Week to plan (any date in that week, YYYY-MM-DD) [default: today]: ").strip()
    anchor = parse_date(raw) if raw else date.today()
    week_start = week_start_on(anchor, start_on_monday=True)
    print(f"Using week starting Monday {week_start.isoformat()}.\n")

    print("Study hours available each day (after work / other commitments):")
    daily: dict[str, float] = {}
    for d in WEEKDAYS:
        s = input(f"  {d} (hours) [0]: ").strip()
        daily[d] = float(s) if s else 0.0

    tasks: list[Task] = []
    print("\nTasks (blank name to finish).")
    while True:
        name = input("Task name (e.g. Calc midterm): ").strip()
        if not name:
            break
        due_s = input("  Due date (YYYY-MM-DD): ").strip()
        due = parse_date(due_s)
        h_s = input("  Estimated study hours [3]: ").strip()
        h = float(h_s) if h_s else 3.0
        tasks.append(Task(name=name, due=due, hours_needed=h))

    if not tasks:
        print("No tasks entered.", file=sys.stderr)
        sys.exit(1)
    return week_start, daily, tasks


def main() -> None:
    p = argparse.ArgumentParser(description="Generate a weekly study plan from due dates and availability.")
    p.add_argument(
        "--config",
        type=Path,
        help="JSON file with week_of, daily_study_hours, tasks",
    )
    args = p.parse_args()

    if args.config:
        week_start, daily, tasks = load_config(args.config)
    else:
        week_start, daily, tasks = interactive_config()

    skipped = [t for t in tasks if t.due < week_start]
    active = [t for t in tasks if t.due >= week_start]
    if skipped:
        print("Skipping tasks already due before this week:", file=sys.stderr)
        for t in skipped:
            print(f"  • {t.name} (was due {t.due.isoformat()})", file=sys.stderr)
        print(file=sys.stderr)
    if not active:
        print("No tasks due on or after the start of this week.", file=sys.stderr)
        sys.exit(1)

    plan = generate_weekly_plan(week_start, active, daily)
    print_plan(plan, active)


if __name__ == "__main__":
    main()
