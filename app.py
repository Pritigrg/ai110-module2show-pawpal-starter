import streamlit as st
from pawpal_system import Owner, Pet, Task, Appointment, PetLog, Schedule, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "owner" not in st.session_state:
    default_pet = Pet(name=pet_name, species=species, age=2)
    st.session_state.owner = Owner(name=owner_name, available_minutes=60, pet=default_pet)

owner = st.session_state.owner

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority_label = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    category = st.selectbox("Category", ["walk", "feeding", "meds", "grooming"])

PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}

if st.button("Add task"):
    new_task = Task(
        name=task_title,
        duration=int(duration),
        priority=PRIORITY_MAP[priority_label],
        category=category,
    )
    owner.add_task(new_task)
    st.success(f"Added: {new_task}")

current_tasks = owner.get_tasks()
if current_tasks:
    st.write("Current tasks:")
    st.table([
        {
            "Name": t.name,
            "Category": t.category,
            "Duration (min)": t.duration,
            "Priority": t.priority,
            "Done": t.completed,
        }
        for t in current_tasks
    ])
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

available_minutes = st.number_input(
    "Available minutes today", min_value=1, max_value=480, value=owner.available_minutes
)
owner.available_minutes = available_minutes

if st.button("Generate schedule"):
    if not owner.get_tasks():
        st.warning("Add at least one task before generating a schedule.")
    else:
        scheduler = Scheduler()
        schedule = scheduler.generate_schedule(owner)
        st.success("Schedule generated!")
        st.text(schedule.display())
