import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")
st.caption("A smart pet care planner — sorted, conflict-checked, and priority-aware.")

PRIORITY_MAP = {"Low": 1, "Medium": 2, "High": 3}
PRIORITY_LABEL = {1: "Low", 2: "Medium", 3: "High"}
PRIORITY_EMOJI = {1: "🟢", 2: "🟡", 3: "🔴"}

# ---------------------------------------------------------------------------
# Owner / pet setup
# ---------------------------------------------------------------------------
with st.expander("Owner & Pet", expanded=True):
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        owner_name = st.text_input("Owner name", value="Jordan")
    with col2:
        pet_name_input = st.text_input("Pet name", value="Mochi")
    with col3:
        species = st.selectbox("Species", ["Dog", "Cat", "Other"])
    with col4:
        available_minutes = st.number_input("Minutes available today", min_value=1, max_value=480, value=60)

# Rebuild owner when identity fields change
owner_key = f"{owner_name}|{pet_name_input}|{species}"
if st.session_state.get("owner_key") != owner_key:
    pet = Pet(name=pet_name_input, species=species, age=2)
    st.session_state.owner = Owner(name=owner_name, available_minutes=int(available_minutes), pet=pet)
    st.session_state.owner_key = owner_key

owner = st.session_state.owner
owner.available_minutes = int(available_minutes)

st.divider()

# ---------------------------------------------------------------------------
# Add a task
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (min)", min_value=1, max_value=240, value=20)
with col3:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming"])

col4, col5, col6 = st.columns(3)
with col4:
    priority_label = st.selectbox("Priority", ["Low", "Medium", "High"], index=2)
with col5:
    use_time = st.checkbox("Set a specific time?")
with col6:
    if use_time:
        picked_time = st.time_input("Time slot", value=None, label_visibility="visible")
        time_slot = picked_time.strftime("%I:%M %p") if picked_time else ""
    else:
        st.caption("No time slot — task will appear after timed tasks.")
        time_slot = ""

if st.button("Add Task", type="primary"):
    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=PRIORITY_MAP[priority_label],
        category=category,
        time_slot=time_slot,
        pet_name=owner.pet.name,
    )
    owner.add_task(new_task)
    st.success(f"Added **{new_task.name}** ({priority_label} priority, {int(duration)} min)")

st.divider()

# ---------------------------------------------------------------------------
# Task list — sorted by time via Scheduler
# ---------------------------------------------------------------------------
st.subheader("Current Tasks")

current_tasks = owner.get_tasks()

if not current_tasks:
    st.info("No tasks yet. Add one above.")
else:
    scheduler = Scheduler()
    sorted_tasks = scheduler.sort_tasks_by_time(current_tasks)

    st.caption(f"{len(sorted_tasks)} task(s) — sorted chronologically; untimed tasks appear last.")

    st.table([
        {
            "Time": t.time_slot if t.time_slot else "—",
            "Task": t.name,
            "Category": t.category.capitalize(),
            "Duration (min)": t.duration,
            "Priority": f"{PRIORITY_EMOJI[t.priority]} {PRIORITY_LABEL[t.priority]}",
            "Done": "✅" if t.completed else "⬜",
        }
        for t in sorted_tasks
    ])

    # --- Conflict check on the live task list ---
    warnings = scheduler.conflict_warnings(current_tasks)
    if warnings:
        st.markdown("**Scheduling conflicts detected:**")
        for w in warnings:
            st.warning(w)
    else:
        timed_count = sum(1 for t in current_tasks if t.time_slot)
        if timed_count >= 2:
            st.success(f"No conflicts found across {timed_count} timed tasks.")

st.divider()

# ---------------------------------------------------------------------------
# Generate schedule
# ---------------------------------------------------------------------------
st.subheader("Generate Daily Schedule")
st.caption(f"Budget: **{owner.available_minutes} min** — high-priority, shorter tasks are selected first.")

if st.button("Generate Schedule"):
    if not owner.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        ordered = schedule.sort_by_time()

        if not ordered:
            st.warning("No tasks fit within your available time budget.")
        else:
            st.success(
                f"Scheduled **{len(ordered)}** of {len(current_tasks)} task(s) "
                f"— {schedule.total_duration()} of {owner.available_minutes} min used."
            )

            st.table([
                {
                    "Time": t.time_slot if t.time_slot else "—",
                    "Task": t.name,
                    "Category": t.category.capitalize(),
                    "Duration (min)": t.duration,
                    "Priority": f"{PRIORITY_EMOJI[t.priority]} {PRIORITY_LABEL[t.priority]}",
                }
                for t in ordered
            ])

            with st.expander("Reasoning"):
                st.write(schedule.reasoning)

        # Surface any conflicts inside the generated schedule
        conflict_warns = scheduler.conflict_warnings(ordered)
        if conflict_warns:
            st.markdown("**Conflicts within the generated schedule:**")
            for w in conflict_warns:
                st.warning(w)
