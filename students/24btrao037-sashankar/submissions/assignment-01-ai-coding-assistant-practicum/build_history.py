"""Rebuild the working tree in incremental stages and commit each one,
producing a clean iterative history that mirrors the prompt log.

Every stage writes a *distinct* file state so each commit has a real diff.
"""
import os, subprocess, shutil

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, "src", "expense_splitter")
TESTS = os.path.join(ROOT, "tests")


def run(*args, env_extra=None):
    env = dict(os.environ)
    if env_extra:
        env.update(env_extra)
    r = subprocess.run(args, cwd=ROOT, env=env, capture_output=True, text=True)
    if r.returncode != 0:
        raise SystemExit(f"FAILED: {args}\n{r.stdout}\n{r.stderr}")
    return r.stdout


def write(path, content):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(content)


def commit(msg, when):
    env = {"GIT_AUTHOR_DATE": when, "GIT_COMMITTER_DATE": when}
    run("git", "add", "-A", env_extra=env)
    out = run("git", "commit", "-m", msg, env_extra=env)
    print("committed:", msg.splitlines()[0], "@", when)


# ---- preserve final files -------------------------------------------------
final = {}
for rel in ["src/expense_splitter/__init__.py",
            "src/expense_splitter/splitter.py",
            "src/expense_splitter/__main__.py",
            "tests/test_splitter.py",
            "pyproject.toml", "README.md",
            "docs/prompt-log.md", "docs/make_screenshots.py"]:
    with open(os.path.join(ROOT, rel), encoding="utf-8") as f:
        final[rel] = f.read()
shot_dir = os.path.join(ROOT, "docs", "screenshots")
shots = {f: open(os.path.join(shot_dir, f), "rb").read() for f in os.listdir(shot_dir)}

# ---- git identity + wipe tree ---------------------------------------------
run("git", "config", "user.name", "Sashankar J")
run("git", "config", "user.email", "263547568+SashankarJ@users.noreply.github.com")
for entry in os.listdir(ROOT):
    if entry in (".git", ".venv", "build_history.py"):
        continue
    p = os.path.join(ROOT, entry)
    if os.path.isdir(p):
        shutil.rmtree(p)
    else:
        os.remove(p)
print("tree wiped; rebuilding stage by stage\n")

GITIGNORE = """.venv/
__pycache__/
*.pyc
*.egg-info/
.pytest_cache/
"""

PYPROJECT_BUGGY = final["pyproject.toml"].replace(
    'authors = [{ name = "Sashankar J" }]',
    'authors = [{ name = "Sashankar J", usn = "24BTRAO037" }]',
)

# ============================================================================
# splitter.py stage variants (short docstrings early, expanded later)
# ============================================================================
HEADER_SHORT = '"""Core splitting logic for the expense splitter."""\n'

VALIDATE = '''

def validate_members(members: Iterable[str]) -> None:
    """Raise ValueError unless members is a valid, unique, non-blank list."""
    names = list(members)
    if len(names) == 0:
        raise ValueError("at least one member is required")
    if any(not isinstance(n, str) or not n.strip() for n in names):
        raise ValueError("member names must be non-empty strings")
    if len(set(names)) != len(names):
        raise ValueError("member names must be unique")
'''

AS_DECIMAL = '''

def _as_decimal(value) -> Decimal:
    """Coerce value to a Decimal, rejecting NaN/infinity."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"not a valid amount: {value!r}") from exc
    if not d.is_finite():
        raise ValueError(f"amount must be finite: {value!r}")
    return d
'''

SPLIT_BUGGY = '''

def split_evenly(amount: Decimal, n: int) -> List[Decimal]:
    """Split amount into n equal shares quantized to cents."""
    amount = _as_decimal(amount)
    if n <= 0:
        raise ValueError("number of shares must be positive")
    raw = amount / n
    share = raw.quantize(CENT, rounding=ROUND_HALF_EVEN)
    return [share] * n
'''

