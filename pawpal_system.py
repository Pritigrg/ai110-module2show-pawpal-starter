from dataclasses import dataclass, field
from datetime import date, datetime, timedelta


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def parse_time(time_str: str) -> datetime:
    """Parse a time string like '08:00 AM' into a datetime for comparison."""
    for fmt in ("%I:%M %p", "%H:%M"):
        try:
            return datetime.strptime(time_str.strip(), fmt)
        except ValueError:
            continue
    raise ValueError(f"Unrecognised time format: '{time_str}'")


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""


@dataclass
class Task:
    name: str
    duration: int          # in minutes
    priority: int          # 1 (low) to 3 (high)
    category: str          # "walk", "feeding", "meds", "grooming"
    completed: bool = False
    time_slot: str = ""    # optional fixed start time, e.g. "08:00 AM"
    pet_name: str = ""     # which pet this task belongs to, e.g. "Buddy"

    def is_high_priority(self) -> bool:
        return self.priority == 3

    def __repr__(self) -> str:
        status = "done" if self.completed else "pending"
        time_info = f" @ {self.time_slot}" if self.time_slot else ""
        return f"[P{self.priority}] {self.name} ({self.category}, {self.duration}min{time_info}) [{status}]"


@dataclass
class RecurringTask(Task):
    """A task that repeats on a regular cadence (daily, weekly, weekdays).

    Each instance represents one occurrence on a specific ``due_date``.
    When the instance is completed, ``next_occurrence()`` produces the
    next copy so the task keeps appearing in future schedules automatically.
    """
    frequency: str = "daily"   # "daily", "weekly", "weekdays"
    # due_date tracks which calendar day *this* instance belongs to.
    # default_factory ensures every new instance gets today's date at
    # construction time rather than the date the class was first imported.
    due_date: str = field(default_factory=lambda: str(date.today()))

    def next_occurrence(self) -> "RecurringTask":
        """Return a pending copy of this task scheduled for the next occurrence.

        Frequency rules
        ---------------
        daily     → tomorrow
        weekly    → same weekday next week (+7 days)
        weekdays  → next calendar day, skipping Saturday and Sunday
        """
        current = date.fromisoformat(self.due_date) if self.due_date else date.today()

        if self.frequency == "weekly":
            next_date = current + timedelta(weeks=1)
        elif self.frequency == "weekdays":
            next_date = current + timedelta(days=1)
            while next_date.weekday() >= 5:   # 5 = Sat, 6 = Sun
                next_date += timedelta(days=1)
        else:                                  # "daily" (default)
            next_date = current + timedelta(days=1)

        return RecurringTask(
            name=self.name,
            duration=self.duration,
            priority=self.priority,
            category=self.category,
            completed=False,
            time_slot=self.time_slot,
            pet_name=self.pet_name,
            frequency=self.frequency,
            due_date=str(next_date),
        )

    def __repr__(self) -> str:
        base = super().__repr__()
        return f"{base} [recurring: {self.frequency}, due: {self.due_date}]"


@dataclass
class Appointment(Task):
    """A fixed-time task such as a vet visit or grooming appointment."""
    appt_date: str = ""    # e.g. "2026-04-15"
    time_slot: str = ""    # e.g. "2:00 PM"
    notes: str = ""

    def __post_init__(self):
        self.priority = 3
        self.category = "vet"

    def is_upcoming(self) -> bool:
        """Returns True if the appointment is in the future."""
        if not self.appt_date:
            return False
        return date.fromisoformat(self.appt_date) >= date.today()

    def __repr__(self) -> str:
        status = "upcoming" if self.is_upcoming() else "past"
        return (
            f"[Appt] {self.name} on {self.appt_date} at {self.time_slot} "
            f"({self.duration}min) [{status}]"
            + (f" — {self.notes}" if self.notes else "")
        )


# ---------------------------------------------------------------------------
# PetLog
# ---------------------------------------------------------------------------

