#!/usr/bin/env python3
"""Generate a small t-way covering set for the RC domino hunt.

Every combination of values for any `t` factors appears in at least one row,
which finds most configuration bugs in far fewer rows than the full product
(NIST: most failures need 1 or 2 interacting factors). Weights push common
real-world values (from the portfolio crawl) into more rows, and they decide
which row is picked when several rows cover the same new tuples.

Input is JSON on stdin or a file:

    {"factors": {"theme": ["one", "two", "three"],
                 "color": ["default", "blue", "gray"],
                 "region": ["1col", "50/50", "33/33/33"]},
     "weights": {"theme": {"one": 120, "two": 40}},
     "strength": 2,
     "seed": 1}

Output is a JSON list of rows (dicts), most-weighted first.

No third-party packages and no installs, so it runs on a drain night.
"""

import itertools
import json
import random
import sys


def _weight(weights, factor, value):
    # JSON object keys are always strings, so match 768 against "768" too.
    table = weights.get(factor, {})
    return float(table.get(value, table.get(str(value), 1.0)))


def _tuples(row, names, strength):
    for combo in itertools.combinations(names, strength):
        yield tuple((name, row[name]) for name in combo)


def generate(factors, strength=2, weights=None, seed=1, candidates=50):
    """Return a list of rows covering every `strength`-way value combination."""
    weights = weights or {}
    names = list(factors)
    if not names:
        return []
    for name in names:
        if not factors[name]:
            raise ValueError(f"factor {name!r} has no values")
    strength = max(1, min(strength, len(names)))

    uncovered = set()
    for combo in itertools.combinations(names, strength):
        for values in itertools.product(*(factors[n] for n in combo)):
            uncovered.add(tuple(zip(combo, values)))

    rng = random.Random(seed)
    rows = []
    while uncovered:
        # Seed each candidate from one uncovered tuple, so every pass makes progress.
        target = max(
            sorted(uncovered, key=repr),
            key=lambda t: sum(_weight(weights, f, v) for f, v in t),
        )
        best, best_score = None, -1.0
        for _ in range(candidates):
            row = dict(target)
            for name in rng.sample(names, len(names)):
                if name in row:
                    continue
                # Greedy: pick the value that covers the most new tuples so far.
                def gain(value):
                    trial = dict(row, **{name: value})
                    covered = sum(
                        1
                        for t in uncovered
                        if all(trial.get(f) == v for f, v in t)
                    )
                    return covered * 1000 + _weight(weights, name, value) + rng.random()
                row[name] = max(factors[name], key=gain)
            new = sum(1 for t in _tuples(row, names, strength) if t in uncovered)
            score = new * 1000 + sum(_weight(weights, n, row[n]) for n in names)
            if score > best_score:
                best, best_score = row, score
        rows.append(best)
        uncovered -= set(_tuples(best, names, strength))

    rows.sort(key=lambda r: -sum(_weight(weights, n, r[n]) for n in names))
    return [{n: r[n] for n in names} for r in rows]


def main(argv):
    src = open(argv[1]) if len(argv) > 1 else sys.stdin
    spec = json.load(src)
    rows = generate(
        spec["factors"],
        strength=spec.get("strength", 2),
        weights=spec.get("weights"),
        seed=spec.get("seed", 1),
    )
    json.dump(rows, sys.stdout, indent=2)
    sys.stdout.write("\n")


if __name__ == "__main__":
    main(sys.argv)
