# PawPal+ Project Reflection

## 1. System Design

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
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
