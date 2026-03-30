import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from datetime import datetime
from pawpal_system import Task, Pet


def test_mark_complete_changes_status():
    task = Task(name="Feed Max", due_date=datetime(2026, 3, 29, 8, 0))
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "done"


def test_add_task_increases_pet_task_count():
    pet = Pet(name="Max", type="dog")
    assert len(pet.tasks) == 0
    pet.add_task(Task(name="Morning walk", due_date=datetime(2026, 3, 29, 7, 0)))
    assert len(pet.tasks) == 1