class PetLog:
    """Tracks completed tasks over time to power the progress dashboard."""

    def __init__(self):
        self.entries: list[dict] = []   # {date, task_name, category, completed}

    def log_task(self, task: Task, completed: bool) -> None:
        """Record whether a task was completed on today's date."""
        self.entries.append({
            "date": str(date.today()),
            "task_name": task.name,
            "category": task.category,
            "completed": completed,
        })

    def get_completion_rate(self, days: int) -> float:
        """Return the % of tasks completed over the last N days (0.0 – 1.0)."""
        cutoff = date.today() - timedelta(days=days)
        recent = [
            e for e in self.entries
            if date.fromisoformat(e["date"]) >= cutoff
        ]
        if not recent:
            return 0.0
        return sum(1 for e in recent if e["completed"]) / len(recent)

    def tasks_by_category(self, category: str) -> list[dict]:
        """Return all log entries for a given category (e.g. 'meds')."""
        return [e for e in self.entries if e["category"] == category]

    def summary(self) -> str:
        """Return a human-readable progress summary for the dashboard."""
        total = len(self.entries)
        if total == 0:
            return "No tasks logged yet."
        done = sum(1 for e in self.entries if e["completed"])
        rate_7 = self.get_completion_rate(7)
        return (
            f"Total logged: {total} | Completed: {done} | "
            f"7-day completion rate: {rate_7:.0%}"
        )


# ---------------------------------------------------------------------------
# Owner
# ---------------------------------------------------------------------------

class Owner:
    def __init__(self, name: str, available_minutes: int, pet: Pet):
        self.name = name
        self.available_minutes = available_minutes
        self.pet = pet
        self.tasks: list[Task] = []
        self.appointments: list[Appointment] = []
        self.log = PetLog()

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        self.tasks.remove(task)

    def get_tasks(self) -> list[Task]:
        return self.tasks

    def filter_tasks(
        self,
        category: str | None = None,
        completed: bool | None = None,
        pet_name: str | None = None,
    ) -> list[Task]:
        """Return tasks matching every supplied filter (all filters are AND-ed).

        Parameters
        ----------
        category:  keep only tasks whose category matches (e.g. "meds")
        completed: True → done tasks only; False → pending only; None → all
        pet_name:  keep only tasks tagged to a specific pet (case-insensitive)
        """
        result = self.tasks
        if category is not None:
            result = [t for t in result if t.category == category]
        if completed is not None:
            result = [t for t in result if t.completed == completed]
        if pet_name is not None:
            result = [t for t in result if t.pet_name.lower() == pet_name.lower()]
        return result

    def get_recurring_tasks(self) -> list[RecurringTask]:
        """Return only the recurring tasks belonging to this owner."""
        return [t for t in self.tasks if isinstance(t, RecurringTask)]

    def add_appointment(self, appt: Appointment) -> None:
        self.appointments.append(appt)

    def get_upcoming_appointments(self) -> list[Appointment]:
        """Returns appointments that have not yet occurred, sorted by date."""
        upcoming = [a for a in self.appointments if a.is_upcoming()]
        return sorted(upcoming, key=lambda a: a.appt_date)

    def complete_task(self, task: Task) -> None:
        """Mark a task done, log it, and — for recurring tasks — automatically
        add the next occurrence to the task list."""
        task.completed = True
        self.log.log_task(task, completed=True)

        if isinstance(task, RecurringTask):
            self.add_task(task.next_occurrence())


# ---------------------------------------------------------------------------
# Schedule
# ---------------------------------------------------------------------------

