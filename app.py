import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Initialize session state to persist objects across reruns
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None
if "tasks" not in st.session_state:
    st.session_state.tasks = []

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

st.subheader("Quick Demo Inputs")
owner_name = st.text_input("Owner name", value="Jordan")
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])

# Create Owner and Pet objects and store them in session state
if st.session_state.owner is None or st.session_state.owner.name != owner_name:
    st.session_state.owner = Owner(name=owner_name)
    pet = Pet(name=pet_name, type=species)
    st.session_state.owner.add_pet(pet)
    st.session_state.scheduler = Scheduler(st.session_state.owner.pets)

st.markdown("### Tasks")
st.caption("Add tasks below. Each task is assigned to your pet and fed into the scheduler.")

col1, col2, col3, col4 = st.columns(4)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)
with col4:
    task_time = st.time_input("Due time")

if st.button("Add task"):
    due_date = datetime.combine(datetime.today().date(), task_time)
    new_task = Task(name=task_title, due_date=due_date)
    st.session_state.owner.pets[0].add_task(new_task)
    st.session_state.tasks.append({
        "title": task_title,
        "duration_minutes": int(duration),
        "priority": priority,
        "due_time": task_time.strftime("%I:%M %p"),
    })

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("This button should call your scheduling logic once you implement it.")

if st.button("Generate schedule"):
    all_tasks = st.session_state.scheduler.get_all_tasks_sorted()
    if not all_tasks:
        st.info("No tasks yet. Add some tasks above.")
    else:
        rows = []
        for task in all_tasks:
            pet_name = next(p.name for p in st.session_state.owner.pets if task in p.tasks)
            rows.append({
                "Pet": pet_name,
                "Task": task.name,
                "Due": task.due_date.strftime("%I:%M %p"),
                "Status": task.status,
            })
        st.table(rows)
