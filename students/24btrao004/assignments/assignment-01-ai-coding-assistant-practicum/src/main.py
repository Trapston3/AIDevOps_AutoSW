"""Entry point for the Evolutionary Feature Selector.

Runs three trials on the breast cancer dataset:
  1. Baseline — all features, no evolution.
  2. Midpoint — 5 generations of genetic-algorithm feature selection.
  3. Apex    — 10 additional generations (15 total).
"""

import sys
import warnings
from functools import partial

import numpy as np
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score

from fitness import evaluate_fitness, load_dataset
from ga_engine import ELITE_COUNT, POPULATION_SIZE, create_population, evolve


def main() -> None:
    # Ensure emoji / Unicode prints cleanly on Windows cp1252 consoles
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

    warnings.filterwarnings("ignore")

    print("🚀 INITIALIZING EVOLUTIONARY FEATURE SELECTOR...")
    print("-" * 50)

    # ── Load dataset ────────────────────────────────────
    X_train, X_test, y_train, y_test, total_features = load_dataset()
    print(f"Dataset Loaded: {total_features} total features available.")
    print(f"Elitism: top {ELITE_COUNT} chromosomes preserved each generation.")
    print("-" * 50)

    # ── Trial 1: Baseline (Generation 0) ────────────────
    print("▶ TRIAL 1: BASELINE (No Evolution)")
    baseline_model = RandomForestClassifier(random_state=42)
    baseline_model.fit(X_train, y_train)
    baseline_preds = baseline_model.predict(X_test)
    trial_1_accuracy = accuracy_score(y_test, baseline_preds) * 100

    print(f"Features Used: {total_features} / {total_features}")
    print(f"Baseline Accuracy: {trial_1_accuracy:.2f}%\n")

    # ── Bind the fitness function to the current split ──
    fitness_fn = partial(
        evaluate_fitness,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
    )

    # ── Initialise population ───────────────────────────
    current_population = create_population(POPULATION_SIZE, total_features)

    # ── Trial 2: Midpoint Evolution (Gen 5) ─────────────
    print("▶ TRIAL 2: MIDPOINT EVOLUTION (5 Generations)")
    best_chrom_5, trial_2_accuracy, current_population = evolve(
        current_population,
        generations=5,
        fitness_fn=fitness_fn,
        elite_count=ELITE_COUNT,
    )
    features_used_5 = int(np.sum(best_chrom_5))

    print(f"Features Retained: {features_used_5} / {total_features}")
    print(f"Midpoint Accuracy: {trial_2_accuracy:.2f}%\n")

    # ── Trial 3: Apex Evolution (Gen 15) ────────────────
    print("▶ TRIAL 3: APEX EVOLUTION (+10 Generations)")
    best_chrom_15, trial_3_accuracy, _ = evolve(
        current_population,
        generations=10,
        fitness_fn=fitness_fn,
        elite_count=ELITE_COUNT,
    )
    features_used_15 = int(np.sum(best_chrom_15))

    print(f"Features Retained: {features_used_15} / {total_features}")
    print(f"Apex Accuracy: {trial_3_accuracy:.2f}%\n")

    # ── Verification Dashboard ──────────────────────────
    print("=" * 50)
    print("🏆 FINAL EVOLUTION REPORT")
    print("=" * 50)

    if trial_3_accuracy > trial_1_accuracy:
        print("✅ EVOLUTION SUCCESSFUL!")
        print(
            f"The Genetic Algorithm improved accuracy from "
            f"{trial_1_accuracy:.2f}% to {trial_3_accuracy:.2f}%."
        )
        print(
            f"It achieved this while dropping "
            f"{total_features - features_used_15} unnecessary features!"
        )
    elif trial_3_accuracy == trial_1_accuracy:
        print("⚠️ EVOLUTION STAGNATED.")
        print(
            f"Accuracy remained at {trial_1_accuracy:.2f}%. However, it "
            f"optimised efficiency by dropping "
            f"{total_features - features_used_15} features."
        )
    else:
        print("❌ EVOLUTION FAILED.")
        print(
            "The model got trapped in a local minimum. "
            "Increase population size or mutation rate."
        )


if __name__ == "__main__":
    main()
