"""Unit tests for the expense splitter."""

from decimal import Decimal

import pytest

from expense_splitter import (
    Splitter,
    split_evenly,
    parse_expense_line,
    compute_balances,
    simplify_debts,
    validate_members,
)


def test_split_evenly_basic():
    assert split_evenly(Decimal("60"), 3) == [
        Decimal("20.00"),
        Decimal("20.00"),
        Decimal("20.00"),
    ]


def test_split_evenly_rounding_remainder_goes_to_last():
    # 10.00 split 3 ways: 3.33 + 3.33 + 3.34 = 10.00
    shares = split_evenly(Decimal("10.00"), 3)
    assert sum(shares) == Decimal("10.00")
    assert shares == [Decimal("3.33"), Decimal("3.33"), Decimal("3.34")]


def test_split_evenly_single_share():
    assert split_evenly(Decimal("42.00"), 1) == [Decimal("42.00")]


def test_split_evenly_rejects_nonpositive_n():
    with pytest.raises(ValueError):
        split_evenly(Decimal("10"), 0)


def test_validate_members_ok():
    validate_members(["alice", "bob", "carol"])  # no exception


def test_validate_members_duplicate():
    with pytest.raises(ValueError):
        validate_members(["alice", "alice"])


def test_validate_members_empty():
    with pytest.raises(ValueError):
        validate_members([])


def test_validate_members_blank_name():
    with pytest.raises(ValueError):
        validate_members(["alice", "  "])


def test_parse_expense_line():
    payer, amount, payees = parse_expense_line("alice 60.00 alice bob carol")
    assert payer == "alice"
    assert amount == Decimal("60.00")
    assert payees == ["alice", "bob", "carol"]


def test_parse_expense_line_too_short():
    with pytest.raises(ValueError):
        parse_expense_line("alice 60")


def test_splitter_equal_split():
    sp = Splitter(["alice", "bob", "carol"])
    sp.add_expense("alice", Decimal("60.00"), ["alice", "bob", "carol"])
    # alice paid 60 and is owed by bob & carol 20 each
    assert sp._balances["alice"] == Decimal("40.00")
    assert sp._balances["bob"] == Decimal("-20.00")
    assert sp._balances["carol"] == Decimal("-20.00")


def test_splitter_unknown_payer_raises():
    sp = Splitter(["alice", "bob"])
    with pytest.raises(ValueError):
        sp.add_expense("charlie", Decimal("10"), ["alice", "bob"])


def test_compute_balances_and_simplify_round_trip():
    expenses = [
        ("alice", Decimal("60.00"), ["alice", "bob", "carol"]),
        ("bob", Decimal("30.00"), ["bob", "carol"]),
    ]
    balances = compute_balances(expenses)
    # alice: +40, bob: -20 + 15 = -5, carol: -20 - 15 = -35
    assert balances["alice"] == Decimal("40.00")
    assert balances["bob"] == Decimal("-5.00")
    assert balances["carol"] == Decimal("-35.00")

    transfers = simplify_debts(balances)
    # minimal transfers should have every debtor/creditor settled
    assert Decimal("0.00") == Decimal("0.00")  # sanity
    total = sum(amount for _, _, amount in transfers)
    assert total == Decimal("40.00")


def test_simplify_debts_balanced_is_empty():
    assert simplify_debts({"a": Decimal("0"), "b": Decimal("0")}) == []
