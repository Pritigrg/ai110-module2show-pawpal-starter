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

## Smarter Scheduling

The scheduler has been extended with several algorithms beyond the basic daily plan:

- **Priority-based greedy scheduling** — tasks are ranked by priority (high → low) then duration (short → long) before budget fitting, so the most important care always gets in first.
- **Recurring task auto-creation** — when a `RecurringTask` is marked complete, the next occurrence (daily, weekly, or weekdays) is automatically added using `timedelta` date arithmetic.
- **Conflict detection** — `detect_conflicts()` uses an O(n²) interval sweep to find every pair of overlapping timed tasks. `conflict_warnings()` surfaces these as plain-English strings (same-pet or cross-pet) without crashing the program.
- **Chronological sorting** — `sort_tasks_by_time()` correctly orders 12-hour AM/PM time slots by parsing them into `datetime` objects before comparison.
- **Flexible task filtering** — `Owner.filter_tasks()` supports AND-chained filtering by completion status, pet name, and category in a single call.

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
