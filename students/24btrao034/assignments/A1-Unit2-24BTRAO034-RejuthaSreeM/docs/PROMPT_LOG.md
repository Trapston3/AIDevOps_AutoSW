# Automation in Software Development — Assignment 1

## Prompt Log: Expense Splitter (Cursor AI)

| Field | Details |
| --- | --- |
| **Student** | Rejutha Sree |
| **USN** | 24BTRAO034 |
| **Unit** | Unit 2 — Automation in Software Development |
| **Assignment** | Assignment 1 |
| **Tool used** | Cursor AI — Free Hobby Tier |
| **Task chosen** | **Option A** — Build a small CLI or module from scratch |

### Project summary

The project is an **Expense Splitter** Python application. Work in this Cursor session created a beginner-friendly package with a core expense data model, equal-share rounding, and **pytest** unit tests. A full interactive CLI was not requested in the prompts used so far and was not implemented.

---

## Tool used

**Cursor AI (Free Hobby Tier)** was used through the Cursor agent chat. Prompts were given in natural language. The agent created and edited files in the workspace and ran `python -m pytest` after implementation steps.

---

## Task chosen

**Option A — Build a small CLI or module from scratch.**

The Expense Splitter module supports:

- recording an expense (`add_expense`)
- listing expenses associated with a person (`expenses_for_person`)
- totalling recorded amounts (`total_amount`)
- splitting one expense equally among participants, including remainder cents (`equal_shares`)

Tests live under `tests/` and are run with pytest.

---

## Prompt log

The table below records the **actual** development prompts from this Cursor conversation. Wording is copied from the chat, not rewritten.

