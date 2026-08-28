"""Balance netting: compute the minimal set of transfers settling a group.

Given per-member signed balances (positive = the group owes them, negative =
they owe the group), produce the shortest list of direct debtor-to-creditor
transfers that clears every balance. Money never routes through an
intermediary, so the result contains at most ``D + C - 1`` transfers for
``D`` debtors and ``C`` creditors.
"""

from dataclasses import dataclass
from decimal import ROUND_HALF_UP, Decimal


@dataclass
class Settlement:
    """One direct payment between two members.

    Args:
        from_: Name of the member who pays (had a negative balance).
        to: Name of the member who receives (had a positive balance).
        amount: Transfer size, rounded to 2 decimal places.
    """

    from_: str
    to: str
    amount: float


# Tolerance for treating a remaining balance as fully settled.
_EPS = 1e-9
# Balances smaller than half a cent cannot fund any 2dp transfer.
_DUST_THRESHOLD = 0.005


def _round_to_cents(value: float) -> float:
    """Round ``value`` to 2 decimal places, halves away from zero.

    Built-in ``round()`` uses round-half-to-even on the *exact binary*
    value, and values like ``1.005`` are stored as slightly less
    (1.00499999999989...), so it snaps to ``1.0``. Converting via
    ``Decimal(str(value))`` rounds the decimal literal a human expects,
    with ROUND_HALF_UP giving conventional money rounding.

    Args:
        value: Monetary amount to round.

    Returns:
        Value rounded to 2 decimal places as a float.
    """
    return float(Decimal(str(value)).quantize(Decimal("0.01"), ROUND_HALF_UP))


def compute_settlement(balances: dict[str, float]) -> list[Settlement]:
    """Compute the minimal list of transfers clearing all balances.

    Uses greedy largest-debtor-to-largest-creditor matching: each transfer
    fully settles at least one participant, so the output never exceeds
    ``D + C - 1`` transfers and never routes money through intermediaries.

    Args:
        balances: Maps member name to signed balance. Positive means the
            group owes that member; negative means they owe the group.
            Entries should sum to approximately zero (float tolerance).

    Returns:
        Settlement records sorted greedily, every ``amount`` rounded to
        2 decimal places. Empty list when nobody owes anything.
    """
    debtors: list[tuple[str, float]] = []
    creditors: list[tuple[str, float]] = []

    for name, balance in balances.items():
        if abs(balance) < _DUST_THRESHOLD:
            continue
        if balance < 0:
            debtors.append((name, -balance))
        else:
            creditors.append((name, balance))

    # Largest obligations first so big debts pair with big credits.
    debtors.sort(key=lambda entry: entry[1], reverse=True)
    creditors.sort(key=lambda entry: entry[1], reverse=True)

    settlements: list[Settlement] = []
    d_idx, c_idx = 0, 0

    while d_idx < len(debtors) and c_idx < len(creditors):
        debtor_name, debt_left = debtors[d_idx]
        creditor_name, credit_left = creditors[c_idx]

        amount = _round_to_cents(min(debt_left, credit_left))
        if amount > 0:
            settlements.append(
                Settlement(from_=debtor_name, to=creditor_name, amount=amount)
            )

        debtors[d_idx] = (debtor_name, debt_left - min(debt_left, credit_left))
        creditors[c_idx] = (
            creditor_name,
            credit_left - min(debt_left, credit_left),
        )

        # Advance whichever side was just fully settled.
        if debtors[d_idx][1] <= _EPS:
            d_idx += 1
        if creditors[c_idx][1] <= _EPS:
            c_idx += 1

    return settlements
