import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import pytest
from datetime import datetime, timedelta
from pawpal_system import Task, Pet, Scheduler


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def make_task(name, hour, minute=0, day=29, month=3, year=2026,
              is_recurring=False, frequency=None, status="pending"):
    return Task(
        name=name,
        due_date=datetime(year, month, day, hour, minute),
        is_recurring=is_recurring,
        frequency=frequency,
        status=status,
    )


def make_pet(name="Max", type="dog", tasks=None):
    pet = Pet(name=name, type=type)
    for t in (tasks or []):
        pet.add_task(t)
    return pet


# ---------------------------------------------------------------------------
# T-00 / T-01  (existing — kept for completeness)
# ---------------------------------------------------------------------------

def test_mark_complete_changes_status():
    task = make_task("Feed Max", hour=8)
    assert task.status == "pending"
    task.mark_complete()
    assert task.status == "done"


def test_add_task_increases_pet_task_count():
    pet = make_pet()
    assert len(pet.tasks) == 0
    pet.add_task(make_task("Morning walk", hour=7))
    assert len(pet.tasks) == 1


# ---------------------------------------------------------------------------
# Task — Recurrence Logic  (T-02 – T-09)
# ---------------------------------------------------------------------------

def test_daily_task_mark_complete_returns_new_task():
    """T-02: completing a daily task returns a non-None next task."""
    task = make_task("Feed", hour=8, is_recurring=True, frequency="daily")
    next_task = task.mark_complete()
    assert next_task is not None


def test_daily_task_next_occurrence_is_plus_one_day():
    """T-03: next task is exactly 1 day later at the same time."""
    task = make_task("Feed", hour=8, is_recurring=True, frequency="daily")
    next_task = task.mark_complete()
    assert next_task.due_date == task.due_date + timedelta(days=1)


def test_weekly_task_next_occurrence_is_plus_seven_days():
    """T-04: next task is exactly 7 days later at the same time."""
    task = make_task("Bath", hour=10, is_recurring=True, frequency="weekly")
    next_task = task.mark_complete()
    assert next_task.due_date == task.due_date + timedelta(weeks=1)


def test_recurring_next_task_inherits_metadata():
    """T-05: returned task keeps the same name, is_recurring, and frequency."""
    task = make_task("Walk", hour=7, is_recurring=True, frequency="daily")
    next_task = task.mark_complete()
    assert next_task.name == task.name
    assert next_task.is_recurring == task.is_recurring
    assert next_task.frequency == task.frequency


def test_one_time_task_mark_complete_returns_none():
    """T-06: non-recurring task returns None — no next occurrence created."""
    task = make_task("Vet visit", hour=9)
    assert task.mark_complete() is None


def test_recurring_flag_true_but_no_frequency_returns_none():
    """T-07: is_recurring=True with frequency=None still returns None."""
    task = make_task("Mystery task", hour=9, is_recurring=True, frequency=None)
    assert task.mark_complete() is None


def test_daily_recurrence_crosses_month_boundary():
    """T-08: daily task on Jan 31 schedules next on Feb 1."""
    task = Task(name="Feed", due_date=datetime(2026, 1, 31, 8, 0),
                is_recurring=True, frequency="daily")
    next_task = task.mark_complete()
    assert next_task.due_date.month == 2
    assert next_task.due_date.day == 1


def test_weekly_recurrence_crosses_year_boundary():
    """T-09: weekly task on Dec 28 schedules next in the following year."""
    task = Task(name="Groom", due_date=datetime(2025, 12, 28, 10, 0),
                is_recurring=True, frequency="weekly")
    next_task = task.mark_complete()
    assert next_task.due_date.year == 2026


# ---------------------------------------------------------------------------
# Pet (T-10 – T-12)
# ---------------------------------------------------------------------------

def test_remove_task_decreases_count():
    """T-10: remove_task drops the pet's task count by 1."""
    task = make_task("Walk", hour=7)
    pet = make_pet(tasks=[task])
    pet.remove_task(task)
    assert len(pet.tasks) == 0


def test_remove_task_not_found_raises_value_error():
    """T-11: removing a task that was never added raises ValueError."""
    pet = make_pet()
    task = make_task("Ghost task", hour=9)
    with pytest.raises(ValueError):
        pet.remove_task(task)


