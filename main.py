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

# Add tasks to Max
max.add_task(Task(name="Morning walk", due_date=datetime(2026, 3, 29, 7, 0)))
max.add_task(Task(name="Vet appointment", due_date=datetime(2026, 3, 29, 11, 0)))

# Add tasks to Luna
luna.add_task(Task(name="Feed Luna", due_date=datetime(2026, 3, 29, 8, 30)))
luna.add_task(Task(name="Flea treatment", due_date=datetime(2026, 3, 29, 14, 0), is_recurring=True))

# Set up scheduler with owner's pets
scheduler = Scheduler(owner.pets)

# Print today's schedule
today = datetime(2026, 3, 29)
todays_tasks = scheduler.get_tasks_by_date(today)

print("=== Today's Schedule ===")
for task in todays_tasks:
    pet_name = next(pet.name for pet in owner.pets if task in pet.tasks)
    print(f"  {task.due_date.strftime('%I:%M %p')} | {pet_name} | {task.name} | Status: {task.status}")