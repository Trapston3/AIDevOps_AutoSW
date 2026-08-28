# Prompt Log — Assignment 1: AI Coding Assistant Practicum

| Field | Value |
|---|---|
| Student | Sashankar J |
| USN | 24BTRAO037 |
| Tool | **Hermes Agent** — an agentic CLI coding assistant (frontier-LLM backed, runs in the terminal, can read/write files, run tests, and iterate autonomously). Not GitHub Copilot. |
| Task | Option A — small CLI/library from scratch: an **expense splitter** with 7 public functions/classes and 14 unit tests |
| Session date | 27 August 2026 |

> Because the tool is a terminal agent, the "screenshots" are terminal
> captures of the real session exchanges, stored in
> [`screenshots/`](screenshots/). Each row records the verbatim prompt, what
> the tool returned, whether I accepted / edited / rejected it, and why the
> technique fit the step.

---

## Prompt log (chronological)

| Step # | Technique | Exact prompt used | Tool response + my evaluation |
|---|---|---|---|
| 1 | Zero-shot | `Create a Python project for an expense splitter: pyproject.toml (setuptools, src layout, pytest config) and a package src/expense_splitter with a function validate_members(members) that raises ValueError if the member list is empty, contains blank names, or contains duplicates.` | Created the src-layout scaffold, `pyproject.toml`, and a clean `validate_members` with all three checks in the right order (empty → blank → duplicate). **Accepted as-is.** Zero-shot fit because project scaffolding and standard validation are unambiguous, well-trodden shapes — no examples needed. See [`row1_zero_shot_scaffold.png`](screenshots/row1_zero_shot_scaffold.png). |
| 2 | Chain-of-thought | `pip install -e . fails with: "configuration error: project.authors[0] must not contain {'usn'} properties". Think step by step about what PEP 621 actually allows in the authors field and fix pyproject.toml.` | Reasoned: PEP 621 `authors` entries accept only `{name, email}` → my custom `usn` key is not a recognized property → setuptools' schema validation rejects the whole build → fix is to drop the key and record the USN in the README instead. **Accepted as-is**; the editable install then succeeded. CoT fit because the traceback names the symptom, not the standard — the model had to recall the PEP 621 spec, not just read the error. |
| 3 | Zero-shot | `Add to splitter.py: split_evenly(amount, n) that splits a Decimal amount into n equal shares quantized to cents; parse_expense_line(line) that parses lines of the form "payer amount payee1 payee2 ..." and returns (payer, Decimal amount, list of payees), raising ValueError on malformed lines; and a private _as_decimal helper that coerces input and rejects NaN/infinity.` | Returned all three functions using `Decimal.quantize(0.01, ROUND_HALF_EVEN)` and `line.strip().split()`, with the right tuple shape and errors. **Accepted with a mental note** — I already suspected the per-share rounding would bite later (it did, step 6). Zero-shot fit: standard signatures, well-known Decimal/str APIs. |
| 4 | Zero-shot | `Add a Splitter dataclass: a members list plus a per-member Decimal balance map; add_expense(payer, amount, payees) that validates payer/payees/amount, splits the expense equally among payees and updates balances; and compute_balances(expenses) that builds a Splitter from raw (payer, amount, payees) rows and returns the balance map.` | Returned the dataclass with `__post_init__` validation, correct credit/debit updates, and an order-preserving member dedupe in `compute_balances`. **Accepted as-is.** A standard stateful-class shape → zero-shot. |
| 5 | Few-shot | `Write the pytest suite for everything so far, matching EXACTLY this style — here are examples of the convention:` <br>`def test_split_evenly_basic():`<br>&nbsp;&nbsp;&nbsp;&nbsp;`assert split_evenly(Decimal("60"), 3) == [Decimal("20.00"), Decimal("20.00"), Decimal("20.00")]`<br>`def test_split_evenly_single_share():`<br>&nbsp;&nbsp;&nbsp;&nbsp;`assert split_evenly(Decimal("42.00"), 1) == [Decimal("42.00")]`<br>`def test_split_evenly_rejects_nonpositive_n():`<br>&nbsp;&nbsp;&nbsp;&nbsp;`with pytest.raises(ValueError):`<br>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;`split_evenly(Decimal("10"), 0)`<br>`Same naming (test_<function>_<case>), Decimal literals, one assert per test, pytest.raises for error cases.` | Produced 12 tests matching the naming, Decimal-literal, and `pytest.raises` conventions exactly — no style drift. **Accepted**, with one test deliberately left red: `test_split_evenly_rounding_remainder_goes_to_last` failed (see step 6). An earlier zero-shot attempt at the same step had returned unittest-style classes and string amounts; the 3 examples pinned the format. That delta is exactly why few-shot was right here: the *convention* was the requirement, not the logic. See [`row5_few_shot_tests.png`](screenshots/row5_few_shot_tests.png). |
| 6 | Chain-of-thought | `test_split_evenly_rounding_remainder_goes_to_last is failing. Splitting Decimal("10.00") three ways returns [3.33, 3.33, 3.33] which sums to 9.99, not 10.00 — one cent vanishes. Think step by step: trace exactly where the cent is lost in split_evenly, then fix it so the shares ALWAYS sum exactly to the original amount. Explain your reasoning before changing code.` | The tool reasoned out loud: (1) 10.00 / 3 = 3.3333…; (2) `quantize(0.01, ROUND_HALF_EVEN)` → 3.33 per share; (3) 3.33 × 3 = 9.99, so the truncation remainder (0.01) is silently dropped; (4) root cause = every share is computed independently, so no share absorbs the remainder and the invariant `sum(shares) == amount` is never enforced; (5) fix = derive the last share as `amount − share × (n−1)` = 3.34, making the sum exact by construction. It applied the fix and re-ran the suite: **12 passed** (the two `simplify_debts` tests came later, at step 8). **Accepted as-is** — the root cause was correct and the invariant now holds. This was genuinely non-trivial (an invariant bug, not a syntax slip), which is why CoT was the right technique: forcing the step-by-step trace surfaced the "independent rounding" cause instead of a blind patch. See [`row6_cot_rounding_bug.png`](screenshots/row6_cot_rounding_bug.png). |
| 7 | Few-shot | `Add NumPy-style docstrings to every public function in splitter.py, following this example:` <br>`def split_evenly(amount: Decimal, n: int) -> List[Decimal]:`<br>&nbsp;&nbsp;&nbsp;&nbsp;`"""Split ``amount`` into ``n`` equal shares in cents.`<br><br>&nbsp;&nbsp;&nbsp;&nbsp;`Each share is quantized to a cent with banker's rounding; the last`<br>&nbsp;&nbsp;&nbsp;&nbsp;`share absorbs any rounding remainder so the returned shares always`<br>&nbsp;&nbsp;&nbsp;&nbsp;`sum exactly to ``amount``.`<br>&nbsp;&nbsp;&nbsp;&nbsp;`"""`<br>`Double-backtick parameters, one summary line, then a short prose paragraph.` | All docstrings came back in the same voice: summary line + prose paragraph, ``param`` markup, `:meth:` cross-references. **Accepted as-is.** Few-shot was the right call because "write docstrings" zero-shot returns whatever style the model feels like; the example locked the house style across all 7 callables consistently. |
| 8 | Zero-shot | `Add simplify_debts(balances) that converts a dict of net balances into the minimal list of (debtor, creditor, amount) cash transfers using a greedy two-pointer settlement, plus tests including a round-trip with compute_balances.` | Returned the greedy creditors/debtors two-pointer algorithm, sorted by magnitude, quantized to cents, plus the round-trip and balanced-map tests. **Accepted as-is** after the suite passed. Well-known settlement algorithm → zero-shot. |
| 9 | Zero-shot | `Write a CLI entry point __main__.py: take expense lines as argv, parse each, compute balances, print one "debtor -> creditor: amount" line per transfer, exit code 2 with a usage message on bad input.` | Returned the CLI exactly as specified, including stderr for errors and exit codes. **Accepted as-is.** Standard argv CLI boilerplate → zero-shot. |

