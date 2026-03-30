from dataclasses import dataclass, field
from datetime import date


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

    def is_high_priority(self) -> bool:
        pass

    def __repr__(self) -> str:
        pass


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
        pass

    def __repr__(self) -> str:
        pass


class PetLog:
    """Tracks completed tasks over time to power the progress dashboard."""

    def __init__(self):
        self.entries: list[dict] = []   # {date, task_name, category, completed}

    def log_task(self, task: Task, completed: bool) -> None:
        """Record whether a task was completed on today's date."""
        pass

    def get_completion_rate(self, days: int) -> float:
        """Return the % of tasks completed over the last N days (0.0 – 1.0)."""
        pass

    def tasks_by_category(self, category: str) -> list[dict]:
        """Return all log entries for a given category (e.g. 'meds')."""
        pass

    def summary(self) -> str:
        """Return a human-readable progress summary for the dashboard."""
        pass


class Owner:
    def __init__(self, name: str, available_minutes: int, pet: Pet):
        self.name = name
        self.available_minutes = available_minutes
        self.pet = pet
        self.tasks: list[Task] = []
        self.appointments: list[Appointment] = []
        self.log = PetLog()

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass

    def get_tasks(self) -> list[Task]:
        pass

    def add_appointment(self, appt: Appointment) -> None:
        pass

    def get_upcoming_appointments(self) -> list[Appointment]:
        """Returns appointments that have not yet occurred, sorted by date."""
        pass


class Schedule:
    def __init__(self, tasks: list[Task], reasoning: str, schedule_date: str = str(date.today())):
        self.tasks = tasks
        self.reasoning = reasoning
        self.schedule_date = schedule_date

    def total_duration(self) -> int:
        pass

    def display(self) -> str:
        pass


class Scheduler:
    def generate_schedule(self, owner: Owner) -> Schedule:
        pass

    def _rank_tasks(self, tasks: list[Task]) -> list[Task]:
        pass

    def _fit_within_budget(self, tasks: list[Task], budget: int) -> list[Task]:
        pass
