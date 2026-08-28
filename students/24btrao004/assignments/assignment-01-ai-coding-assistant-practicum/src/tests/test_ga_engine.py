"""Unit tests for the existing genetic-algorithm engine (pre-feature baseline)."""

import random

import numpy as np
import pytest

from ga_engine import MUTATION_RATE, POPULATION_SIZE, create_population, evolve


def test_create_population_shape():
    """Population has the requested number of individuals and gene length."""
    pop = create_population(size=12, length=7)
    assert len(pop) == 12
    assert all(len(chrom) == 7 for chrom in pop)


def test_create_population_is_binary():
    """Every gene is either 0 or 1."""
    pop = create_population(size=10, length=20)
    for chrom in pop:
        assert set(chrom).issubset({0, 1})


def test_create_population_not_all_identical():
    """Random initialisation should not collapse to a single chromosome."""
    np.random.seed(0)
    pop = create_population(size=15, length=30)
    unique = {tuple(chrom) for chrom in pop}
    assert len(unique) > 1


def _counting_fitness(chromosome):
    """Fitness = number of selected features (deterministic)."""
    return float(sum(chromosome))


def test_evolve_returns_valid_structure():
    """evolve returns (best_chromosome, best_fitness, final_population)."""
    np.random.seed(1)
    random.seed(1)
    pop = create_population(size=8, length=6)
    best_chrom, best_fit, final_pop = evolve(
        pop, generations=2, fitness_fn=_counting_fitness, population_size=8
    )
    assert len(best_chrom) == 6
    assert isinstance(best_fit, float)
    assert len(final_pop) == 8


def test_evolve_best_is_at_least_as_good_as_start():
    """The tracked best must never be worse than the initial best."""
    np.random.seed(2)
    random.seed(2)
    pop = create_population(size=10, length=8)
    initial_best = max(_counting_fitness(c) for c in pop)
    _, best_fit, _ = evolve(
        pop, generations=3, fitness_fn=_counting_fitness, population_size=10
    )
    assert best_fit >= initial_best


def test_evolve_improves_on_counting_fitness():
    """Under a monotone fitness, a few generations should reach high scores."""
    np.random.seed(3)
    random.seed(3)
    pop = create_population(size=20, length=10)
    _, best_fit, _ = evolve(
        pop, generations=6, fitness_fn=_counting_fitness, population_size=20
    )
    # With 10 genes and selection pressure, best should select most features.
    assert best_fit >= 7.0


def test_zero_generations_raises():
    """generations=0 is a caller error and is rejected with a ValueError."""
    pop = create_population(size=4, length=3)
    with pytest.raises(ValueError):
        evolve(pop, generations=0, fitness_fn=_counting_fitness)