def test_pet_starts_with_no_tasks():
    """T-12: a freshly created Pet has an empty task list."""
    pet = Pet(name="Bella", type="cat")
    assert pet.tasks == []


# ---------------------------------------------------------------------------
# Scheduler — Happy Paths (T-13 – T-22)
# ---------------------------------------------------------------------------

def test_get_all_tasks_combines_multiple_pets():
    """T-13: tasks from two pets are all returned."""
    pet1 = make_pet("Max", tasks=[make_task("Walk", 7), make_task("Feed", 8)])
    pet2 = make_pet("Bella", type="cat", tasks=[make_task("Play", 9)])
    scheduler = Scheduler([pet1, pet2])
    assert len(scheduler.get_all_tasks()) == 3


def test_get_tasks_by_date_returns_correct_day_sorted():
    """T-14: only tasks on the target date are returned, in time order."""
    target = datetime(2026, 3, 29)
    t1 = Task("Walk", datetime(2026, 3, 29, 8, 0))
    t2 = Task("Feed", datetime(2026, 3, 29, 7, 0))
    t_other = Task("Bath", datetime(2026, 3, 30, 9, 0))
    pet = make_pet(tasks=[t1, t2, t_other])
    scheduler = Scheduler([pet])

    result = scheduler.get_tasks_by_date(target)

    assert len(result) == 2
    assert result[0].due_date < result[1].due_date   # sorted ascending


def test_get_recurring_tasks_excludes_one_time_tasks():
    """T-15: only is_recurring=True tasks appear in result."""
    recurring = make_task("Feed", 8, is_recurring=True, frequency="daily")
    one_time = make_task("Vet", 10)
    pet = make_pet(tasks=[recurring, one_time])
    scheduler = Scheduler([pet])

    result = scheduler.get_recurring_tasks()

    assert recurring in result
    assert one_time not in result


def test_sort_by_time_returns_earliest_first():
    """T-16: sort_by_time orders tasks by time-of-day, earliest first."""
    early = make_task("Walk", hour=6)
    mid = make_task("Feed", hour=8)
    late = make_task("Play", hour=20)
    pet = make_pet(tasks=[late, early, mid])
    scheduler = Scheduler([pet])

    result = scheduler.sort_by_time()

    assert result[0].name == "Walk"
    assert result[1].name == "Feed"
    assert result[2].name == "Play"


def test_mark_task_complete_appends_next_task_to_pet():
    """T-17: completing a recurring task grows the pet's task list by 1."""
    task = make_task("Feed", hour=8, is_recurring=True, frequency="daily")
    pet = make_pet(tasks=[task])
    scheduler = Scheduler([pet])

    scheduler.mark_task_complete(task)

    assert len(pet.tasks) == 2


def test_detect_conflicts_no_conflicts_returns_empty():
    """T-18: a schedule with no overlapping times returns []."""
    pet = make_pet(tasks=[make_task("Walk", 7), make_task("Feed", 8)])
    scheduler = Scheduler([pet])
    assert scheduler.detect_conflicts() == []


def test_detect_conflicts_flags_same_datetime():
    """T-19: two tasks at the exact same datetime produce one warning."""
    t1 = Task("Walk", datetime(2026, 3, 29, 8, 0))
    t2 = Task("Feed", datetime(2026, 3, 29, 8, 0))
    pet = make_pet(tasks=[t1, t2])
    scheduler = Scheduler([pet])

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "WARNING" in warnings[0]


def test_filter_tasks_by_status_pending():
    """T-20: filter_tasks('pending') excludes done tasks."""
    pending = make_task("Walk", 7, status="pending")
    done = make_task("Feed", 8, status="done")
    pet = make_pet(tasks=[pending, done])
    scheduler = Scheduler([pet])

    result = scheduler.filter_tasks(status="pending")

    assert pending in result
    assert done not in result


def test_filter_tasks_by_pet_name():
    """T-21: filter_tasks(pet_name=...) returns only that pet's tasks."""
    max_task = make_task("Walk", 7)
    bella_task = make_task("Play", 9)
    pet_max = make_pet("Max", tasks=[max_task])
    pet_bella = make_pet("Bella", type="cat", tasks=[bella_task])
    scheduler = Scheduler([pet_max, pet_bella])

    result = scheduler.filter_tasks(pet_name="Max")

    assert max_task in result
    assert bella_task not in result


