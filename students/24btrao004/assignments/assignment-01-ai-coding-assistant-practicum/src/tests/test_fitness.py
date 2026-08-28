"""Unit tests for the fitness-evaluation module (pre-feature baseline)."""

import numpy as np
import pytest

from fitness import evaluate_fitness, load_dataset


def test_load_dataset_shapes(dataset):
    """Train/test matrices are consistent with the 30-feature dataset."""
    X_train, X_test, y_train, y_test, total_features = dataset
    assert total_features == 30
    assert X_train.shape[1] == 30
    assert X_test.shape[1] == 30
    assert X_train.shape[0] == y_train.shape[0]
    assert X_test.shape[0] == y_test.shape[0]


def test_load_dataset_labels_binary(dataset):
    """Breast-cancer labels are binary (malignant / benign)."""
    _, _, y_train, y_test, _ = dataset
    assert set(np.unique(y_train)).issubset({0, 1})
    assert set(np.unique(y_test)).issubset({0, 1})


def test_evaluate_fitness_returns_percentage(dataset):
    """A valid chromosome yields an accuracy in the 0-100 range."""
    X_train, X_test, y_train, y_test, total = dataset
    chrom = [1] * total
    score = evaluate_fitness(
        chrom, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test
    )
    assert 0.0 <= score <= 100.0


def test_evaluate_fitness_all_zero_is_zero(dataset):
    """An empty feature set is defined to score 0.0 (guard clause)."""
    X_train, X_test, y_train, y_test, total = dataset
    chrom = [0] * total
    score = evaluate_fitness(
        chrom, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test
    )
    assert score == 0.0


def test_evaluate_fitness_subset_is_deterministic(dataset):
    """The same chromosome scores identically across repeated calls."""
    X_train, X_test, y_train, y_test, total = dataset
    chrom = [i % 2 for i in range(total)]
    s1 = evaluate_fitness(
        chrom, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test
    )
    s2 = evaluate_fitness(
        chrom, X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test
    )
    assert s1 == s2
