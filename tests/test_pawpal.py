import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

import unittest
from pawpal_system import Pet, Task, Owner


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


if __name__ == "__main__":
    unittest.main()
