# PawPal+ Project Reflection

## 1. System Design

- The user at this time should be able to:
- Add pets
- Add tasks for pets
- See schedule for pets
- Schedule tasks

  **a. Initial design**

- Briefly describe your initial UML design.
  The initial UML design consists of four classes: `Owner`, `Pet`, `Task`, and `Scheduler`. `Owner` has a one-to-many relationship with `Pet` — one owner can have multiple pets. `Pet` similarly has a one-to-many relationship with `Task` — each pet can have multiple tasks. `Scheduler` depends on `Owner`'s pet list to aggregate and manage tasks across all pets, allowing it to sort tasks by due date and handle recurring tasks.
- What classes did you include, and what responsibilities did you assign to each?
  The four classes are `Owner`, `Pet`, `Task`, and `Scheduler`.
  - The `Owner` class holds a `name` attribute and a list of `Pet` objects, with methods to add a pet, retrieve the names of all pets, and display the schedule for a specific pet.
  - The `Pet` class stores the pet's `name`, `type`, and a list of `Task` objects, and has methods to add and remove tasks from that list.
  - The `Task` class holds the task's `name`, `due_date`, an `is_recurring` flag, and a `status`, with a single `update_status` method that takes a new status string and updates the task accordingly.
  - The `Scheduler` class receives the owner's list of pets as its attribute, giving it access to all tasks across all pets. Its methods allow it to retrieve all tasks sorted by due date, filter for recurring tasks, and aggregate tasks across pets.
    **b. Design changes**

- Did your design change during implementation?
  Yes, the design changed in a few ways during implementation.
  - The `Task` class originally had an `update_status` method that accepted any status string and validated it against a fixed set. This was replaced with a simpler `mark_complete` method that directly sets the status to `"done"`, since that was the only transition that mattered in practice.
  - The `display_schedule` method in `Owner` was initially designed to only show tasks for a single pet. During implementation, it was extended to accept an optional `pet` parameter and an optional `scheduler` parameter. If no pet is passed, it delegates to `scheduler.get_all_tasks_sorted()` to print all tasks across all pets in order of due date. This change avoided duplicating sorting logic that already belonged to `Scheduler`.
  - A `get_all_tasks_sorted` method was added to `Scheduler` to support the updated `display_schedule` behavior, keeping task aggregation and sorting logic centralized in one place.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
  The scheduler considers time as its primary constraint — every task has a `due_date` with a specific time, and `sort_by_time()` orders tasks by that time regardless of date. It also considers recurrence frequency (`daily` or `weekly`) as a scheduling constraint, automatically advancing a task's due date when it is completed. Conflict detection treats simultaneous scheduling as a constraint violation and flags it for the owner to resolve.

- How did you decide which constraints mattered most?
  Time came first because a pet care routine is fundamentally time-driven — feeding at 8 AM and walking at 7 PM are non-negotiable windows. Recurrence was prioritized next because missing a recurring task entirely (by requiring manual re-entry) would undermine the whole point of a care scheduler. Priority ranking was deprioritized in this iteration because the scenario involved a single owner managing a small number of pets where explicit priority scores would add complexity without much practical benefit.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
  `sort_by_time()` sorts by time-of-day only (the `"HH:MM"` component of `due_date`), ignoring the calendar date. This means a task due tomorrow at 7 AM appears before a task due today at 9 AM in the sorted view.

- Why is that tradeoff reasonable for this scenario?
  The goal of the sorted schedule is to show the owner what their daily routine looks like — when things happen during the day — rather than a strict chronological event list across multiple days. Since most recurring pet care tasks repeat on a fixed daily clock, sorting by time-of-day gives a more readable and actionable daily plan. A full datetime sort is still available via `get_tasks_by_date()` when the user needs it for a specific day.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
  AI was used across the full project lifecycle. During design, it helped evaluate the initial UML and flag structural issues — for example, pointing out that `Scheduler` should hold a list of `Pet` objects rather than an `Owner` reference, since it never needed owner-level data. During implementation, it helped draft docstrings, explain tradeoffs in algorithm choices (e.g., why a `dict` grouping is clearer than nested loops for conflict detection), and suggest edge cases to cover in tests. In the final phase, it helped reconcile the UML diagram with what was actually built.

- What kinds of prompts or questions were most helpful?
  The most useful prompts were specific and comparative: "given my final implementation, what updates should I make to my initial UML?" and "what tradeoff does sorting by time-of-day create?" Open-ended prompts like "improve my scheduler" were less useful because they produced suggestions beyond the scope of the project. Asking the AI to explain *why* a design decision made sense — not just *what* to do — consistently produced better output.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
  When the AI described the `display_schedule` changes in the reflection draft, it referenced a `get_all_tasks_sorted()` method. That method does not exist in the final implementation — the actual method used is `sort_by_time()`. The AI had carried over terminology from an earlier design draft that was never merged into the final code.

- How did you evaluate or verify what the AI suggested?
  The suggestion was verified by reading `pawpal_system.py` directly and checking that `sort_by_time` — not `get_all_tasks_sorted` — is the method called inside `display_schedule`. Any AI claim about a specific method or file path was cross-checked against the actual source before accepting it.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
  The test suite covers four areas: recurrence logic (daily and weekly task advancement, one-time task completion returning `None`), sorting correctness (`sort_by_time` ordering by time-of-day across multiple dates, `get_tasks_by_date` returning only the matching date), conflict detection (no conflicts, two-task collision, three-task collision), and edge cases (empty scheduler, pet with no tasks, unknown pet name in filter, month/year boundary crossing during recurrence, combined status+pet filtering using AND logic).

