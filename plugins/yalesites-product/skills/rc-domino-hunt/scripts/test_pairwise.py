#!/usr/bin/env python3
import itertools
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from pairwise import generate  # noqa: E402


FACTORS = {
    "theme": ["one", "two", "three", "four", "five"],
    "color": ["default", "one", "two", "three"],
    "region": ["1col", "50/50", "33/33/33", "sidebar"],
    "width": [360, 768, 1280],
}


def covered(rows, factors, strength):
    names = list(factors)
    missing = []
    for combo in itertools.combinations(names, strength):
        for values in itertools.product(*(factors[n] for n in combo)):
            if not any(all(r[n] == v for n, v in zip(combo, values)) for r in rows):
                missing.append(tuple(zip(combo, values)))
    return missing


class PairwiseTest(unittest.TestCase):
    def test_covers_every_pair(self):
        rows = generate(FACTORS, strength=2)
        self.assertEqual(covered(rows, FACTORS, 2), [])

    def test_far_smaller_than_full_product(self):
        rows = generate(FACTORS, strength=2)
        full = 5 * 4 * 4 * 3
        self.assertLess(len(rows), full / 4)

    def test_covers_every_triple_at_strength_three(self):
        rows = generate(FACTORS, strength=3)
        self.assertEqual(covered(rows, FACTORS, 3), [])

    def test_rows_use_only_known_values(self):
        for row in generate(FACTORS):
            self.assertEqual(set(row), set(FACTORS))
            for name, value in row.items():
                self.assertIn(value, FACTORS[name])

    def test_heaviest_row_comes_first(self):
        weights = {"theme": {"three": 500}}
        rows = generate(FACTORS, weights=weights)
        self.assertEqual(rows[0]["theme"], "three")

    def test_numeric_values_match_string_weight_keys(self):
        rows = generate(FACTORS, weights={"width": {"768": 500}})
        self.assertEqual(rows[0]["width"], 768)

    def test_mixed_value_types_do_not_crash(self):
        rows = generate({"a": [1, "x"], "b": ["y", 2]})
        self.assertEqual(covered(rows, {"a": [1, "x"], "b": ["y", 2]}, 2), [])

    def test_same_seed_same_rows(self):
        self.assertEqual(generate(FACTORS, seed=7), generate(FACTORS, seed=7))

    def test_strength_above_factor_count_is_clamped(self):
        rows = generate({"a": [1, 2], "b": [3]}, strength=5)
        self.assertEqual(covered(rows, {"a": [1, 2], "b": [3]}, 2), [])

    def test_empty_factor_is_an_error(self):
        with self.assertRaises(ValueError):
            generate({"a": [1], "b": []})


if __name__ == "__main__":
    unittest.main()