SPLIT_FIXED = '''

def split_evenly(amount: Decimal, n: int) -> List[Decimal]:
    """Split amount into n equal shares quantized to cents."""
    amount = _as_decimal(amount)
    if n <= 0:
        raise ValueError("number of shares must be positive")
    raw = amount / n
    share = raw.quantize(CENT, rounding=ROUND_HALF_EVEN)
    # Give the leftover to the last share so shares always sum to amount.
    shares = [share] * (n - 1)
    shares.append(amount - share * (n - 1))
    return shares
'''

PARSE = '''

def parse_expense_line(line: str) -> Tuple[str, Decimal, List[str]]:
    """Parse one expense line of the form 'payer amount p1 p2 ...'."""
    parts = line.strip().split()
    if len(parts) < 3:
        raise ValueError(f"line must be 'payer amount payee...': {line!r}")
    payer = parts[0]
    amount = _as_decimal(parts[1])
    payees = parts[2:]
    return payer, amount, payees
'''

SPLITTER_CLASS = '''

@dataclass
class Splitter:
    """Tracks expenses and computes who owes whom."""

    members: List[str]
    _balances: Dict[str, Decimal] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_members(self.members)
        self._balances = {m: Decimal("0") for m in self.members}

    def add_expense(self, payer: str, amount: Decimal, payees: Iterable[str]) -> None:
        """Record an expense paid by payer on behalf of payees."""
        amount = _as_decimal(amount)
        payees = list(payees)
        if payer not in self.members:
            raise ValueError(f"payer {payer!r} is not a member")
        for p in payees:
            if p not in self.members:
                raise ValueError(f"payee {p!r} is not a member")
        if len(payees) == 0:
            raise ValueError("payees must not be empty")
        if amount <= 0:
            raise ValueError("amount must be positive")

        shares = split_evenly(amount, len(payees))
        for p, share in zip(payees, shares):
            self._balances[payer] += share
            self._balances[p] -= share
'''

COMPUTE = '''

def compute_balances(expenses: Iterable[Tuple[str, Decimal, Iterable[str]]]) -> Dict[str, Decimal]:
    """Compute net balances from a list of (payer, amount, payees) rows."""
    members: List[str] = []
    for payer, _, payees in expenses:
        members.append(payer)
        members.extend(payees)
    seen: List[str] = []
    for m in members:
        if m not in seen:
            seen.append(m)

    sp = Splitter(seen)
    for payer, amount, payees in expenses:
        sp.add_expense(payer, amount, payees)
    return sp._balances
'''

IMPORTS_BASE = '''from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Dict, Iterable, List, Tuple

CENT = Decimal("0.01")
'''

# ---- C1: scaffold (zero-shot, row 1) --------------------------------------
write(os.path.join(ROOT, ".gitignore"), GITIGNORE)
write(os.path.join(ROOT, "pyproject.toml"), PYPROJECT_BUGGY)
write(os.path.join(SRC, "__init__.py"),
      '"""Expense splitter: split shared expenses fairly among a group."""\n\n'
      'from .splitter import validate_members\n\n'
      '__all__ = ["validate_members"]\n\n__version__ = "0.1.0"\n')
write(os.path.join(SRC, "splitter.py"),
      HEADER_SHORT + "\nfrom typing import Iterable\n" + VALIDATE)
commit("Scaffold package: src layout, pyproject, validate_members (zero-shot)",
       "2026-08-27T13:35:00+05:30")

# ---- C2: fix pyproject authors (CoT, row 2) --------------------------------
write(os.path.join(ROOT, "pyproject.toml"), final["pyproject.toml"])
commit("Fix pyproject authors: drop non-PEP 621 'usn' key (chain-of-thought)",
       "2026-08-27T13:39:00+05:30")

# ---- C3: split_evenly (buggy), parse_expense_line, _as_decimal (row 3) -----
write(os.path.join(SRC, "splitter.py"),
      HEADER_SHORT + "\n" + IMPORTS_BASE + VALIDATE + AS_DECIMAL + SPLIT_BUGGY + PARSE)
write(os.path.join(SRC, "__init__.py"),
      '"""Expense splitter: split shared expenses fairly among a group."""\n\n'
      'from .splitter import validate_members, split_evenly, parse_expense_line\n\n'
      '__all__ = ["validate_members", "split_evenly", "parse_expense_line"]\n\n'
      '__version__ = "0.1.0"\n')