def test_filter_tasks_combined_status_and_pet_name():
    """T-22: both filters are AND-ed — only matching pet AND status."""
    done_max = make_task("Walk", 7, status="done")
    pending_max = make_task("Feed", 8, status="pending")
    done_bella = make_task("Play", 9, status="done")
    pet_max = make_pet("Max", tasks=[done_max, pending_max])
    pet_bella = make_pet("Bella", type="cat", tasks=[done_bella])
    scheduler = Scheduler([pet_max, pet_bella])

    result = scheduler.filter_tasks(status="done", pet_name="Max")

    assert done_max in result
    assert pending_max not in result
    assert done_bella not in result


# ---------------------------------------------------------------------------
# Scheduler — Edge Cases (T-23 – T-31)
# ---------------------------------------------------------------------------

def test_scheduler_no_pets_all_methods_return_empty():
    """T-23: Scheduler([]) — every read method returns []."""
    scheduler = Scheduler([])
    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []
    assert scheduler.detect_conflicts() == []
    assert scheduler.get_recurring_tasks() == []


def test_scheduler_pet_with_no_tasks_returns_empty():
    """T-24: a pet with no tasks contributes nothing to results."""
    pet = make_pet()   # no tasks
    scheduler = Scheduler([pet])
    assert scheduler.get_all_tasks() == []
    assert scheduler.sort_by_time() == []


def test_get_tasks_by_date_no_match_returns_empty():
    """T-25: date with no tasks returns []."""
    pet = make_pet(tasks=[make_task("Walk", 7, day=29)])
    scheduler = Scheduler([pet])
    result = scheduler.get_tasks_by_date(datetime(2026, 4, 1))
    assert result == []


def test_sort_by_time_same_time_different_dates_does_not_crash():
    """T-26: tasks on different dates at the same time both appear without error."""
    t1 = Task("Walk", datetime(2026, 3, 29, 8, 0))
    t2 = Task("Feed", datetime(2026, 3, 30, 8, 0))
    pet = make_pet(tasks=[t1, t2])
    scheduler = Scheduler([pet])

    result = scheduler.sort_by_time()

    assert len(result) == 2


def test_detect_conflicts_three_tasks_same_slot():
    """T-27: three tasks at the same time produce exactly one warning listing all three."""
    dt = datetime(2026, 3, 29, 8, 0)
    t1 = Task("Walk", dt)
    t2 = Task("Feed", dt)
    t3 = Task("Bath", dt)
    pet = make_pet(tasks=[t1, t2, t3])
    scheduler = Scheduler([pet])

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "Walk" in warnings[0]
    assert "Feed" in warnings[0]
    assert "Bath" in warnings[0]


def test_detect_conflicts_same_pet_two_tasks_same_time():
    """T-28: conflict within a single pet's tasks is still reported."""
    dt = datetime(2026, 3, 29, 8, 0)
    pet = make_pet(tasks=[Task("Walk", dt), Task("Feed", dt)])
    scheduler = Scheduler([pet])

    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1


def test_filter_tasks_unknown_pet_name_returns_empty():
    """T-29: pet name not in scheduler returns [] without raising."""
    pet = make_pet(tasks=[make_task("Walk", 7)])
    scheduler = Scheduler([pet])
    assert scheduler.filter_tasks(pet_name="Ghost") == []


def test_filter_tasks_no_args_returns_all():
    """T-30: filter_tasks() with no arguments behaves like get_all_tasks()."""
    pet = make_pet(tasks=[make_task("Walk", 7), make_task("Feed", 8)])
    scheduler = Scheduler([pet])
    assert scheduler.filter_tasks() == scheduler.get_all_tasks()


def test_mark_task_complete_non_recurring_does_not_grow_task_list():
    """T-31: completing a one-time task does not append anything to the pet."""
    task = make_task("Vet visit", hour=9)
    pet = make_pet(tasks=[task])
    scheduler = Scheduler([pet])

    scheduler.mark_task_complete(task)

    assert len(pet.tasks) == 1
