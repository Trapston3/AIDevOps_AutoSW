"""Core data model for recording and grouping shared expenses."""

from dataclasses import dataclass, field


@dataclass
class Expense:
    """Represent one expense with an amount, description, and participants."""

    description: str
    amount: float
    paid_by: str
    participants: list[str]

    def __post_init__(self) -> None:
        self.description = self.description.strip()
        self.paid_by = self.paid_by.strip()
        self.participants = [name.strip() for name in self.participants]

        if not self.description:
            raise ValueError("description cannot be empty")
        if self.amount <= 0:
            raise ValueError("amount must be greater than 0")
        if not self.paid_by:
            raise ValueError("paid_by cannot be empty")
        if not self.participants:
            raise ValueError("participants cannot be empty")
        if any(not name for name in self.participants):
            raise ValueError("participant names cannot be empty")

    def equal_shares(self) -> list[float]:
        """Return each participant's share so the amounts add up to the expense."""
        total_cents = round(self.amount * 100)
        count = len(self.participants)
        base_cents, extra_cents = divmod(total_cents, count)
        shares = []
        for index in range(count):
            cents = base_cents
            if index >= count - extra_cents:
                cents += 1
            shares.append(round(cents / 100, 2))
        return shares


@dataclass
class ExpenseSplitter:
    """Track recorded expenses for later listing and splitting."""

    expenses: list[Expense] = field(default_factory=list)

    def add_expense(self, expense: Expense) -> None:
        """Add one expense to the tracker."""
        self.expenses.append(expense)

    def total_amount(self) -> float:
        """Return the total value of all recorded expenses."""
        return sum(expense.amount for expense in self.expenses)

    def expenses_for_person(self, person: str) -> list[Expense]:
        """Return all expenses associated with the given person."""
        name = person.strip()
        return [
            expense
            for expense in self.expenses
            if expense.paid_by == name or name in expense.participants
        ]
