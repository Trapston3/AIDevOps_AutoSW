"""Regression tests for the balance-netting rounding behavior."""

from tabsplit.netting import compute_settlement


def test_settlement_amount_is_rounded_to_cents():
    result = compute_settlement({"A": -1.005, "B": 1.005})
    assert len(result) == 1
    assert result[0].amount == 1.01


def test_empty_balances_returns_empty_list():
    """An empty balance map produces no transfers.

    Returns:
        ``None``; assertions verify the settlement is empty.
    """
    assert compute_settlement({}) == []


def test_all_zero_balances_returns_empty_list():
    """Members with zero balances owe nothing and are owed nothing.

    Returns:
        ``None``; assertions verify the settlement is empty.
    """
    result = compute_settlement({"A": 0.0, "B": 0.0, "C": 0.0})
    assert result == []


def test_unequal_debtor_and_creditor_transfer_smaller_amount():
    """A single debtor-creditor pair settles at the smaller magnitude.

    The debtor owes 30.00 while the creditor is owed 50.00, so exactly
    one transfer of 30.00 flows from debtor to creditor.

    Returns:
        ``None``; assertions verify one correctly directed transfer.
    """
    result = compute_settlement({"Debtor": -30.0, "Creditor": 50.0})
    assert len(result) == 1
    assert result[0].from_ == "Debtor"
    assert result[0].to == "Creditor"
    assert result[0].amount == 30.0


def test_three_debtors_one_creditor_conserves_total():
    """Transfers paid by three debtors sum to the creditor's credit.

    Total conserved: the sum of transfer amounts must equal the sum of
    positive balances (70.00 here).

    Returns:
        ``None``; assertions verify the conservation identity.
    """
    balances = {"D1": -10.0, "D2": -20.0, "D3": -40.0, "Cred": 70.0}
    result = compute_settlement(balances)

    transferred = sum(s.amount for s in result)
    total_credit = sum(v for v in balances.values() if v > 0)
    assert transferred == total_credit == 70.0
    assert {s.to for s in result} == {"Cred"}


def test_every_amount_is_rounded_to_two_decimals():
    """All transfer amounts carry at most two decimal places.

    Uses balances with sub-cent remainders so unrounded greedy matching
    would leak extra precision into the output.

    Returns:
        ``None``; assertions verify every amount equals its 2dp rounding.
    """
    result = compute_settlement(
        {"A": -10.5555, "B": -5.1234, "C": 15.6789}
    )
    assert result, "expected at least one transfer"
    for settlement in result:
        assert settlement.amount == round(settlement.amount, 2)
