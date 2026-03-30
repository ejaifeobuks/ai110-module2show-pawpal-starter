from dataclasses import dataclass, field
from datetime import datetime

@dataclass
class Task:
    name: str
    due_date: datetime
    is_recurring: bool = False
    status: str = "pending"

    def update_status(self, new_status: str) -> None:
        pass


@dataclass
class Pet:
    name: str
    type: str
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        pass

    def remove_task(self, task: Task) -> None:
        pass


class Owner:
    def __init__(self, name: str) -> None:
        self.name = name
        self.pets: list[Pet] = []

    def add_pet(self, pet: Pet) -> None:
        pass

    def get_pets(self) -> list[str]:
        pass

    def display_schedule(self, pet: Pet) -> None:
        pass


class Scheduler:
    def __init__(self, pets: list[Pet]) -> None:
        self.pets = pets

    def get_all_tasks(self) -> list[Task]:
        pass

    def get_tasks_by_date(self, date: datetime) -> list[Task]:
        pass

    def get_recurring_tasks(self) -> list[Task]:
        pass
