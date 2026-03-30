from datetime import datetime
from pawpal_system import Owner, Pet, Task, Scheduler

# Create owner
owner = Owner(name="Alex")

# Create pets
max = Pet(name="Max", type="dog")
luna = Pet(name="Luna", type="cat")

# Add pets to owner
owner.add_pet(max)
owner.add_pet(luna)

# Add tasks OUT OF ORDER to demonstrate sorting
max.add_task(Task(name="Vet appointment", due_date=datetime(2026, 3, 29, 11, 0)))
luna.add_task(Task(name="Flea treatment", due_date=datetime(2026, 3, 29, 14, 0), is_recurring=True, frequency="weekly"))
luna.add_task(Task(name="Feed Luna", due_date=datetime(2026, 3, 29, 8, 30), frequency="daily"))
max.add_task(Task(name="Morning walk", due_date=datetime(2026, 3, 29, 7, 0)))

# Intentional conflict: two tasks at the same time
max.add_task(Task(name="Bath time", due_date=datetime(2026, 3, 29, 11, 0)))  # same time as Vet appointment
luna.add_task(Task(name="Brush fur", due_date=datetime(2026, 3, 29, 14, 0)))  # same time as Flea treatment

# Set up scheduler
scheduler = Scheduler(owner.pets)

# --- Conflict detection ---
print("=== Conflict Detection ===")
conflicts = scheduler.detect_conflicts()
if conflicts:
    for warning in conflicts:
        print(f"  {warning}")
else:
    print("  No conflicts found.")

# --- Sort by time ---
print("\n=== All Tasks Sorted by Time ===")
for task in scheduler.sort_by_time():
    pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
    print(f"  {task.due_date.strftime('%H:%M')} | {pet_name} | {task.name} | Status: {task.status}")

# --- Complete a daily and a weekly task ---
feed_task = luna.tasks[0]   # Feed Luna (daily)
flea_task = luna.tasks[1]   # Flea treatment (weekly)

scheduler.mark_task_complete(feed_task)
scheduler.mark_task_complete(flea_task)

print("\n=== After Completing 'Feed Luna' (daily) and 'Flea treatment' (weekly) ===")
for task in scheduler.sort_by_time():
    pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
    print(f"  {task.due_date.strftime('%Y-%m-%d %H:%M')} | {pet_name} | {task.name} | Status: {task.status}")

# --- Filter by status ---
print("\n=== Pending Tasks ===")
for task in scheduler.filter_tasks(status="pending"):
    pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
    print(f"  {task.due_date.strftime('%Y-%m-%d %H:%M')} | {pet_name} | {task.name}")

print("\n=== Done Tasks ===")
for task in scheduler.filter_tasks(status="done"):
    pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
    print(f"  {task.due_date.strftime('%Y-%m-%d %H:%M')} | {pet_name} | {task.name}")
