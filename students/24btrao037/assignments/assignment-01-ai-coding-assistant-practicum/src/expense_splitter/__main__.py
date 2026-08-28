"""Command-line interface for the expense splitter."""

import sys
from decimal import Decimal

from .splitter import parse_expense_line, compute_balances, simplify_debts


def main(argv=None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    if not argv:
        _usage()
        return 2

    expenses = []
    try:
        for line in argv:
            expenses.append(parse_expense_line(line))
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    balances = compute_balances(expenses)
    transfers = simplify_debts(balances)

    for debtor, creditor, amount in transfers:
        print(f"{debtor} -> {creditor}: {amount:.2f}")
    return 0


def _usage() -> None:
    print(
        "usage: expense-splitter 'payer amount payee...' "
        "['payer amount payee...' ...]"
    )
    print("example: expense-splitter 'alice 60 alice bob carol' "
          "'bob 30 bob carol'")


if __name__ == "__main__":
    raise SystemExit(main())
