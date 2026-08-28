"""Shared pytest fixtures for the evolutionary feature selector test suite."""

import numpy as np
import pytest

from fitness import load_dataset


@pytest.fixture(scope="session")
def dataset():
    """Load the breast cancer split once for the whole test session.

    Returns
    -------
    tuple
        ``(X_train, X_test, y_train, y_test, total_features)``.
    """
    return load_dataset(test_size=0.3, random_state=42)


@pytest.fixture
def small_chromosome():
    """A short, deterministic binary chromosome for fast unit tests."""
    return [1, 0, 1, 1, 0, 0, 1, 0]
