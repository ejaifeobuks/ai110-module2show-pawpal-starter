import streamlit as st
from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# ---------------------------------------------------------------------------
# Session state bootstrap
# ---------------------------------------------------------------------------
if "owner" not in st.session_state:
    st.session_state.owner = None
if "scheduler" not in st.session_state:
    st.session_state.scheduler = None

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")
st.title("🐾 PawPal+")
st.caption("A smart pet care scheduler — add tasks, detect conflicts, and generate a sorted daily plan.")

st.divider()

# ---------------------------------------------------------------------------
# Sidebar — owner / pet setup
# ---------------------------------------------------------------------------
with st.sidebar:
    st.header("Owner Setup")
    owner_name = st.text_input("Owner name", value="Jordan")

    if st.button("Create / Reset profile", use_container_width=True):
        new_owner = Owner(name=owner_name)
        st.session_state.owner = new_owner
        st.session_state.scheduler = Scheduler(new_owner.pets)
        st.success(f"Profile created for {owner_name}.")

    st.markdown("---")
    st.header("Add a Pet")
    pet_name_input = st.text_input("Pet name", value="Mochi")
    species = st.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])

    if st.button("Add pet", use_container_width=True):
        if st.session_state.owner is None:
            st.error("Create an owner profile first.")
        else:
            existing_names = [p.name for p in st.session_state.owner.pets]
            if pet_name_input in existing_names:
                st.warning(f"{pet_name_input} is already in the roster.")
            else:
                new_pet = Pet(name=pet_name_input, type=species)
                st.session_state.owner.add_pet(new_pet)
                st.success(f"{pet_name_input} added!")

    if st.session_state.owner:
        st.markdown("---")
        st.markdown(f"**Owner:** {st.session_state.owner.name}")
        for p in st.session_state.owner.pets:
            st.markdown(f"**{p.name}** ({p.type}) — {len(p.tasks)} task(s)")

# Guard: require a profile before showing the rest of the app
if st.session_state.owner is None or st.session_state.scheduler is None:
    st.info("Use the sidebar to create an owner and pet profile to get started.")
    st.stop()

owner: Owner = st.session_state.owner
scheduler: Scheduler = st.session_state.scheduler

# ---------------------------------------------------------------------------
# Section 1 — Add a task
# ---------------------------------------------------------------------------
st.subheader("Add a Task")

col1, col2, col3, col4, col5 = st.columns([2, 1, 1, 1, 1])
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    task_time = st.time_input("Due time", key="task_time_input")
with col3:
    frequency = st.selectbox("Frequency", ["none", "daily", "weekly"])
with col4:
    pet_target = st.selectbox("Pet", [p.name for p in owner.pets])
with col5:
    st.write("")  # vertical spacer
    st.write("")
    add_clicked = st.button("Add task", use_container_width=True)

if add_clicked:
    due_date = datetime.combine(datetime.today().date(), task_time)
    is_recurring = frequency != "none"
    new_task = Task(
        name=task_title,
        due_date=due_date,
        is_recurring=is_recurring,
        frequency=frequency if is_recurring else None,
    )
    pet = next(p for p in owner.pets if p.name == pet_target)
    pet.add_task(new_task)
    st.success(f"Task **{task_title}** added for {pet_target} at {task_time.strftime('%I:%M %p')}.")

st.divider()

# ---------------------------------------------------------------------------
# Section 2 — Conflict warnings
# ---------------------------------------------------------------------------
st.subheader("Conflict Check")

conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        st.warning(warning)
else:
    all_tasks = scheduler.get_all_tasks()
    if all_tasks:
        st.success("No scheduling conflicts detected.")
    else:
        st.info("No tasks added yet — nothing to check.")

st.divider()

# ---------------------------------------------------------------------------
# Section 3 — Sorted schedule
# ---------------------------------------------------------------------------
st.subheader("Daily Schedule (sorted by time)")

sorted_tasks = scheduler.sort_by_time()

if not sorted_tasks:
    st.info("No tasks yet. Add some tasks above to see the schedule.")
else:
    rows = []
    for task in sorted_tasks:
        owning_pet = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
        rows.append({
            "Pet": owning_pet,
            "Task": task.name,
            "Due": task.due_date.strftime("%I:%M %p"),
            "Recurring": "Yes" if task.is_recurring else "No",
            "Frequency": task.frequency or "—",
            "Status": task.status,
        })

    st.dataframe(
        rows,
        use_container_width=True,
        column_config={
            "Status": st.column_config.TextColumn(
                "Status",
                help="pending or done",
            ),
            "Recurring": st.column_config.TextColumn("Recurring"),
        },
    )

st.divider()

# ---------------------------------------------------------------------------
# Section 4 — Filter tasks
# ---------------------------------------------------------------------------
st.subheader("Filter Tasks")

fcol1, fcol2 = st.columns(2)
with fcol1:
    filter_status = st.selectbox("Filter by status", ["(all)", "pending", "done"])
with fcol2:
    pet_options = ["(all)"] + [p.name for p in owner.pets]
    filter_pet = st.selectbox("Filter by pet", pet_options)

status_arg = None if filter_status == "(all)" else filter_status
pet_arg = None if filter_pet == "(all)" else filter_pet

filtered = scheduler.filter_tasks(status=status_arg, pet_name=pet_arg)

if not filtered:
    st.info("No tasks match the selected filters.")
else:
    filter_rows = []
    for task in filtered:
        owning_pet = next((p.name for p in owner.pets if task in p.tasks), "Unknown")
        filter_rows.append({
            "Pet": owning_pet,
            "Task": task.name,
            "Due": task.due_date.strftime("%I:%M %p"),
            "Status": task.status,
            "Frequency": task.frequency or "—",
        })
    st.dataframe(filter_rows, use_container_width=True)

st.divider()

# ---------------------------------------------------------------------------
# Section 5 — Mark task complete
# ---------------------------------------------------------------------------
st.subheader("Mark a Task Complete")

all_tasks = scheduler.get_all_tasks()
pending_tasks = [t for t in all_tasks if t.status == "pending"]

if not pending_tasks:
    st.info("No pending tasks to complete.")
else:
    task_labels = {
        f"{t.name} ({t.due_date.strftime('%I:%M %p')})": t for t in pending_tasks
    }
    chosen_label = st.selectbox("Select task to complete", list(task_labels.keys()))
    chosen_task = task_labels[chosen_label]

    if st.button("Mark complete"):
        scheduler.mark_task_complete(chosen_task)
        if chosen_task.frequency:
            st.success(
                f"**{chosen_task.name}** marked done. "
                f"Next occurrence auto-scheduled in 1 {'day' if chosen_task.frequency == 'daily' else 'week'}."
            )
        else:
            st.success(f"**{chosen_task.name}** marked done.")
        st.rerun()