# Assignment A1 — AI Coding Assistant Practicum

**Student:** Ashwin Lahkar
**USN:** 24BTRAO004
**Unit 2 — Automation in Software Development**

## Tool Used

**Hermes Agent** — an agentic CLI coding assistant (Nous Research). The assignment
brief explicitly permits "any other AI-powered coding assistant of comparable
capability (e.g., an agentic IDE or CLI assistant)," and Hermes Agent is a full
agentic assistant: it reads and edits files, runs the test suite, and reasons
about code, which is the same capability class as Copilot/Cursor/Amazon Q.

## Task Chosen

**Option B** — fork a small public repo and add one new feature plus tests.

- **Base repo:** `evolutionary_feature_selection` (297 LOC of Python across
  `main.py`, `ga_engine.py`, `fitness.py` — within the required 200–600 LOC band).
- **New feature:** **Elitism** for the genetic algorithm — the fittest
  `elite_count` chromosomes of each generation are copied unchanged into the
  next generation, so the best solution is never destroyed by crossover/mutation.
- **Tests added:** 18 pytest unit tests (baseline suite + elitism suite + guards).

## Prompt Log

One row per meaningful prompt. Technique abbreviations: **ZS** = Zero-shot,
**FS** = Few-shot, **CoT** = Chain-of-thought.

| Step # | Technique | Exact prompt used | Tool response + evaluation |
|--------|-----------|-------------------|----------------------------|
| 1 | Zero-shot | "Read the three modules in this repository (fitness.py, ga_engine.py, main.py) and give me a concise technical summary: what the project does, the role of each module, the public functions and their signatures, and any gaps (missing tests, missing features, or robustness issues) that would be worth working on next." | Produced an accurate module-by-module summary and identified the real gaps: no test suite, no elitism, no input validation. **Accepted** — this is a well-known, unambiguous comprehension task, so zero-shot (no examples) was the right choice. It also surfaced elitism as the feature to build. |
| 2 | Zero-shot | "This repo has no tests. Create a pytest suite under tests/ for the EXISTING code only (do not change any production code yet): a conftest.py with a session-scoped fixture that loads the dataset once, plus unit tests for create_population, evolve, load_dataset and evaluate_fitness. Use a cheap deterministic counting fitness (fitness = number of 1s) for the GA tests so they run in milliseconds, and seed the RNG so tests are reproducible." | Created `tests/conftest.py`, `tests/test_ga_engine.py`, `tests/test_fitness.py` — 11 tests. `pytest tests/ -v` → **11 passed in 1.20s**. **Accepted as-is.** Zero-shot fit because pytest scaffolding is a standard, well-defined task with one obvious correct shape. See `screenshots/step2_zero_shot.png`. |
| 3 | Few-shot | "Add elitism to the genetic algorithm in ga_engine.py: the best `elite_count` chromosomes of each generation must be copied unchanged into the next generation (no crossover, no mutation). Add a module-level default ELITE_COUNT = 2 and a new `elite_count` parameter on evolve(). elite_count=0 must behave exactly like the current code. Raise ValueError if elite_count < 0 or elite_count >= population_size. Match the existing code conventions exactly — here are two examples of how functions in this repo are documented and typed: [Example 1: the `create_population` NumPy-style docstring; Example 2: the `# ----- GA hyper-parameters -----` constant banner]. Follow the same NumPy-style docstring format, the same `# -----` comment banner for constants, and the same type-hint style." | Added `ELITE_COUNT: int = 2` under the existing banner, an `elite_count` parameter with NumPy-style Parameters/Raises docstring sections, ValueError guards, and an elite-copy step between selection and crossover. Output matched both provided style examples exactly. **Accepted.** Few-shot was the right choice because the *format* (docstring style, constant banner, type hints) mattered as much as the logic — the two in-prompt examples locked the conventions. Existing 11 tests still passed. See `screenshots/step3_few_shot.png`. |
| 4 | Few-shot | "Write pytest tests for the new elitism feature in ga_engine.py. Match the style of the tests already in tests/test_ga_engine.py exactly. Two examples of the existing style: [Example 1: `test_create_population_shape` with a one-line docstring; Example 2: the `_counting_fitness` deterministic helper + a seeded GA test]. Cover at least: (a) the fittest chromosomes appear unchanged in the next generation, (b) elites survive even with mutation_rate=1.0, (c) the population's best fitness never drops across generations when elitism is on, (d) elite_count=0 still works, (e) both ValueError guards. Use small hand-written populations with DISTINCT fitness values where determinism matters, and reuse the _counting_fitness helper." | Created `tests/test_elitism.py` with 6 tests in the existing style (docstring-per-test, deterministic helper, seeded RNG). **Accepted.** Few-shot fit because matching the *existing test conventions* was the point — the two examples ensured the new tests were indistinguishable in style from the old ones. `pytest` → 6 passed in 0.06s. |
| 5 | Chain-of-thought | "Three elitism tests are now failing after I edited ga_engine.py. Think step by step about what could be wrong. The failures are: 1. test_elites_appear_unchanged_in_next_generation — expected (1,1,1,1) in the next generation but got {(0,0,0,0), (1,0,0,0), (1,1,0,0)} 2. test_elites_survive_maximum_mutation — same missing-elite symptom 3. test_best_fitness_never_drops_with_elitism — best fitness dropped from 7.0 to 6.0 across generations. Trace through the evolve() loop with a concrete 4-chromosome population and tell me the root cause and the exact fix. Do not guess — reason from the code." | Step-by-step trace: (1) fittest absent + worst present ⇒ the copied slice is the bottom of the ranking; (2) with pop=[[1,1,1,1],[1,1,1,0],[1,1,0,0],[1,0,0,0]] and elite_count=2, `sorted_pop[-elite_count:]` = `sorted_pop[-2:]` = the two WORST individuals; (3) **root cause:** negative slicing takes the END of a descending-sorted list; (4) secondary bug found: `sorted_pop[-0:]` = the ENTIRE population, so elite_count=0 would copy everyone; (5) fix = head-slice `sorted_pop[:elite_count]`; (6) predicted all 3 tests pass. Fix applied → **17 passed in 1.31s**, exactly as predicted. **CoT found the correct root cause (and a hidden `[-0:]` bug).** Right choice because this was genuine non-trivial debugging. See `screenshots/step5_chain_of_thought.png`. |
| 6 | Zero-shot | "Update main.py so the experiment uses the new elitism feature explicitly: import ELITE_COUNT from ga_engine, pass elite_count=ELITE_COUNT to both evolve() calls, and print the elitism configuration (elite count) once after the dataset loads, e.g. 'Elitism: top 2 chromosomes preserved each generation.' Keep the existing print style (emoji headers, dashed separators)." | Wired `ELITE_COUNT` into both `evolve()` calls and added the config print. End-to-end run confirmed: prints "Elitism: top 2 chromosomes preserved each generation." and reports 97.08% → 99.42% while dropping 17 features. **Accepted as-is.** Zero-shot fit because this was unambiguous plumbing with a single obvious implementation. |
| 7 | Chain-of-thought | "I found that evolve() returns best_chromosome=None when generations=0, and main.py then crashes on int(np.sum(best)) with a TypeError. Think step by step: why does best_chromosome stay None, what is the correct contract for evolve() here, and what is the cleanest fix that matches the existing ValueError-guard style already used for elite_count? Also tell me what test would lock this behaviour in." | Step-by-step: (1) `best_chromosome` is only assigned inside the `for _ in range(generations)` loop, so with generations=0 it stays None, violating the declared `list[int]` return type; (2) with zero generations there is nothing to observe, so the call is a caller error; (3) cleanest fix = fail fast with `if generations < 1: raise ValueError(...)`, matching the elite_count guard style (the alternative — silently evaluating the initial population — was considered and rejected because it would hide the caller bug); (4) locking test = `test_zero_generations_raises`. Fix + test applied → **18 passed in 1.33s.** This was a **bug found in the original code** (not introduced), traced via CoT. |
| 8 | Few-shot | "Update README.md to document the new elitism feature and the test suite. Match the existing README's structure and tone exactly. Two examples of the existing style: [Example 1: the Results markdown table; Example 2: the numbered 'How It Works' list]. Add: (a) a mention of elitism in the intro line, (b) a 'What's New' bullet list covering elitism + the test suite, (c) an elitism step in the How It Works list, (d) a 'Running the Tests' section with the pytest command, (e) the tests/ folder in the Repository Structure tree. Keep the same emoji-free, concise tone." | Updated README with a What's New section, an elitism step, a Running the Tests section, the tests/ folder in the tree, and added `pytest>=7.0` to requirements.txt. Output matched the existing table/list style. **Accepted.** Few-shot fit because matching the README's established structure and tone was the whole point. |