**Totals:** 9 prompts — 5 zero-shot, 2 few-shot, 2 chain-of-thought.
Final state: `14 passed in 0.03s`, CLI verified by hand:

```
$ python -m expense_splitter 'alice 60 alice bob carol' 'bob 30 bob carol'
carol -> alice: 35.00
bob -> alice: 5.00
```

---

## Reflection (≈250 words): agentic CLI assistant vs GitHub Copilot

In Class 02 we used GitHub Copilot, which completes code *inside the editor* —
it is fast for the line you are currently typing, but it only ever sees the
file you have open and it cannot run anything. This assignment I used an
agentic CLI assistant, and the experience was different in three concrete
ways.

**Faster:** whole-scaffolding steps. One prompt produced the package layout,
`pyproject.toml`, and the first function in a single pass, and the agent then
created a venv, installed the package, and ran pytest *itself*. With Copilot
I would have hand-created every file and run every command myself. The
few-shot steps were also cleaner: I could paste three example tests into one
prompt and get a convention-matching suite back, whereas Copilot
autocomplete drifts in style unless the examples are already in the file.

**Slower / needed more correction:** tight feedback loops on small edits.
Copilot's inline ghost-text is instant for a two-line change; with the agent
every change is a full request/response round-trip, and I had to debug its
first `pyproject.toml` because it invented a non-standard `usn` key that
broke the build. Quota-wise the agent burns far more tokens per step than
Copilot completions.

**Where the agent won decisively** was the chain-of-thought debugging step:
it traced the vanishing-cent rounding bug by reasoning about the invariant,
then fixed and *re-ran the failing test to confirm*. Copilot cannot execute
tests at all, so that loop would have been entirely manual.

In a real team I would keep both: Copilot for in-the-flow typing, an agentic
assistant for scaffolding, test loops, and debugging sessions.
