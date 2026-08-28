"""Unit tests for the elitism feature added to the genetic-algorithm engine."""

import random

import numpy as np
import pytest

from ga_engine import create_population, evolve


def _counting_fitness(chromosome):
    """Fitness = number of selected features (deterministic)."""
    return float(sum(chromosome))


def _distinct_population():
    """Four chromosomes with strictly distinct counting-fitness values."""
    return [
        [1, 1, 1, 1],  # fitness 4 (fittest)
        [1, 1, 1, 0],  # fitness 3
        [1, 1, 0, 0],  # fitness 2
        [1, 0, 0, 0],  # fitness 1
    ]


def test_elites_appear_unchanged_in_next_generation():
    """The fittest chromosomes survive into the next generation verbatim."""
    pop = _distinct_population()
    _, _, final_pop = evolve(
        pop,
        generations=1,
        fitness_fn=_counting_fitness,
        population_size=4,
        mutation_rate=0.0,
        elite_count=2,
    )
    as_tuples = {tuple(chrom) for chrom in final_pop}
    assert (1, 1, 1, 1) in as_tuples
    assert (1, 1, 1, 0) in as_tuples


def test_elites_survive_maximum_mutation():
    """Even with mutation_rate=1.0 the elites are copied, not mutated."""
    random.seed(7)
    pop = _distinct_population()
    _, _, final_pop = evolve(
        pop,
        generations=1,
        fitness_fn=_counting_fitness,
        population_size=4,
        mutation_rate=1.0,
        elite_count=2,
    )
    as_tuples = {tuple(chrom) for chrom in final_pop}
    assert (1, 1, 1, 1) in as_tuples
    assert (1, 1, 1, 0) in as_tuples


def test_best_fitness_never_drops_with_elitism():
    """With elitism on, the best fitness seen so far is monotone non-decreasing."""
    np.random.seed(4)
    random.seed(4)
    pop = create_population(size=12, length=8)
    best_so_far = 0.0
    for _ in range(5):
        _, best_fit, pop = evolve(
            pop,
            generations=1,
            fitness_fn=_counting_fitness,
            population_size=12,
            elite_count=2,
        )
        assert best_fit >= best_so_far
        best_so_far = best_fit


def test_elite_count_zero_matches_original_behaviour():
    """elite_count=0 disables elitism and still returns a valid population."""
    np.random.seed(5)
    random.seed(5)
    pop = create_population(size=8, length=6)
    best_chrom, best_fit, final_pop = evolve(
        pop,
        generations=2,
        fitness_fn=_counting_fitness,
        population_size=8,
        elite_count=0,
    )
    assert len(best_chrom) == 6
    assert isinstance(best_fit, float)
    assert len(final_pop) == 8


def test_negative_elite_count_raises():
    """A negative elite_count is rejected with a ValueError."""
    pop = _distinct_population()
    with pytest.raises(ValueError):
        evolve(
            pop,
            generations=1,
            fitness_fn=_counting_fitness,
            population_size=4,
            elite_count=-1,
        )


def test_elite_count_at_least_population_size_raises():
    """elite_count >= population_size leaves no room for offspring."""
    pop = _distinct_population()
    with pytest.raises(ValueError):
        evolve(
            pop,
            generations=1,
            fitness_fn=_counting_fitness,
            population_size=4,
            elite_count=4,
        )