- Why were these tests important?
  These behaviors are the core value of the scheduler — if recurrence breaks, recurring care stops; if conflict detection misses a slot, the owner gets no warning; if sorting is wrong, the daily plan is misleading. Testing them directly gave confidence that the logic holds beyond the happy path shown in the UI.

**b. Confidence**

- How confident are you that your scheduler works correctly?
  ★★★★☆ (4/5). The core scheduling behaviors are all verified and passing across 32 tests. Confidence is high for the Python logic layer.

- What edge cases would you test next if you had more time?
  The Streamlit UI layer (`app.py`) is entirely untested — interactions like adding a duplicate pet, submitting a task with no pet selected, or marking a task complete and verifying the rerun behavior are all exercised manually but not in the test suite. The `Owner.display_schedule()` console output path is also uncovered. These would be the next targets.

---

## 5. AI Strategy — VS Code Copilot Experience

**a. Most effective Copilot features**

The two features that contributed most were **inline completions** and **chat with context**.

Inline completions were most valuable during repetitive but error-prone work — writing the `filter_tasks` method, for example. Once the method signature and docstring were in place, Copilot correctly inferred the filtering pattern from the existing `get_all_tasks()` call above it and suggested the list comprehension structure without prompting. This saved time on boilerplate while keeping the logic readable.

Chat with context was most useful for algorithm decisions. Asking "what is the cleanest way to group tasks by time slot for conflict detection?" inside the editor — with `pawpal_system.py` open — produced a focused suggestion using a `dict` with `setdefault`, which matched the existing code style better than a `defaultdict` import would have. Having the file open meant the suggestion fit the project rather than being generic Python.

**b. One suggestion rejected or modified**

When drafting the `sort_by_time` method, Copilot suggested sorting by the full `due_date` datetime object directly:

```python
return sorted(self.get_all_tasks(), key=lambda task: task.due_date)
```

This was rejected. Sorting by full datetime means a task due tomorrow at 7 AM would appear before a task due today at 9 PM — the output would reflect chronological event order across multiple days rather than the daily routine pattern the method is meant to show. The final version sorts by `task.due_date.strftime("%H:%M")` to isolate time-of-day. The suggestion was technically correct Python but architecturally wrong for the use case. Accepting it would have made `sort_by_time` and `get_tasks_by_date` redundant and confused their distinct purposes.

**c. How separate chat sessions helped**

Using a new chat session for each project phase — UML design, implementation, testing, reflection — prevented earlier context from bleeding into later decisions. During the testing phase, for instance, starting fresh meant the AI focused on what the code *actually did* rather than on what the design phase had *intended* it to do. This mattered when the `get_all_tasks_sorted` vs. `sort_by_time` discrepancy came up: a session that had been open since the design phase might have reinforced the stale name rather than flagging it. Separate sessions forced each phase to be grounded in the current state of the codebase.

**d. Being the "lead architect"**

The central lesson was that AI is a fast, fluent collaborator that has no stake in the design — it will suggest whatever fits the immediate prompt, not whatever fits the long-term system. That makes the human's role explicitly architectural: deciding what belongs in `Task` versus `Scheduler`, keeping method responsibilities from overlapping, and pushing back when a suggestion is technically correct but violates a design boundary.

In practice this meant treating every AI suggestion as a pull request from a junior developer: read it, evaluate whether it fits the system's existing patterns and responsibilities, and either merge it, modify it, or close it with a reason. The AI produced better output when given architectural constraints upfront ("the `Scheduler` should not know about `Owner`, only `Pet`") than when given open-ended prompts. The lead architect's job is to set those constraints and hold them consistently across every session.

---

## 6. Reflection

**a. What went well**

- What part of this project are you most satisfied with?
  The recurrence system. The design of having `Task.mark_complete()` return the next task as a new object — rather than mutating state in place — made the logic clean, testable, and easy to reason about. The `Scheduler` could then stay simple: call `mark_complete()`, get back a task or `None`, and append it to the right pet. The boundary between what `Task` owns and what `Scheduler` coordinates stayed clear throughout.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?
  The conflict detection currently flags any two tasks scheduled at the exact same `"YYYY-MM-DD HH:MM"` slot. A more useful version would flag tasks within a configurable window (e.g., within 15 minutes of each other) so the owner can account for travel or transition time between pets. I would also add task duration as a `Task` attribute, which would make both conflict detection and schedule display significantly more realistic.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
  The UML diagram is most useful as a living document, not a contract. The design that looked complete on paper had several gaps that only became visible during implementation — the `Scheduler`→`Owner` relationship was wrong, `Task` needed a `frequency` field, and `Scheduler` needed four more methods that were not anticipated upfront. Updating the UML at the end to match the real code made it genuinely useful for explaining the system, rather than just an artifact of the planning phase. AI helped surface these gaps quickly, but the verification — reading the actual code — always had to happen before trusting the suggestion.
