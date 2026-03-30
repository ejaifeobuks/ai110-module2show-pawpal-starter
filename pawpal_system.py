from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    name: str
    due_date: datetime
    is_recurring: bool = False
    status: str = "pending"

    def mark_complete(self) -> None:
        """Mark the task as done."""
        self.status = "done"


@dataclass
class Pet:
    name: str
    type: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to the pet's task list."""
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the pet's task list, raising an error if not found."""
        if task not in self.tasks:
            raise ValueError(f"Task '{task.name}' not found for pet '{self.name}'")
        self.tasks.remove(task)


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's pet list."""
        self.pets.append(pet)

    def get_pets(self) -> list[str]:
        """Return a list of names of all pets owned."""
        return [pet.name for pet in self.pets]

    def display_schedule(self, pet: Pet = None, scheduler: "Scheduler" = None) -> None:
        """Print tasks for a specific pet, or all pets sorted by due date if no pet is given."""
        if pet is None:
            print(f"Full schedule for {self.name}:")
            for task in scheduler.get_all_tasks_sorted():
                pet_name = next(p.name for p in self.pets if task in p.tasks)
                print(f"  {task.due_date} | {pet_name} | {task.name} | Status: {task.status}")
        else:
            print(f"Schedule for {pet.name}:")
            if not pet.tasks:
                print("  No tasks scheduled.")
                return
            for task in pet.tasks:
                print(f"  - {task.name} | Due: {task.due_date} | Status: {task.status}")


class Scheduler:
    def __init__(self, pets: list[Pet]) -> None:
        self.pets = pets

    def get_all_tasks(self) -> list[Task]:
        """Return all tasks across every pet."""
        all_tasks = []
        for pet in self.pets:
            all_tasks.extend(pet.tasks)
        return all_tasks

    def get_tasks_by_date(self, date: datetime) -> list[Task]:
        """Return all tasks for a given date, sorted by due time."""
        matching = [task for task in self.get_all_tasks() if task.due_date.date() == date.date()]
        return sorted(matching, key=lambda task: task.due_date)

    def get_all_tasks_sorted(self) -> list[Task]:
        """Return all tasks across all pets sorted by due date."""
        return sorted(self.get_all_tasks(), key=lambda task: task.due_date)

    def get_recurring_tasks(self) -> list[Task]:
        """Return all tasks marked as recurring across all pets."""
        return [task for task in self.get_all_tasks() if task.is_recurring]
