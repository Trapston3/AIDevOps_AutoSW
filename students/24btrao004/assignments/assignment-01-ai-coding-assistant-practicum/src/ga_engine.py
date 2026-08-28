"""Genetic Algorithm engine for binary feature selection.

Provides population initialisation, tournament-style selection, single-point
crossover, and bit-flip mutation.  The engine is dataset-agnostic — callers
inject a fitness function at evolution time.
"""

import random
from typing import Callable

import numpy as np

# ----- GA hyper-parameters (module-level defaults) -----
POPULATION_SIZE: int = 20
MUTATION_RATE: float = 0.1
ELITE_COUNT: int = 2


def create_population(size: int, length: int) -> list[list[int]]:
    """Create an initial random population of binary chromosomes.

    Parameters
    ----------
    size : int
        Number of individuals in the population.
    length : int
        Length of each chromosome (= number of features).

    Returns
    -------
    list[list[int]]
        A population of binary chromosomes.
    """
    return [np.random.randint(2, size=length).tolist() for _ in range(size)]


def evolve(
    population: list[list[int]],
    generations: int,
    fitness_fn: Callable[[list[int]], float],
    population_size: int = POPULATION_SIZE,
    mutation_rate: float = MUTATION_RATE,
    elite_count: int = ELITE_COUNT,
) -> tuple[list[int], float, list[list[int]]]:
    """Run the genetic algorithm for a fixed number of generations.

    Parameters
    ----------
    population : list[list[int]]
        Current population of binary chromosomes.
    generations : int
        Number of generations to evolve.
    fitness_fn : Callable[[list[int]], float]
        A function that accepts a chromosome and returns a fitness score.
    population_size : int
        Target population size for each generation.
    mutation_rate : float
        Per-gene probability of a bit-flip mutation.
    elite_count : int
        Number of the fittest chromosomes copied unchanged into the next
        generation (no crossover, no mutation).  ``0`` disables elitism
        and reproduces the original behaviour exactly.

    Returns
    -------
    best_chromosome : list[int]
        The highest-fitness chromosome observed across all generations.
    best_fitness : float
        Its fitness score.
    population : list[list[int]]
        The final generation (can be fed back into another ``evolve`` call).

    Raises
    ------
    ValueError
        If ``generations`` is less than 1, if ``elite_count`` is negative,
        or if ``elite_count`` is not strictly smaller than
        ``population_size``.
    """
    if generations < 1:
        raise ValueError(f"generations must be >= 1, got {generations}")
    if elite_count < 0:
        raise ValueError(f"elite_count must be >= 0, got {elite_count}")
    if elite_count >= population_size:
        raise ValueError(
            f"elite_count ({elite_count}) must be smaller than "
            f"population_size ({population_size})"
        )

    num_genes = len(population[0])
    best_chromosome: list[int] | None = None
    best_fitness: float = 0.0

    for _ in range(generations):
        # 1. Evaluate fitness
        fitness_scores = [fitness_fn(chrom) for chrom in population]

        # Track the global best
        max_fitness = max(fitness_scores)
        if max_fitness > best_fitness:
            best_fitness = max_fitness
            best_chromosome = population[fitness_scores.index(max_fitness)]

        # 2. Selection — keep top 50 %
        sorted_pop = [
            x
            for _, x in sorted(
                zip(fitness_scores, population), reverse=True
            )
        ]
        parents = sorted_pop[: population_size // 2]

        # 3. Elitism — copy the fittest chromosomes across unchanged
        elites = [list(chrom) for chrom in sorted_pop[:elite_count]]

        # 4. Crossover & mutation
        next_generation: list[list[int]] = list(elites)
        while len(next_generation) < population_size:
            p1 = random.choice(parents)
            p2 = random.choice(parents)

            # Single-point crossover
            crossover_point = random.randint(1, num_genes - 1)
            child = p1[:crossover_point] + p2[crossover_point:]

            # Bit-flip mutation
            for i in range(num_genes):
                if random.random() < mutation_rate:
                    child[i] = 1 - child[i]

            next_generation.append(child)

        population = next_generation

    return best_chromosome, best_fitness, population
