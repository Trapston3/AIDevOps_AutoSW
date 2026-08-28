# Assignment 01 — AI Coding Assistant Practicum

```yaml
task_id: assignment-01
title: AI Coding Assistant Practicum (Option B — fork + feature + tests)
author: Ashwin Lahkar
usn: 24btrao004
date: 2026-08-28
status: complete
```

## Overview

Submission for **Assignment A1 — AI Coding Assistant Practicum** (Automation in
Software Development, Unit 2), Option B: fork a small public repo, add one new
feature plus tests, and document the entire session with a real prompt log.

The base repository is
[`ghoulraider13-rgb/evolutionary_feature_selection`](https://github.com/ghoulraider13-rgb/evolutionary_feature_selection)
(297 LOC Python — a genetic-algorithm feature-selection pipeline). The new
feature is **elitism**: the fittest chromosomes of each generation are copied
unchanged into the next, so the best solution is never destroyed by crossover
or mutation. On the breast-cancer dataset the GA now cuts features by ~50 %
while raising accuracy from 97.08 % to 99.42 %.

The AI coding assistant used was
[Hermes Agent](https://hermes-agent.nousresearch.com) — an agentic CLI
assistant, permitted by the brief as "any other AI-powered coding assistant of
comparable capability". The prompt log in `evidence/PROMPT_LOG.md` is a genuine
transcript of that session, with one incremental commit per step.

## Architecture / Design

```
src/
├── main.py            # Entry point — runs the 3-trial experiment
├── ga_engine.py       # Core GA: population init, selection, crossover,
│                      #   mutation, and the new elitism step
├── fitness.py         # Dataset loading & fitness evaluation
├── tests/             # 18 pytest unit tests
└── requirements.txt   # numpy, scikit-learn, pytest
```

Elitism sits between selection and crossover in `evolve()`: the population is
ranked by fitness, the top `elite_count` (default 2) chromosomes are copied
verbatim into the next generation, and the remainder are produced by the usual
tournament selection + single-point crossover + bit-flip mutation.

Prompting techniques applied (detailed in the prompt log):

- **Zero-shot** — unambiguous, standard steps (codebase summary, pytest
  scaffolding, wiring elitism into `main.py`).
- **Few-shot** — convention-sensitive steps (implementing elitism, writing its
  tests, README updates): two in-prompt style examples locked the existing
  docstring/test conventions.
- **Chain-of-thought** — non-trivial reasoning (debugging a failing test,
  tracing the `generations=0` edge case): explicit step-by-step reasoning
  found the wrong-slice root cause plus a hidden `[-0:]` bug.

## How to run

```bash
# from this deliverable folder (students/24btrao004/assignments/assignment-01-ai-coding-assistant-practicum/)
pip install -r src/requirements.txt
python src/main.py                # runs the 3-trial GA experiment
cd src && python -m pytest tests/ -v   # 18 tests, all green
```

## Dependencies

Declared in `src/requirements.txt`: `numpy>=1.24`, `scikit-learn>=1.3`,
`pytest>=7.0`.

## Results & Evidence

| Trial | Generations | Features Used | Accuracy |
|-------|-------------|---------------|----------|
| Baseline | 0 | 30 / 30 | 97.08 % |
| Midpoint | 5 | ~15 / 30 | 98.83 % |
| Apex | 15 | ~15 / 30 | 99.42 % |

- `evidence/PROMPT_LOG.md` — full step-by-step prompt log (exact prompts,
  responses, evaluations) plus the Hermes-vs-Copilot reflection.
- `evidence/screenshots/step2_zero_shot.png` — zero-shot step (pytest scaffold).
- `evidence/screenshots/step3_few_shot.png` — few-shot step (implement elitism).
- `evidence/screenshots/step5_chain_of_thought.png` — chain-of-thought debug step.

## Known limitations

- Results are measured on a single dataset (breast cancer) with a fixed seed;
  no multi-dataset generalisation study.
- The GA is single-objective (accuracy) — feature-count pressure comes only
  from the fitness penalty term.
- Screenshots are terminal-style renders of the session log rather than raw
  IDE captures, since the assistant used is a CLI agent.
