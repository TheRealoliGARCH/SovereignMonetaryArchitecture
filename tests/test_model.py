import math
import unittest

from bsmpm.model import (
    adoption_fixed_points,
    critical_adoption_linear,
    critical_adoption_quadratic,
    liquidity_shortfall,
    logistic,
    monetary_transmission_linear,
    monetary_transmission_nonlinear,
    seigniorage_proxy,
    welfare,
    welfare_optimum,
)


class TestTransmission(unittest.TestCase):
    def test_linear_endpoints(self):
        self.assertAlmostEqual(monetary_transmission_linear(0, 0.8, 0.1), 0.8)
        self.assertAlmostEqual(monetary_transmission_linear(1, 0.8, 0.1), 0.1)

    def test_linear_monotonicity(self):
        values = [monetary_transmission_linear(s, 0.8, 0.1) for s in (0, .2, .4, .6, .8, 1)]
        self.assertTrue(all(a >= b for a, b in zip(values, values[1:])))

    def test_invalid_share(self):
        with self.assertRaises(ValueError):
            monetary_transmission_linear(1.1, 0.8, 0.1)

    def test_nonlinear(self):
        self.assertAlmostEqual(monetary_transmission_nonlinear(.5, .8, .2, .4), .6)


class TestThresholds(unittest.TestCase):
    def test_linear_threshold(self):
        threshold = critical_adoption_linear(.8, .1, .3)
        self.assertAlmostEqual(threshold, .5)
        self.assertGreaterEqual(monetary_transmission_linear(threshold, .8, .1), .3)

    def test_quadratic_threshold(self):
        threshold = critical_adoption_quadratic(.8, .2, .4, .3)
        self.assertAlmostEqual(monetary_transmission_nonlinear(threshold, .8, .2, .4), .3)

    def test_infeasible_requirement(self):
        with self.assertRaises(ValueError):
            critical_adoption_linear(.5, .1, .6)


class TestAdoption(unittest.TestCase):
    def test_logistic_stability(self):
        self.assertAlmostEqual(logistic(0), .5)
        self.assertTrue(0 < logistic(1000) < 1)
        self.assertTrue(0 < logistic(-1000) < 1)

    def test_single_fixed_point_without_feedback(self):
        roots = adoption_fixed_points(0.0, 0.0)
        self.assertEqual(len(roots), 1)
        self.assertAlmostEqual(roots[0].share, .5, places=6)

    def test_multiple_fixed_points_possible(self):
        roots = adoption_fixed_points(-2.0, 8.0)
        self.assertGreaterEqual(len(roots), 2)
        self.assertTrue(all(0 <= r.share <= 1 for r in roots))


class TestOtherChannels(unittest.TestCase):
    def test_seigniorage_proxy(self):
        self.assertAlmostEqual(seigniorage_proxy(2.0, .5, .6), 1.4)

    def test_liquidity_shortfall(self):
        self.assertEqual(liquidity_shortfall(20, 8, 5), 7)
        self.assertEqual(liquidity_shortfall(5, 8, 1), 0)

    def test_welfare_and_optimum(self):
        optimum = welfare_optimum(.5, .7, .1, .9)
        self.assertAlmostEqual(optimum, .4 / 1.6)
        values = [welfare(s, .5, .7, .1, .9) for s in (0, optimum, 1)]
        self.assertEqual(max(values), values[1])


if __name__ == "__main__":
    unittest.main()