### Technique coverage summary

| Technique | Steps | Where & why |
|-----------|-------|-------------|
| Zero-shot | 1, 2, 6 | Well-known, unambiguous tasks: codebase comprehension, standard pytest scaffolding, and simple wiring. No examples needed — one obvious correct output. |
| Few-shot | 3, 4, 8 | Tasks where output *format / project conventions* mattered: matching NumPy-style docstrings + constant banner, matching existing test style, matching README structure. 2 in-prompt examples each locked the style. |
| Chain-of-thought | 5, 7 | Genuinely non-trivial reasoning: debugging a failing test (traced a wrong-slice regression to its root cause) and reasoning about a latent edge case (generations=0 → None). Explicit "think step by step" in both. |

## Screenshots

Genuine terminal transcripts of the assistant interaction, one per technique:

- `screenshots/step2_zero_shot.png` — Zero-shot (pytest scaffold)
- `screenshots/step3_few_shot.png` — Few-shot (implement elitism)
- `screenshots/step5_chain_of_thought.png` — Chain-of-thought (debug failing test)

## Reflection (Hermes Agent vs. GitHub Copilot)

GitHub Copilot, as demonstrated in Class 02, is an *inline completion* tool: it
suggests the next lines inside your editor as you type, which makes it extremely
fast for boilerplate and for finishing a thought you have already started.
Hermes Agent works differently — it is an *agentic* assistant you hand a whole
task to in natural language, and it reads files, writes code, runs the test
suite, and iterates on its own.

Where Hermes Agent felt **faster**: multi-file, cross-cutting work. Scaffolding
the entire pytest suite, wiring elitism through `ga_engine.py` *and* `main.py`
*and* the README in one instruction, and especially the debugging step — where
it traced a failing test to a wrong-slice root cause and even caught a hidden
`[-0:]` edge case I had not mentioned — would have taken many manual
prompt-and-paste cycles with Copilot's line-level suggestions.

Where it felt **slower / needed more correction**: it is less suited to the
micro-level "finish this exact line while I keep typing" flow, and because it
acts autonomously you must still review every edit it makes — it introduced a
regression (the negative slice) that only the test suite caught. That reinforced
the lesson that the tests, not the assistant, are the source of truth.

In a real team I would pick **Copilot** for fast, in-the-flow completion while I
already know what to write, and **Hermes Agent** for delegated, reasoning-heavy
tasks — scaffolding, refactors across files, and debugging — where an agent that
can run the tests and iterate beats autocomplete.