class Schedule:
    def __init__(
        self,
        tasks: list[Task],
        reasoning: str,
        schedule_date: str = str(date.today()),
    ):
        self.tasks = tasks
        self.reasoning = reasoning
        self.schedule_date = schedule_date

    def total_duration(self) -> int:
        return sum(t.duration for t in self.tasks)

    def sort_by_time(self) -> list[Task]:
        """Return tasks ordered by their time_slot.

        Tasks without a time_slot are placed after all timed tasks.

        How the lambda key works
        ------------------------
        sorted() needs a *comparable value* to rank each item.  A lambda is
        an anonymous one-line function that produces that value on the fly:

            key=lambda t: parse_time(t.time_slot)
               ^^^^^^^^^                           — receives one Task object
                           ^^^^^^^^^^^^^^^^^^^^^^^ — returns a datetime to compare

        Why not sort the raw strings directly?
        - "07:00 AM" < "10:00 AM" works alphabetically, BUT
        - "07:00 PM" < "10:00 AM" is WRONG alphabetically — '7' < 'P'.
        So 12-hour strings must be parsed into datetime first.

        For 24-hour "HH:MM" strings the alphabetic trick DOES work because
        zero-padded numerics sort identically to numeric order:
            "07:00" < "10:00" < "18:00"  ✓

        Example (24-hour shortcut):
            sorted(tasks, key=lambda t: t.time_slot)   # only safe for HH:MM
        """
        timed = [t for t in self.tasks if t.time_slot]
        untimed = [t for t in self.tasks if not t.time_slot]
        # parse_time converts "HH:MM AM/PM" → datetime so the comparison is correct
        timed_sorted = sorted(timed, key=lambda t: parse_time(t.time_slot))
        return timed_sorted + untimed

    def display(self) -> str:
        if not self.tasks:
            return f"Schedule for {self.schedule_date}: No tasks fit within the time budget."
        ordered = self.sort_by_time()
        lines = [f"Schedule for {self.schedule_date} ({self.total_duration()} min total):"]
        for i, task in enumerate(ordered, 1):
            lines.append(f"  {i}. {task}")
        lines.append(f"\nReasoning: {self.reasoning}")
        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Scheduler
# ---------------------------------------------------------------------------

