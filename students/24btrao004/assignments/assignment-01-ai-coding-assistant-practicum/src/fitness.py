"""Fitness evaluation module for evolutionary feature selection.

Encapsulates dataset loading and the fitness function used by the genetic
algorithm to score candidate feature subsets.
"""

import numpy as np
from sklearn.datasets import load_breast_cancer
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from sklearn.model_selection import train_test_split


def load_dataset(test_size: float = 0.3, random_state: int = 42):
    """Load the breast cancer dataset and return train/test splits.

    Parameters
    ----------
    test_size : float
        Fraction of samples reserved for the test set.
    random_state : int
        Seed for reproducible splits.

    Returns
    -------
    X_train, X_test, y_train, y_test : ndarray
        Training and testing feature matrices and label vectors.
    total_features : int
        Number of features in the dataset.
    """
    data = load_breast_cancer()
    X, y = data.data, data.target
    total_features = X.shape[1]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )
    return X_train, X_test, y_train, y_test, total_features


def evaluate_fitness(
    chromosome: list[int],
    X_train: np.ndarray,
    X_test: np.ndarray,
    y_train: np.ndarray,
    y_test: np.ndarray,
    random_state: int = 42,
) -> float:
    """Score a binary chromosome by training an RF on the selected features.

    Parameters
    ----------
    chromosome : list[int]
        Binary mask (1 = keep, 0 = drop) of length *total_features*.
    X_train, X_test : ndarray
        Full training and testing feature matrices.
    y_train, y_test : ndarray
        Training and testing labels.
    random_state : int
        Seed for the underlying RandomForestClassifier.

    Returns
    -------
    float
        Accuracy on the test set expressed as a percentage (0–100).
    """
    if np.sum(chromosome) == 0:
        return 0.0

    selected = [i for i, val in enumerate(chromosome) if val == 1]

    X_train_sub = X_train[:, selected]
    X_test_sub = X_test[:, selected]

    model = RandomForestClassifier(random_state=random_state)
    model.fit(X_train_sub, y_train)
    preds = model.predict(X_test_sub)

    return accuracy_score(y_test, preds) * 100