| Step # | Technique | Exact prompt used | Tool response + evaluation |
| --- | --- | --- | --- |
| 1 | Zero-shot | See [Zero-shot prompting](#1-zero-shot-prompting) (full prompt). Opening request: create a clean initial project structure and core data model only; Python; pytest layout; no complete application yet. | The agent created `expense_splitter/` (`models.py` with `Expense` and `ExpenseSplitter`), `tests/test_models.py`, `requirements.txt` (pytest only), `pytest.ini`, `.gitignore`, and `README.md`. It added field validation (empty description, non-positive amount, empty participants). **7 tests passed.** Evaluation: the request was followed. No CLI and no split calculations were added. Suitable first step. |
| 2 | Few-shot | See [Few-shot prompting](#2-few-shot-prompting) (full prompt). Four examples of function/class names and one-line docstrings were supplied (`add_expense`, `total_amount`, `expenses_for_person`, `Expense`). | Docstrings were updated to the example style. `add_expense` was already present; `total_amount()` and `expenses_for_person()` were added to match the example names. Existing validation behaviour was unchanged. **10 tests passed.** Evaluation: naming and docstring style matched the examples. The prompt also said not to introduce unnecessary features; adding the two extra methods was driven by the few-shot names rather than by a separate feature request. |
| 3 | Chain-of-thought | See [Chain-of-thought prompting](#3-chain-of-thought-prompting) (full prompt). The 100 split among 3 people (33.33, 33.33, 33.34) was specified, with four numbered reasoning steps, then implement, regression-test, and run the full suite. | The agent inspected `models.py` and reported that **no equal-split logic existed**. It implemented `Expense.equal_shares()` using integer cents and gave leftover cents to the last participant(s). Tests were added for 100.00 / 3 and for other amounts summing to the original expense. **12 tests passed.** Evaluation: the remainder case was handled correctly; CoT was appropriate because the bug is easy to miss with naive `amount / n` rounding. |

---

## 1. Zero-shot prompting

Zero-shot prompting means stating the task without worked examples of code or docstrings.

### Exact prompt used

> I need to build a small Python CLI application called Expense Splitter for an academic assignment.
>
> Create a clean initial project structure for an expense-splitting application. The application should allow users to record expenses, list expenses, calculate the total amount spent, and calculate how much each participant owes.
>
> For now, focus only on creating the basic project structure and core data model. Use Python and keep the implementation simple and beginner-friendly.
>
> Do not add unnecessary dependencies or advanced architecture. Include a suitable structure for unit tests using pytest.
>
> Do not implement the complete application yet. Only create the initial project structure and core data model.

### Tool response (summary)

The agent treated the empty workspace as a new project and added:

- `expense_splitter/models.py` — `Expense` and `ExpenseSplitter` with `add_expense`
- `tests/test_models.py` — creation, validation, and add-expense tests
- pytest configuration and a short README

It then installed pytest and reported **7 passed**.

### Evaluation

This technique was appropriate because the goal was a **blank-folder scaffold**, not a specific coding style. Constraints (“structure and data model only”, “no unnecessary dependencies”) were enough. The model did not need sample functions to invent a reasonable dataclass-based design.

---

## 2. Few-shot prompting

Few-shot prompting means giving **concrete examples** of the desired output shape so the model can copy the pattern.

### Exact prompt used

> Now improve the expense model's documentation and naming style using the following examples.
>
> Follow these examples consistently:
>
> Example 1:  
> Function: add_expense()  
> Docstring: "Add one expense to the tracker."
>
> Example 2:  
> Function: total_amount()  
> Docstring: "Return the total value of all recorded expenses."
>
> Example 3:  
> Function: expenses_for_person()  
> Docstring: "Return all expenses associated with the given person."
>
> Example 4:  
> Class: Expense  
> Docstring: "Represent one expense with an amount, description, and participants."
>
> Update the existing expense-related code so that its public classes and functions follow this concise one-line docstring style. Keep the existing functionality unchanged and do not introduce unnecessary features.
>
> Also add or update tests if needed to ensure the existing behavior still works.

### Tool response (summary)

Public docstrings were changed to single-line form. The `Expense` class docstring matches Example 4. `add_expense` uses the Example 1 sentence. `total_amount` and `expenses_for_person` were implemented with the Example 2 and 3 names and sentences. New tests covered summing expenses and filtering by person. **10 tests passed.**

### Evaluation

Few-shot was appropriate for **API wording**. Zero-shot would have left the earlier longer `Attributes:` docstring. The examples made the required style unambiguous. A small judgement call remained: whether Examples 2 and 3 were documentation samples only, or methods to add. The agent added the methods. That still matches the named public API in the prompt.

---

## 3. Chain-of-thought prompting

Chain-of-thought prompting means asking the model to **reason in ordered steps** before changing code, especially for an edge case.

### Exact prompt used

> The expense splitter needs to handle an important edge case correctly.
>
> Suppose an expense of 100 is shared equally by 3 people. The amount owed by each person should be 33.33, 33.33, and 33.34 so that the individual amounts add up exactly to 100.00 rather than 99.99.
>
> Please inspect the current expense calculation logic and tests, identify whether this rounding edge case is handled correctly, and fix it if necessary.
>
> Think step by step about:
>
> 1. How the current calculation distributes the amount.  
> 2. Where rounding can cause a mismatch.  
> 3. How the remainder should be distributed.  
> 4. How to test that the individual shares always add up exactly to the original expense.
>
> Then implement the fix and add an appropriate regression test. Run the complete test suite afterward.

### Tool response (summary)

The agent’s reasoning matched the requested steps:

1. **Current distribution:** there was no share calculation in `models.py`.
2. **Rounding mismatch:** `100 / 3` rounded per person can yield three times `33.33` (`99.99`).
3. **Remainder:** convert to cents (`10000`), divide by 3 (`3333` remainder `1`), give the extra cent to the last person → `33.33`, `33.33`, `33.34`.
4. **Tests:** `test_equal_shares_gives_remainder_cent_to_last_people` plus a test that several amounts always sum (when rounded to cents) to the original expense.

`python -m pytest` reported **12 passed**.

### Evaluation

CoT was appropriate because money rounding is a **logic** problem, not a style problem. Asking for inspection first avoided blindly editing the wrong function. The numbered remainder rule in the prompt (`33.34` on the last share) was implemented as specified.

---

## Technique coverage summary

| Technique | Where it was used | Why it was appropriate |
| --- | --- | --- |
| **Zero-shot** | Step 1 — initial package, `Expense` / `ExpenseSplitter`, pytest layout | The task was open-ended scaffolding. No example project was required. Constraints (Python, pytest, model only) were sufficient. |
| **Few-shot** | Step 2 — one-line docstrings and public names | Four input–output examples defined the exact names and docstring sentences. Pattern-matching is what few-shot is for. |
| **Chain-of-thought** | Step 3 — 100.00 among 3 people | The failure mode is a remainder of one cent. Step-by-step inspection, remainder policy, then a regression test reduced the chance of `99.99` slipping through. |

All three techniques required by the assignment were used on **real** Expense Splitter prompts in this Cursor session. No extra fictional chat turns were added to this log.

---

## Screenshots


| Figure | Technique | Suggested file | What the screenshot should show |
| --- | --- | --- | --- |
| Figure 1 | Zero-shot prompting | `docs/zero_shot.png` | The Step 1 prompt (project structure and core data model only) and the agent creating files / reporting 7 passing tests. |
| Figure 2 | Few-shot prompting | `docs/few_shot.png` | The Step 2 prompt with the four function/class examples, and the updated one-line docstrings (or 10 passing tests). |
| Figure 3 | Chain-of-thought prompting | `docs/chain_of_thought.png` | The Step 3 prompt with the four “think step by step” items, `equal_shares` / 33.33–33.34, and **12 passed**. |

![Figure 1. Zero-shot prompting in Cursor AI](docs/zero_shot.png)

*Figure 1. Zero-shot prompt and initial project-structure response.*

![Figure 2. Few-shot prompting in Cursor AI](docs/few_shot.png)

*Figure 2. Few-shot examples for names and one-line docstrings.*

![Figure 3. Chain-of-thought prompting in Cursor AI](docs/chain_of_thought.png)

*Figure 3. Chain-of-thought rounding edge case and full pytest run.*

---

## Reflection

This Expense Splitter project was built in Cursor’s agent chat on the Free Hobby Tier. That workflow is different from GitHub Copilot’s usual role as inline autocomplete inside the editor.

Cursor’s main strength here was completing a whole task in one request: it created the package layout, data model, and pytest files, then ran the suite. Few-shot prompting worked because the examples for names and one-line docstrings were applied across `Expense` and `ExpenseSplitter`. Chain-of-thought prompting helped with money rounding: the model inspected the code, saw that equal-split logic was missing, implemented cent-based remainder assignment, and added a regression test. Running pytest in the same session made evaluation immediate (7, then 10, then 12 passing tests).

Limitations were also clear. On the Hobby Tier, replies can be slower, and installing pytest plus running tests on Windows took about a minute in this session. The agent sometimes did slightly more than asked. After the few-shot docstring prompt, which said not to add unnecessary features, it still added `total_amount()` and `expenses_for_person()` because those names appeared in the examples. Copilot more often waits until the developer starts the next function. Copilot is typically faster for small, local edits (a loop or a test assertion) but weaker at creating a multi-file project from an empty folder, or at remainder rounding, unless the developer writes a long chat prompt.

In a real team, Cursor (or a similar agent) is useful for scaffolding, refactors that touch several files, and reproducing a failing edge case with tests. Copilot is useful in daily work on a familiar codebase, when developers want short completions without leaving the editor. Using both is reasonable: Copilot for line-level speed, Cursor when the task needs planning, file creation, and verification.