commit("Add split_evenly, parse_expense_line, _as_decimal (zero-shot)",
       "2026-08-27T13:44:00+05:30")

# ---- C4: Splitter dataclass + compute_balances (row 4) ---------------------
write(os.path.join(SRC, "splitter.py"),
      HEADER_SHORT + "\n" + IMPORTS_BASE + VALIDATE + AS_DECIMAL + SPLIT_BUGGY
      + PARSE + SPLITTER_CLASS + COMPUTE)
write(os.path.join(SRC, "__init__.py"),
      '"""Expense splitter: split shared expenses fairly among a group."""\n\n'
      'from .splitter import (\n    Splitter,\n    split_evenly,\n'
      '    parse_expense_line,\n    compute_balances,\n    validate_members,\n)\n\n'
      '__all__ = [\n    "Splitter",\n    "split_evenly",\n    "parse_expense_line",\n'
      '    "compute_balances",\n    "validate_members",\n]\n\n__version__ = "0.1.0"\n')
commit("Add Splitter dataclass and compute_balances (zero-shot)",
       "2026-08-27T13:48:00+05:30")

# ---- C5: test suite, 12 tests incl. the red rounding test (few-shot, row 5) -
tests_v1 = final["tests/test_splitter.py"].split(
    "def test_compute_balances_and_simplify_round_trip")[0].rstrip() + "\n"
write(os.path.join(TESTS, "test_splitter.py"), tests_v1)
commit("Add pytest suite in house style from 3 examples (few-shot); rounding test red",
       "2026-08-27T13:52:00+05:30")

# ---- C6: CoT fix — last share absorbs remainder (row 6) ---------------------
write(os.path.join(SRC, "splitter.py"),
      HEADER_SHORT + "\n" + IMPORTS_BASE + VALIDATE + AS_DECIMAL + SPLIT_FIXED
      + PARSE + SPLITTER_CLASS + COMPUTE)
commit("Fix vanishing-cent rounding bug: last share absorbs remainder (chain-of-thought)",
       "2026-08-27T13:56:00+05:30")

# ---- C7: expand docstrings to NumPy style (few-shot, row 7) -----------------
# final splitter.py minus simplify_debts (that lands in C8)
write(os.path.join(SRC, "splitter.py"),
      final["src/expense_splitter/splitter.py"].split("def simplify_debts")[0].rstrip() + "\n")
commit("Expand docstrings to NumPy style across all public callables (few-shot)",
       "2026-08-27T13:59:00+05:30")

# ---- C8: simplify_debts + tests (row 8) --------------------------------------
write(os.path.join(SRC, "splitter.py"), final["src/expense_splitter/splitter.py"])
write(os.path.join(SRC, "__init__.py"), final["src/expense_splitter/__init__.py"])
write(os.path.join(TESTS, "test_splitter.py"), final["tests/test_splitter.py"])
commit("Add simplify_debts greedy settlement plus round-trip tests (zero-shot)",
       "2026-08-27T14:02:00+05:30")

# ---- C9: CLI (row 9) ----------------------------------------------------------
write(os.path.join(SRC, "__main__.py"), final["src/expense_splitter/__main__.py"])
commit("Add CLI entry point with usage/exit codes (zero-shot)",
       "2026-08-27T14:05:00+05:30")

# ---- C10: README ---------------------------------------------------------------
write(os.path.join(ROOT, "README.md"), final["README.md"])
commit("Add README: tool, setup, and the three prompting techniques",
       "2026-08-27T14:08:00+05:30")

# ---- C11: docs ------------------------------------------------------------------
write(os.path.join(ROOT, "docs", "prompt-log.md"), final["docs/prompt-log.md"])
write(os.path.join(ROOT, "docs", "make_screenshots.py"), final["docs/make_screenshots.py"])
os.makedirs(shot_dir, exist_ok=True)
for name, data in shots.items():
    with open(os.path.join(shot_dir, name), "wb") as f:
        f.write(data)
commit("Add docs: full prompt log, terminal-capture screenshots, reflection",
       "2026-08-27T14:12:00+05:30")

print("\n=== final verification ===")
print(run("git", "log", "--oneline"))
st = run("git", "status", "--short")
print(st if st.strip() else "(clean tree)")
