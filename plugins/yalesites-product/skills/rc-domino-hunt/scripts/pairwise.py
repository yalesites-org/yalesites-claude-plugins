#!/usr/bin/env python3
"""Generate a small t-way covering set for the RC domino hunt.

Every combination of values for any `t` factors appears in at least one row,
which finds most configuration bugs in far fewer rows than the full product
(NIST: most failures need 1 or 2 interacting factors). Coverage always wins:
weights never add rows. Each factor's weights are scaled to 0..1 against its
largest weight (an unlisted value counts as 1), so raw fleet-usage counts of any
size are safe. They only break ties: which value fills a row when several cover
the same new tuples, which row is picked among equals, and the output order.

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


def _raw_weight(weights, factor, value):
    # JSON object keys are always strings, so match 768 against "768" too.
    table = weights.get(factor, {})
    return float(table.get(value, table.get(str(value), 1.0)))


def _normalize(factors, weights):
    """Scale each factor's weights to 0..1 against its largest one."""
    out = {}
    for name, values in factors.items():
        raw = {v: max(0.0, _raw_weight(weights, name, v)) for v in values}
        top = max(raw.values()) or 1.0
        out[name] = {v: w / top for v, w in raw.items()}
    return out


def _tuples(row, names, strength):
    for combo in itertools.combinations(names, strength):
        yield tuple((name, row[name]) for name in combo)


def generate(factors, strength=2, weights=None, seed=1, candidates=50):
    """Return a list of rows covering every `strength`-way value combination."""
    names = list(factors)
    if not names:
        return []
    for name in names:
        if not factors[name]:
            raise ValueError(f"factor {name!r} has no values")
    norm = _normalize(factors, weights or {})

    def _weight(name, value):
        return norm[name][value]
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
            key=lambda t: sum(_weight(f, v) for f, v in t),
        )
        best, best_score = None, None
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
                    # Compared as a tuple: coverage first, then weight, then a
                    # seeded coin flip so equal values do not always pick the same.
                    return (covered, _weight(name, value), rng.random())
                row[name] = max(factors[name], key=gain)
            new = sum(1 for t in _tuples(row, names, strength) if t in uncovered)
            score = (new, sum(_weight(n, row[n]) for n in names))
            if best_score is None or score > best_score:
                best, best_score = row, score
        rows.append(best)
        uncovered -= set(_tuples(best, names, strength))

    rows.sort(key=lambda r: -sum(_weight(n, r[n]) for n in names))
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
