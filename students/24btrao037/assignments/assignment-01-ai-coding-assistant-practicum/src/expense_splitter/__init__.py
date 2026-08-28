"""Expense splitter: split shared expenses fairly among a group.

A small library used as the basis for Assignment 1 (AI Coding Assistant
Practicum) — demonstrating Zero-shot, Few-shot, and Chain-of-thought
prompting techniques with an agentic AI coding assistant.
"""

from .splitter import (
    Splitter,
    split_evenly,
    parse_expense_line,
    compute_balances,
    simplify_debts,
    validate_members,
)

__all__ = [
    "Splitter",
    "split_evenly",
    "parse_expense_line",
    "compute_balances",
    "simplify_debts",
    "validate_members",
]

__version__ = "0.1.0"
