"""Unit tests for the Expense Splitter data model."""

import pytest

from expense_splitter.models import Expense, ExpenseSplitter


def test_create_expense():
    expense = Expense(
        description="Dinner",
        amount=90.0,
        paid_by="Alice",
        participants=["Alice", "Bob", "Charlie"],
    )

    assert expense.description == "Dinner"
    assert expense.amount == 90.0
    assert expense.paid_by == "Alice"
    assert expense.participants == ["Alice", "Bob", "Charlie"]


def test_expense_strips_whitespace():
    expense = Expense(
        description="  Lunch  ",
        amount=30.0,
        paid_by="  Bob  ",
        participants=[" Alice ", " Bob "],
    )

    assert expense.description == "Lunch"
    assert expense.paid_by == "Bob"
    assert expense.participants == ["Alice", "Bob"]


def test_expense_rejects_empty_description():
    with pytest.raises(ValueError, match="description"):
        Expense(
            description="   ",
            amount=10.0,
            paid_by="Alice",
            participants=["Alice"],
        )


def test_expense_rejects_non_positive_amount():
    with pytest.raises(ValueError, match="amount"):
        Expense(
            description="Taxi",
            amount=0,
            paid_by="Alice",
            participants=["Alice", "Bob"],
        )


def test_expense_rejects_empty_participants():
    with pytest.raises(ValueError, match="participants"):
        Expense(
            description="Snacks",
            amount=12.0,
            paid_by="Alice",
            participants=[],
        )


def test_add_expense_to_splitter():
    splitter = ExpenseSplitter()
    expense = Expense(
        description="Groceries",
        amount=45.5,
        paid_by="Charlie",
        participants=["Alice", "Charlie"],
    )

    splitter.add_expense(expense)

    assert len(splitter.expenses) == 1
    assert splitter.expenses[0] is expense


def test_new_splitter_has_no_expenses():
    splitter = ExpenseSplitter()
    assert splitter.expenses == []


def test_total_amount_sums_recorded_expenses():
    splitter = ExpenseSplitter()
    splitter.add_expense(
        Expense(
            description="Dinner",
            amount=90.0,
            paid_by="Alice",
            participants=["Alice", "Bob"],
        )
    )
    splitter.add_expense(
        Expense(
            description="Taxi",
            amount=30.0,
            paid_by="Bob",
            participants=["Alice", "Bob"],
        )
    )

    assert splitter.total_amount() == 120.0


def test_total_amount_is_zero_when_empty():
    splitter = ExpenseSplitter()
    assert splitter.total_amount() == 0


def test_expenses_for_person_includes_payer_and_participants():
    splitter = ExpenseSplitter()
    dinner = Expense(
        description="Dinner",
        amount=90.0,
        paid_by="Alice",
        participants=["Alice", "Bob"],
    )
    taxi = Expense(
        description="Taxi",
        amount=30.0,
        paid_by="Charlie",
        participants=["Charlie", "Dana"],
    )
    snacks = Expense(
        description="Snacks",
        amount=12.0,
        paid_by="Bob",
        participants=["Alice", "Charlie"],
    )
    splitter.add_expense(dinner)
    splitter.add_expense(taxi)
    splitter.add_expense(snacks)

    assert splitter.expenses_for_person("Alice") == [dinner, snacks]
    assert splitter.expenses_for_person("Charlie") == [taxi, snacks]
    assert splitter.expenses_for_person("Dana") == [taxi]
    assert splitter.expenses_for_person("Eve") == []


def test_equal_shares_gives_remainder_cent_to_last_people():
    expense = Expense(
        description="Dinner",
        amount=100.0,
        paid_by="Alice",
        participants=["Alice", "Bob", "Charlie"],
    )

    shares = expense.equal_shares()

    assert shares == [33.33, 33.33, 33.34]
    assert round(sum(shares), 2) == 100.0


def test_equal_shares_always_add_up_to_the_expense():
    cases = [
        (100.0, 3),
        (10.0, 3),
        (0.01, 3),
        (0.02, 3),
        (99.99, 4),
        (50.0, 1),
        (1.0, 7),
    ]
    for amount, count in cases:
        participants = [f"Person{i}" for i in range(count)]
        expense = Expense(
            description="Split",
            amount=amount,
            paid_by=participants[0],
            participants=participants,
        )
        shares = expense.equal_shares()
        assert len(shares) == count
        assert round(sum(shares), 2) == round(amount, 2)
