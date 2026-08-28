# Reflection — Hermes Agent vs. GitHub Copilot

*(Assignment requirement: 200–300 words comparing the tool used with GitHub Copilot.)*

I built this entire assignment with **Hermes Agent**, an agentic CLI coding assistant,
rather than Copilot's inline-suggestion model, and the difference in *shape* was the
biggest surprise. Copilot ghosts completions inside the file you're editing; Hermes
takes whole verbatim prompts, plans multi-step work, writes files, runs the test suite,
and reports back a summary I could paste straight into my prompt log. For assignment-style
work — scaffold, tests, refactor, debug — that loop felt faster: one clear prompt produced
`main.py` complete and passing, where the same scope would have been dozens of accepted
line-suggestions in Copilot.

The trade-off was latency and trust. Each Hermes turn took minutes, not milliseconds,
so quick "what does this flag do?" questions would favor Copilot. It also needed more
*deliberate correction*: after its few-shot error-envelope refactor, one of my existing
tests went red because it still asserted FastAPI's default error shape — the tool had
done exactly what I asked without noticing the contract break, so I edited the test myself.
Twice, API quota/connection errors killed runs mid-task; I noted them rather than hiding
them, since real quota limits are themselves useful observations about a tool.

Where it clearly won: convention enforcement via few-shot examples (25 docstrings rewritten
in one pass) and chain-of-thought debugging — watching it trace `round(1.005, 2)` to binary
floating-point representation was better evidence of understanding than any inline diff.

In a real team I'd pick Copilot for high-frequency editing inside a mature codebase, and
Hermes for greenfield scaffolding, test generation, refactors across many files, and
root-cause hunts — anything where delegating a whole verified unit of work beats
co-piloting every line.