class Scheduler:
    @staticmethod
    def sort_tasks_by_time(tasks: list[Task]) -> list[Task]:
        """Sort a flat list of Task objects by time_slot, earliest first.

        The lambda acts as a *key function* — sorted() calls it once per task
        and uses the returned value to decide the order:

            sorted(tasks, key=lambda t: parse_time(t.time_slot))

        Two common lambda patterns for time sorting
        -------------------------------------------
        1. 24-hour "HH:MM" strings (zero-padded) — alphabetic order works:
               sorted(tasks, key=lambda t: t.time_slot)

        2. 12-hour "HH:MM AM/PM" strings — must convert to datetime first:
               sorted(tasks, key=lambda t: parse_time(t.time_slot))

        We use approach 2 here because our time_slot values use AM/PM.
        Tasks with no time_slot are placed at the end.
        """
        timed = [t for t in tasks if t.time_slot]
        untimed = [t for t in tasks if not t.time_slot]
        return sorted(timed, key=lambda t: parse_time(t.time_slot)) + untimed

    def generate_schedule(self, owner: Owner) -> "Schedule":
        """Build a daily Schedule for the given owner using a greedy priority algorithm.

        Retrieval path:
          owner.get_tasks()          → flat list of Task objects
          _rank_tasks(tasks)         → sorted by priority (desc) then duration (asc)
          _fit_within_budget(...)    → trimmed to owner.available_minutes

        The greedy approach always schedules the highest-priority tasks first.
        Tasks that do not fit within the remaining time budget are skipped entirely.

        Args:
            owner: The Owner whose tasks and available_minutes drive the schedule.

        Returns:
            A Schedule containing the selected tasks and a plain-English reasoning string.
        """
        all_tasks = owner.get_tasks()
        ranked = self._rank_tasks(all_tasks)
        selected = self._fit_within_budget(ranked, owner.available_minutes)

        reasoning = (
            f"Selected {len(selected)} of {len(all_tasks)} tasks for "
            f"{owner.pet.name} within {owner.available_minutes} min. "
            f"High-priority tasks were scheduled first."
        )
        return Schedule(tasks=selected, reasoning=reasoning)

    def _rank_tasks(self, tasks: list[Task]) -> list[Task]:
        """Sort tasks so the most important ones are scheduled first.

        Sorting key: (-priority, duration)
          - Primary:   priority descending  → P3 before P2 before P1
          - Secondary: duration ascending   → shorter tasks win ties,
                       maximising the number of tasks that fit the budget.

        Args:
            tasks: Unsorted list of Task objects.

        Returns:
            A new list sorted by the composite key; the input is not modified.
        """
        return sorted(tasks, key=lambda t: (-t.priority, t.duration))

    def _fit_within_budget(self, tasks: list[Task], budget: int) -> list[Task]:
        """Greedily select tasks that fit within the available time budget.

        Iterates the pre-ranked task list in order and includes each task only
        if its duration fits within the remaining minutes.  This is a greedy
        approximation of the 0/1 knapsack problem — not globally optimal, but
        predictable and fast for the small task lists typical in pet care.

        Args:
            tasks:  Tasks in priority order (output of _rank_tasks).
            budget: Total minutes available for the day.

        Returns:
            Subset of tasks whose durations sum to at most ``budget`` minutes.
        """
        selected = []
        remaining = budget
        for task in tasks:
            if task.duration <= remaining:
                selected.append(task)
                remaining -= task.duration
        return selected

    def detect_conflicts(self, tasks: list[Task]) -> list[tuple[Task, Task]]:
        """Return every pair of tasks whose time windows overlap.

        Accepts a flat list so it works for a single schedule *or* for tasks
        pooled across multiple owners/pets.  Only tasks with a ``time_slot``
        are considered — tasks without one are silently skipped.

        Two tasks conflict when their [start, end) intervals intersect:
            start_a < end_b  AND  start_b < end_a
        """
        timed = [t for t in tasks if t.time_slot]
        conflicts: list[tuple[Task, Task]] = []
        for i in range(len(timed)):
            for j in range(i + 1, len(timed)):
                t1, t2 = timed[i], timed[j]
                start1 = parse_time(t1.time_slot)
                end1   = start1 + timedelta(minutes=t1.duration)
                start2 = parse_time(t2.time_slot)
                end2   = start2 + timedelta(minutes=t2.duration)
                if start1 < end2 and start2 < end1:
                    conflicts.append((t1, t2))
        return conflicts

    def conflict_warnings(self, tasks: list[Task]) -> list[str]:
        """Return human-readable warning strings for every detected conflict.

        Returns an empty list when no conflicts exist — never raises.
        Each message notes whether the overlap is same-pet or cross-pet so
        the caller can surface it without any extra parsing.

        Strategy: lightweight — report and continue, never crash.
        """
        warnings: list[str] = []
        for t1, t2 in self.detect_conflicts(tasks):
            start1 = parse_time(t1.time_slot)
            end1   = start1 + timedelta(minutes=t1.duration)
            start2 = parse_time(t2.time_slot)
            end2   = start2 + timedelta(minutes=t2.duration)

            # Overlap window — helpful to show how bad the clash is
            overlap_start = max(start1, start2)
            overlap_end   = min(end1,   end2)
            overlap_mins  = int((overlap_end - overlap_start).total_seconds() / 60)

            if t1.pet_name and t2.pet_name and t1.pet_name != t2.pet_name:
                scope = f"CROSS-PET ({t1.pet_name} & {t2.pet_name})"
            elif t1.pet_name:
                scope = f"SAME-PET ({t1.pet_name})"
            else:
                scope = "CONFLICT"

            warnings.append(
                f"⚠ {scope}: '{t1.name}' ({t1.time_slot}, {t1.duration}min) "
                f"overlaps '{t2.name}' ({t2.time_slot}, {t2.duration}min) "
                f"— {overlap_mins}min overlap"
            )
        return warnings
