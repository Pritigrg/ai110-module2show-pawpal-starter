# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML design:

Owner
Stores the pet owner's profile — name and total time available per day. Responsible for holding pet and task references.

Pet
Stores pet-specific info — name, species, age, and any health notes. Owned by Owner (composition).

Task
Represents a single care task with attributes: name, duration (minutes), priority (1–3), and frequency (daily/weekly). Responsible for describing what needs to be done and how long it takes.

Scheduler
The core logic class. Takes an Owner (with their tasks) and a time budget, and produces a Schedule. Responsible for sorting tasks by priority, fitting them within available time, and generating an explanation.

Schedule
Holds the ordered list of tasks selected for the day and the reasoning string. Responsible for displaying the final plan.
- What classes did you include, and what responsibilities did you assign to each?

Owner

Stores: name, daily time available (minutes)
Responsible for: holding the pet and the list of tasks
Has: one Pet, many Tasks
Pet

Stores: name, species, age, health notes
Responsible for: representing who the care is for
Note: passive data class — no logic needed here
Task

Stores: name, duration, priority, category (walk/feed/meds/etc.)
Responsible for: describing a single care item
Note: knows nothing about scheduling — just describes itself
Scheduler

Stores: nothing permanently (stateless logic)
Responsible for: taking tasks + time budget → producing a ranked, time-fitted plan
Key method: generate_schedule(owner) → Schedule
Schedule

Stores: ordered list of selected tasks, reasoning text
Responsible for: representing the final output — what to display to the user


**b. Design changes**

- Did your design change during implementation?
 Yes
- If yes, describe at least one change and why you made it.
 1) added Vet Appointments and pet logs [This was my own logic - I felt this component was important to have]
 2) AI help me add logic issues - 
  Added complete_task() to Owner - Original design: Owner only managed adding/removing tasks.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
->Time,Priority, Duration,Time slot
- How did you decide which constraints mattered most?
-> Scheduler should work in FIFO manner thats why we consider the time budget constraint the most. Hence first task should be process before the second task

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
->Greedy selection over optimal selection. for example, two 20-minute medium-priority tasks that together fit the budget might be skipped because a 35-minute high-priority task was taken first, leaving only 25 minutes.
- Why is that tradeoff reasonable for this scenario?
-> Because of its simplicity.
-> Pet care is priority-driven by nature.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
Used AI for refactoring, debugging and analyzing different algorithms for the project 
- What kinds of prompts or questions were most helpful?
-> Add the test cases 
-> Refactor the code or the algorithm (performance and readibility analysis)
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
-> designing the UML diagram-> it gave a basic one like adding scheduling but for the current project like a smart pet care management system it needs more than that. so I had to revise it by adding vet appointments and pet logs.
- How did you evaluate or verify what the AI suggested?
-> By reviewing the suggestion myself and I also took reference from one of the pet smart management tool.
---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
-> I tested six core behaviors across 14 unit tests:
  1. **Task completion** — verifying `completed` flips from `False` to `True` after `complete_task()`.
  2. **Task addition** — verifying `owner.get_tasks()` count increases correctly.
  3. **Chronological sorting** — verifying AM/PM tasks come out in the right order, untimed tasks land last, and an all-untimed list still returns all tasks.
  4. **Recurring task recurrence** — verifying daily (+1 day), weekly (+7 days), and weekday (Friday → Monday, skipping the weekend) `due_date` arithmetic, and that the original task is marked completed.
  5. **Conflict detection** — verifying same-start-time conflicts are flagged, partial overlaps are caught, back-to-back (touching) tasks are *not* flagged, a single task never self-conflicts, and untimed tasks are silently skipped.
 6. **UI testing** - delete/edit the task added - it fails - no UI to do it.
- Why were these tests important?
-> These behaviors are the core of the scheduler's correctness. Sorting ensures the UI always shows tasks in a meaningful order. Recurrence logic is the trickiest date arithmetic in the project — getting Friday→Monday wrong silently produces a Saturday task, which would never appear on a weekday schedule. Conflict detection protects against double-booking, which is the most user-visible failure mode. Without tests for these three, a bug could ship unnoticed.

**b. Confidence**

- How confident are you that your scheduler works correctly?
-> **3.5 out of 5.** All 14 tests pass and they cover the three most critical algorithms (sorting, recurrence, conflict detection) including meaningful edge cases like the weekend skip and the back-to-back boundary. I'm less confident about the Streamlit UI layer , malformed input (e.g. a bad date string in `due_date` raises an unhandled `ValueError`)-> had to fix this,edit the already added task not possible and the greedy scheduler under tight budgets where a long high-priority task can crowd out multiple shorter ones.

- What edge cases would you test next if you had more time?
-> 
   1. **Zero-minute budget** — call `generate_schedule()` with `available_minutes=0` and verify an empty schedule is returned.
   2. **`complete_task()` called twice on the same `RecurringTask`** — currently adds two next-occurrences; decide if that's intentional and test accordingly.
   3. **`filter_tasks()` with all three filters combined** — verify AND-chaining works when category + completed + pet_name are all specified at once.
   4. **`conflict_warnings()` output content** — assert the warning string contains the correct pet name, overlap duration, and scope label (`SAME-PET` vs `CROSS-PET`).
   5. **UI functionality**- editing or delete the added task, the adding box should be empty after adding one task rather need to overwrite.
---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
->UML design and converting it to an MVP code.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
-> The UI. The focus was more on logic rather than the UI, so I would add edit/delete task functionality, clear the input form after adding a task, and surface the PetLog completion rate on the dashboard. VetAppointment and PetLog exist in the backend but are invisible in app.py — a future iteration would expose them.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
->The first UML the AI generated was technically correct but too generic — it didn't account for recurring tasks, vet appointments, or cross-pet conflict detection. I had to push back with specifics about what a pet care system actually needs. The pattern that worked: use AI to draft, then revise based on your own understanding of the problem.