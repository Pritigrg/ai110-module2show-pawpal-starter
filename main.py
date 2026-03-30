from pawpal_system import Pet, Task, RecurringTask, Owner, Scheduler

scheduler = Scheduler()

# --- Pets & Owners ---
buddy    = Pet(name="Buddy",    species="Dog", age=3)
whiskers = Pet(name="Whiskers", species="Cat", age=5)

alex = Owner(name="Alex", available_minutes=180, pet=buddy)

# ── Tasks with NO conflicts (clean baseline) ─────────────────────────────────
alex.add_task(Task(name="Morning walk",    duration=30, priority=3, category="walk",     time_slot="07:00 AM", pet_name="Buddy"))
alex.add_task(Task(name="Give joint meds", duration=5,  priority=3, category="meds",     time_slot="07:45 AM", pet_name="Buddy"))
alex.add_task(Task(name="Feed wet food",   duration=5,  priority=3, category="feeding",  time_slot="08:00 AM", pet_name="Whiskers"))

# ── Same-pet conflict: "Brush fur" starts at 07:15 AM, inside "Morning walk" ─
# Morning walk runs 07:00–07:30, so 07:15 overlaps by 15 minutes.
alex.add_task(Task(name="Brush fur",       duration=20, priority=2, category="grooming", time_slot="07:15 AM", pet_name="Buddy"))

# ── Cross-pet conflict: Whiskers' litter clean overlaps Buddy's meds ─────────
# Give joint meds runs 07:45–07:50; Clean litter starts 07:48 → 2-min overlap.
alex.add_task(Task(name="Clean litter",    duration=10, priority=2, category="grooming", time_slot="07:48 AM", pet_name="Whiskers"))

# ── A clean afternoon block (no collisions expected) ─────────────────────────
alex.add_task(Task(name="Play fetch",      duration=20, priority=1, category="walk",     time_slot="05:00 PM", pet_name="Buddy"))
alex.add_task(Task(name="Laser play",      duration=15, priority=1, category="walk",     time_slot="04:30 PM", pet_name="Whiskers"))

all_tasks = alex.get_tasks()

# ── 1. Show the full task list (out-of-order insertion) ───────────────────────
print("=" * 62)
print("ALL TASKS (insertion order — intentionally out of time order)")
print("=" * 62)
for t in all_tasks:
    print(f"  {t}")

# ── 2. Sort by time slot ──────────────────────────────────────────────────────
print()
print("=" * 62)
print("SORTED BY TIME SLOT (sort_tasks_by_time)")
print("=" * 62)
for t in scheduler.sort_tasks_by_time(all_tasks):
    print(f"  {t}")

# ── 3. Filter: pending tasks only ────────────────────────────────────────────
print()
print("=" * 62)
print("FILTER — pending tasks only (completed=False)")
print("=" * 62)
for t in alex.filter_tasks(completed=False):
    print(f"  {t}")

# ── 4. Filter: Buddy's tasks only ────────────────────────────────────────────
print()
print("=" * 62)
print("FILTER — Buddy's tasks only (pet_name='Buddy')")
print("=" * 62)
for t in alex.filter_tasks(pet_name="Buddy"):
    print(f"  {t}")

# ── 5. Filter: Buddy's pending tasks (combined) ───────────────────────────────
print()
print("=" * 62)
print("FILTER — Buddy's pending tasks (pet_name + completed combined)")
print("=" * 62)
for t in alex.filter_tasks(completed=False, pet_name="Buddy"):
    print(f"  {t}")

# Mark one task done to verify completed=True filter works
all_tasks[0].completed = True

print()
print("=" * 62)
print("FILTER — completed tasks only (after marking first task done)")
print("=" * 62)
for t in alex.filter_tasks(completed=True):
    print(f"  {t}")

# ── 2. Run conflict detection across ALL tasks (same & cross pet) ─────────────
print()
print("=" * 62)
print("CONFLICT CHECK — all tasks pooled")
print("=" * 62)
warnings = scheduler.conflict_warnings(all_tasks)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# ── 3. Isolate: same-pet only (Buddy's tasks) ────────────────────────────────
print()
print("=" * 62)
print("CONFLICT CHECK — Buddy's tasks only (same-pet)")
print("=" * 62)
buddy_tasks = [t for t in all_tasks if t.pet_name == "Buddy"]
for w in scheduler.conflict_warnings(buddy_tasks):
    print(f"  {w}")

# ── 4. Verify the clean afternoon block has zero warnings ─────────────────────
print()
print("=" * 62)
print("CONFLICT CHECK — afternoon block (should be clean)")
print("=" * 62)
afternoon = [t for t in all_tasks if t.time_slot and t.time_slot.endswith("PM")]
warnings_pm = scheduler.conflict_warnings(afternoon)
if warnings_pm:
    for w in warnings_pm:
        print(f"  {w}")
else:
    print("  No conflicts — afternoon schedule is clear.")

# ── 5. Show detect_conflicts raw tuples for reference ─────────────────────────
print()
print("=" * 62)
print("RAW CONFLICT PAIRS (detect_conflicts)")
print("=" * 62)
pairs = scheduler.detect_conflicts(all_tasks)
if pairs:
    for t1, t2 in pairs:
        print(f"  • '{t1.name}'  ↔  '{t2.name}'")
else:
    print("  (none)")

# ── 6. Explicit same-time conflict demo ───────────────────────────────────────
print()
print("=" * 62)
print("CONFLICT DEMO — two tasks at the exact same time")
print("=" * 62)

clash_tasks = [
    Task(name="Morning walk",  duration=30, priority=3, category="walk",    time_slot="09:00 AM", pet_name="Buddy"),
    Task(name="Vet checkup",   duration=45, priority=3, category="vet",     time_slot="09:00 AM", pet_name="Buddy"),
    Task(name="Feed Whiskers", duration=10, priority=2, category="feeding", time_slot="09:00 AM", pet_name="Whiskers"),
]

print("  Tasks added:")
for t in clash_tasks:
    print(f"    {t}")

print()
warnings = scheduler.conflict_warnings(clash_tasks)
if warnings:
    for w in warnings:
        print(f"  {w}")
else:
    print("  No conflicts detected.")

# ── 6. Recurring task auto-creation on complete ───────────────────────────────
print()
print("=" * 62)
print("RECURRING TASK — auto-create next occurrence on complete")
print("=" * 62)

daily_walk   = RecurringTask(name="Daily walk",    duration=30, priority=3, category="walk",    pet_name="Buddy",    frequency="daily")
weekly_bath  = RecurringTask(name="Weekly bath",   duration=20, priority=2, category="grooming", pet_name="Buddy",   frequency="weekly")

alex.add_task(daily_walk)
alex.add_task(weekly_bath)

print(f"  Before — task count: {len(alex.get_tasks())}")
print(f"  Completing: {daily_walk}")
print(f"  Completing: {weekly_bath}")

alex.complete_task(daily_walk)
alex.complete_task(weekly_bath)

recurring = alex.get_recurring_tasks()
print(f"\n  After — recurring tasks ({len(recurring)} total):")
for t in recurring:
    print(f"    {t}")
