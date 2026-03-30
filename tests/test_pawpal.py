import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from pawpal_system import Pet, Task, RecurringTask, Owner, Scheduler


class TestTaskCompletion(unittest.TestCase):
    """Test 1: Completing a task changes its status from False to True."""

    def test_complete_task_sets_completed_true(self):
        pet = Pet(name="Buddy", species="Dog", age=3)
        owner = Owner(name="Alex", available_minutes=60, pet=pet)
        task = Task(name="Morning walk", duration=30, priority=2, category="walk")

        owner.add_task(task)

        # Before: task should NOT be completed yet
        self.assertFalse(task.completed, "Task should start as not completed")

        owner.complete_task(task)

        # After: task should now be marked completed
        self.assertTrue(task.completed, "Task should be completed after calling complete_task()")


class TestTaskAddition(unittest.TestCase):
    """Test 2: Adding a task to an Owner increases the task count."""

    def test_add_task_increases_task_count(self):
        pet = Pet(name="Whiskers", species="Cat", age=5)
        owner = Owner(name="Alex", available_minutes=60, pet=pet)

        # Start with zero tasks
        self.assertEqual(len(owner.get_tasks()), 0, "Owner should start with no tasks")

        owner.add_task(Task(name="Feed wet food", duration=5, priority=3, category="feeding"))
        owner.add_task(Task(name="Clean litter",  duration=10, priority=2, category="grooming"))

        # Should now have exactly 2 tasks
        self.assertEqual(len(owner.get_tasks()), 2, "Owner should have 2 tasks after adding two")


# ---------------------------------------------------------------------------
# Test 3: Sorting correctness
# ---------------------------------------------------------------------------

class TestSortingByTime(unittest.TestCase):
    """Verify that sort_tasks_by_time returns tasks in chronological order."""

    def setUp(self):
        self.scheduler = Scheduler()

    def test_tasks_sorted_chronologically(self):
        """Tasks with AM/PM time slots should come out earliest-first."""
        t1 = Task(name="Evening meds",   duration=5,  priority=1, category="meds",     time_slot="07:00 PM")
        t2 = Task(name="Morning walk",   duration=30, priority=2, category="walk",     time_slot="07:00 AM")
        t3 = Task(name="Afternoon feed", duration=10, priority=3, category="feeding",  time_slot="12:00 PM")

        # Intentionally pass them out of order
        result = self.scheduler.sort_tasks_by_time([t1, t2, t3])

        self.assertEqual(result[0].name, "Morning walk",   "07:00 AM should be first")
        self.assertEqual(result[1].name, "Afternoon feed", "12:00 PM should be second")
        self.assertEqual(result[2].name, "Evening meds",   "07:00 PM should be last")

    def test_untimed_tasks_placed_at_end(self):
        """Tasks without a time_slot must appear after all timed tasks."""
        timed   = Task(name="Walk",  duration=20, priority=2, category="walk",    time_slot="09:00 AM")
        untimed = Task(name="Brush", duration=10, priority=2, category="grooming")  # no time_slot

        result = self.scheduler.sort_tasks_by_time([untimed, timed])

        self.assertEqual(result[0].name, "Walk",  "Timed task should come first")
        self.assertEqual(result[1].name, "Brush", "Untimed task should come last")

    def test_all_untimed_tasks_preserves_count(self):
        """When no tasks have a time_slot, all tasks are still returned."""
        tasks = [
            Task(name="Task A", duration=10, priority=1, category="grooming"),
            Task(name="Task B", duration=10, priority=2, category="feeding"),
        ]
        result = self.scheduler.sort_tasks_by_time(tasks)
        self.assertEqual(len(result), 2, "All untimed tasks should be returned")


# ---------------------------------------------------------------------------
# Test 4: Recurrence logic
# ---------------------------------------------------------------------------

