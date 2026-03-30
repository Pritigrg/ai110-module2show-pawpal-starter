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
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
