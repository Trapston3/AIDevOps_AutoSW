"""Core splitting logic for the expense splitter.

This module contains all the functions and classes for splitting shared
expenses among a group of people.  It was written incrementally with the
help of an agentic AI coding assistant, applying three prompting
techniques (Zero-shot, Few-shot, Chain-of-thought) at different stages.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from decimal import Decimal, ROUND_HALF_EVEN, InvalidOperation
from typing import Dict, Iterable, List, Tuple

CENT = Decimal("0.01")


@dataclass
class Splitter:
    """Tracks expenses and computes who owes whom.

    Attributes
    ----------
    members : List[str]
        The people participating in the split.
    _balances : Dict[str, Decimal]
        Running net balance for each member (positive = owed money back).
    """

    members: List[str]
    _balances: Dict[str, Decimal] = field(default_factory=dict)

    def __post_init__(self) -> None:
        validate_members(self.members)
        self._balances = {m: Decimal("0") for m in self.members}

    def add_expense(self, payer: str, amount: Decimal, payees: Iterable[str]) -> None:
        """Record an expense paid by ``payer`` on behalf of ``payees``.

        The expense is split equally among ``payees``.
        """
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

        # split_evenly guarantees the shares sum exactly to amount (the
        # last share absorbs any rounding remainder), so we can debit each
        # payee and credit the payer directly.
        shares = split_evenly(amount, len(payees))
        for p, share in zip(payees, shares):
            self._balances[payer] += share
            self._balances[p] -= share


def validate_members(members: Iterable[str]) -> None:
    """Raise ``ValueError`` unless ``members`` is a non-empty collection of
    unique, non-blank names."""
    names = list(members)
    if len(names) == 0:
        raise ValueError("at least one member is required")
    if any(not isinstance(n, str) or not n.strip() for n in names):
        raise ValueError("member names must be non-empty strings")
    if len(set(names)) != len(names):
        raise ValueError("member names must be unique")


def _as_decimal(value) -> Decimal:
    """Coerce ``value`` to a ``Decimal``, rejecting NaN/infinity."""
    try:
        d = Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise ValueError(f"not a valid amount: {value!r}") from exc
    if not d.is_finite():
        raise ValueError(f"amount must be finite: {value!r}")
    return d


def split_evenly(amount: Decimal, n: int) -> List[Decimal]:
    """Split ``amount`` into ``n`` equal shares in cents.

    Each share is quantized to a cent with banker's rounding; the last
    share absorbs any rounding remainder so the returned shares always
    sum exactly to ``amount``.
    """
    amount = _as_decimal(amount)
    if n <= 0:
        raise ValueError("number of shares must be positive")
    raw = amount / n
    share = raw.quantize(CENT, rounding=ROUND_HALF_EVEN)
    # Give the leftover to the last share so shares always sum to amount.
    shares = [share] * (n - 1)
    shares.append(amount - share * (n - 1))
    return shares


def parse_expense_line(line: str) -> Tuple[str, Decimal, List[str]]:
    """Parse a single expense line of the form ``"payer amount p1 p2 ..."``.

    Returns ``(payer, amount, payees)``.
    """
    parts = line.strip().split()
    if len(parts) < 3:
        raise ValueError(f"line must be 'payer amount payee...': {line!r}")
    payer = parts[0]
    amount = _as_decimal(parts[1])
    payees = parts[2:]
    return payer, amount, payees


def compute_balances(expenses: Iterable[Tuple[str, Decimal, Iterable[str]]]) -> Dict[str, Decimal]:
    """Compute net balances from a list of ``(payer, amount, payees)`` rows."""
    members: List[str] = []
    for payer, _, payees in expenses:
        members.append(payer)
        members.extend(payees)
    # preserve first-seen order, deduplicated
    seen: List[str] = []
    for m in members:
        if m not in seen:
            seen.append(m)

    sp = Splitter(seen)
    for payer, amount, payees in expenses:
        sp.add_expense(payer, amount, payees)
    return sp._balances


def simplify_debts(balances: Dict[str, Decimal]) -> List[Tuple[str, str, Decimal]]:
    """Turn a net-balance map into the minimal list of cash transfers."""
    creditors = [(name, amt) for name, amt in balances.items() if amt > 0]
    debtors = [(name, -amt) for name, amt in balances.items() if amt < 0]
    creditors.sort(key=lambda x: -x[1])
    debtors.sort(key=lambda x: -x[1])
    transfers: List[Tuple[str, str, Decimal]] = []
    i = j = 0
    while i < len(debtors) and j < len(creditors):
        debtor, owed = debtors[i]
        creditor, due = creditors[j]
        amount = min(owed, due).quantize(CENT, rounding=ROUND_HALF_EVEN)
        transfers.append((debtor, creditor, amount))
        owed -= amount
        due -= amount
        if owed <= 0:
            i += 1
        else:
            debtors[i] = (debtor, owed)
        if due <= 0:
            j += 1
        else:
            creditors[j] = (creditor, due)
    return transfers
