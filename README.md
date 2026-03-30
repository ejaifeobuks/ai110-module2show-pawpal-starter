# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## Smarter Scheduling

The `Scheduler` class has been extended with four algorithmic features:

**Sort by time** (`sort_by_time`)
All tasks across every pet are ordered by time-of-day using a lambda that formats `due_date` as an `"HH:MM"` string. This surfaces the daily routine pattern regardless of which calendar date a task falls on.

**Filter tasks** (`filter_tasks`)
Tasks can be narrowed by completion status (`"pending"` / `"done"`), by pet name, or both at once. Both parameters are optional — omitting one skips that filter entirely.

**Auto-rescheduling** (`Task.frequency` + `Scheduler.mark_task_complete`)
Tasks now carry an optional `frequency` field (`"daily"` or `"weekly"`). When `mark_task_complete` is called, it delegates to `Task.mark_complete()`, which marks the task done and returns a new instance shifted forward by one day (`timedelta(days=1)`) or one week (`timedelta(weeks=1)`). The Scheduler then adds the new task to the correct pet automatically, keeping recurring routines alive without manual re-entry.

**Conflict detection** (`detect_conflicts`)
The scheduler groups all tasks by their exact `"YYYY-MM-DD HH:MM"` slot. Any slot with more than one task produces a human-readable warning string. The method never raises an exception — callers receive an empty list when the schedule is clean.
