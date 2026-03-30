from dataclasses import dataclass, field
from datetime import datetime, timedelta

@dataclass
class Task:
    name: str
    due_date: datetime
    is_recurring: bool = False
    status: str = "pending"
    frequency: str = None  # "daily", "weekly", or None

    def mark_complete(self) -> "Task | None":
        """Mark the task as done. Returns a new Task for the next occurrence if frequency is set."""
        self.status = "done"
        if self.frequency == "daily":
            return Task(name=self.name, due_date=self.due_date + timedelta(days=1),
                        is_recurring=self.is_recurring, frequency=self.frequency)
        if self.frequency == "weekly":
            return Task(name=self.name, due_date=self.due_date + timedelta(weeks=1),
                        is_recurring=self.is_recurring, frequency=self.frequency)
        return None


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
            for task in scheduler.sort_by_time():
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

    def get_recurring_tasks(self) -> list[Task]:
        """Return all tasks marked as recurring across all pets."""
        return [task for task in self.get_all_tasks() if task.is_recurring]

    def sort_by_time(self) -> list[Task]:
        """Return all tasks sorted by time-of-day using HH:MM string format.

        Uses a lambda key that extracts the time component as a string so tasks
        from multiple days are ordered by when they occur during the day rather
        than by their full timestamp. Useful for displaying a recurring daily
        routine across all pets.

        Returns:
            list[Task]: All tasks across every pet sorted ascending by time-of-day.
        """
        return sorted(self.get_all_tasks(), key=lambda task: task.due_date.strftime("%H:%M"))

    def mark_task_complete(self, task: Task) -> None:
        """Mark a task complete and auto-schedule the next occurrence if it has a frequency.

        Delegates status change to Task.mark_complete(), which returns a new Task
        shifted forward by one day (frequency="daily") or one week (frequency="weekly").
        The Scheduler then locates the owning Pet and appends the new Task, keeping
        recurring care routines alive without manual re-entry.

        Args:
            task: The Task to mark as done. Must belong to one of the Scheduler's pets.
        """
        next_task = task.mark_complete()
        if next_task is not None:
            pet = next((p for p in self.pets if task in p.tasks), None)
            if pet is not None:
                pet.add_task(next_task)

    def detect_conflicts(self) -> list[str]:
        """Return warning messages for any tasks scheduled at the same date and time.

        Groups every task across all pets by its exact "YYYY-MM-DD HH:MM" slot.
        Any slot containing more than one task is flagged with a human-readable
        warning string. The method never raises an exception — callers receive an
        empty list when the schedule is conflict-free, so the program can continue
        running regardless.

        Returns:
            list[str]: One warning string per conflicting time slot, empty if none.
        """
        seen: dict[str, list[tuple[str, Task]]] = {}
        for pet in self.pets:
            for task in pet.tasks:
                key = task.due_date.strftime("%Y-%m-%d %H:%M")
                seen.setdefault(key, []).append((pet.name, task))

        warnings = []
        for time_slot, entries in seen.items():
            if len(entries) > 1:
                details = ", ".join(f"{pet_name}: '{task.name}'" for pet_name, task in entries)
                warnings.append(f"WARNING: Conflict at {time_slot} — {details}")
        return warnings

    def filter_tasks(self, status: str = None, pet_name: str = None) -> list[Task]:
        """Filter tasks by completion status and/or pet name.

        Both parameters are optional and can be combined. When both are provided
        the result is the intersection — tasks that match the status AND belong to
        the named pet. When neither is provided all tasks are returned unchanged.

        Args:
            status:   Target status string to match (e.g. "pending" or "done").
                      Pass None to skip status filtering.
            pet_name: Exact name of the pet whose tasks should be returned.
                      Pass None to include tasks from all pets.

        Returns:
            list[Task]: Tasks that satisfy all provided filter criteria.
        """
        tasks = self.get_all_tasks()
        if status is not None:
            tasks = [task for task in tasks if task.status == status]
        if pet_name is not None:
            pet_tasks = [task for pet in self.pets if pet.name == pet_name for task in pet.tasks]
            tasks = [task for task in tasks if task in pet_tasks]
        return tasks