class TestRecurringTasks(unittest.TestCase):
    """Confirm that completing a recurring task creates the correct next occurrence."""

    def test_daily_task_creates_next_day_occurrence(self):
        """Completing a daily task adds a new pending task for tomorrow."""
        pet   = Pet(name="Rex", species="Dog", age=2)
        owner = Owner(name="Sam", available_minutes=120, pet=pet)

        task = RecurringTask(
            name="Morning walk", duration=30, priority=2,
            category="walk", frequency="daily", due_date="2026-04-01"
        )
        owner.add_task(task)
        self.assertEqual(len(owner.get_tasks()), 1)

        owner.complete_task(task)

        # completing should add exactly one new occurrence
        tasks = owner.get_tasks()
        self.assertEqual(len(tasks), 2, "Completing a recurring task should add one new occurrence")

        next_task = tasks[1]
        self.assertEqual(next_task.due_date, "2026-04-02", "Daily task should be due the following day")
        self.assertFalse(next_task.completed, "New occurrence must start as pending")

    def test_weekly_task_creates_next_week_occurrence(self):
        """Completing a weekly task adds a task exactly 7 days later."""
        pet   = Pet(name="Rex", species="Dog", age=2)
        owner = Owner(name="Sam", available_minutes=120, pet=pet)

        task = RecurringTask(
            name="Bath time", duration=45, priority=2,
            category="grooming", frequency="weekly", due_date="2026-04-01"
        )
        owner.add_task(task)
        owner.complete_task(task)

        next_task = owner.get_tasks()[1]
        self.assertEqual(next_task.due_date, "2026-04-08", "Weekly task should be due 7 days later")

    def test_weekday_task_skips_weekend(self):
        """Completing a weekdays task on Friday should schedule for Monday."""
        pet   = Pet(name="Rex", species="Dog", age=2)
        owner = Owner(name="Sam", available_minutes=120, pet=pet)

        # 2026-04-03 is a Friday
        task = RecurringTask(
            name="Pill", duration=5, priority=3,
            category="meds", frequency="weekdays", due_date="2026-04-03"
        )
        owner.add_task(task)
        owner.complete_task(task)

        next_task = owner.get_tasks()[1]
        # 2026-04-06 is Monday — Saturday and Sunday must be skipped
        self.assertEqual(next_task.due_date, "2026-04-06", "Weekday task completed Friday should roll to Monday")

    def test_original_task_is_marked_completed(self):
        """The original recurring task instance should be marked done after completion."""
        pet   = Pet(name="Rex", species="Dog", age=2)
        owner = Owner(name="Sam", available_minutes=120, pet=pet)

        task = RecurringTask(
            name="Feed", duration=10, priority=3,
            category="feeding", frequency="daily", due_date="2026-04-01"
        )
        owner.add_task(task)
        owner.complete_task(task)

        self.assertTrue(task.completed, "Original task should be marked completed")


# ---------------------------------------------------------------------------
# Test 5: Conflict detection
# ---------------------------------------------------------------------------

class TestConflictDetection(unittest.TestCase):
    """Verify that the Scheduler correctly flags overlapping time slots."""

    def setUp(self):
        self.scheduler = Scheduler()

    def test_same_start_time_is_a_conflict(self):
        """Two tasks starting at the exact same time must be flagged."""
        t1 = Task(name="Walk",  duration=30, priority=2, category="walk",    time_slot="09:00 AM")
        t2 = Task(name="Bath",  duration=20, priority=1, category="grooming", time_slot="09:00 AM")

        conflicts = self.scheduler.detect_conflicts([t1, t2])
        self.assertEqual(len(conflicts), 1, "Same start time should be detected as a conflict")

    def test_overlapping_tasks_flagged(self):
        """A task starting mid-way through another should be detected."""
        # Walk: 07:00 AM → 07:30 AM; Feed: 07:15 AM → 07:25 AM — fully inside walk
        t1 = Task(name="Walk", duration=30, priority=2, category="walk",    time_slot="07:00 AM")
        t2 = Task(name="Feed", duration=10, priority=3, category="feeding", time_slot="07:15 AM")

        conflicts = self.scheduler.detect_conflicts([t1, t2])
        self.assertEqual(len(conflicts), 1, "Overlapping tasks should produce one conflict")

    def test_non_overlapping_tasks_have_no_conflict(self):
        """Tasks that end before the next one starts must NOT be flagged."""
        # Walk ends at 07:30 AM; Feed starts at 07:30 AM — touching but not overlapping
        t1 = Task(name="Walk", duration=30, priority=2, category="walk",    time_slot="07:00 AM")
        t2 = Task(name="Feed", duration=10, priority=3, category="feeding", time_slot="07:30 AM")

        conflicts = self.scheduler.detect_conflicts([t1, t2])
        self.assertEqual(len(conflicts), 0, "Back-to-back tasks must not be flagged as conflicting")

    def test_no_conflicts_with_single_task(self):
        """A list with only one task can never produce a conflict."""
        t1 = Task(name="Walk", duration=30, priority=2, category="walk", time_slot="08:00 AM")

        conflicts = self.scheduler.detect_conflicts([t1])
        self.assertEqual(len(conflicts), 0, "Single task should never conflict with itself")

    def test_untimed_tasks_ignored_in_conflict_check(self):
        """Tasks without time_slot should be skipped by detect_conflicts."""
        t1 = Task(name="Walk",  duration=30, priority=2, category="walk")     # no time_slot
        t2 = Task(name="Brush", duration=15, priority=1, category="grooming") # no time_slot

        conflicts = self.scheduler.detect_conflicts([t1, t2])
        self.assertEqual(len(conflicts), 0, "Tasks without time_slot should not produce conflicts")


if __name__ == "__main__":
    unittest.main()
