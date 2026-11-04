import unittest

from sma.structural import (
    MonetaryState, StructuralParameters, policy_loss, transition_one_period,
)


class StructuralScaffoldTests(unittest.TestCase):
    def setUp(self):
        self.state = MonetaryState(
            inflation_gap=0.02, output_gap=-0.01, exchange_rate_gap=0.03,
            bitcoin_use_share=0.2, sdr_exposure=0.4,
        )

    def test_transition_is_deterministic_and_finite(self):
        params = StructuralParameters(bitcoin_transmission_insulation=0.5)
        result = transition_one_period(self.state, 0.01, params)
        self.assertAlmostEqual(result.effective_policy_shock, 0.009)
        self.assertTrue(0 <= result.state.bitcoin_use_share <= 1)
        self.assertGreaterEqual(result.policy_loss, 0)

    def test_zero_shock_still_allows_state_persistence(self):
        result = transition_one_period(self.state, 0.0)
        self.assertNotEqual(result.state.inflation_gap, 0.0)

    def test_policy_loss_is_nonnegative(self):
        self.assertGreaterEqual(policy_loss(self.state, StructuralParameters()), 0)

    def test_invalid_share_rejected(self):
        bad = MonetaryState(0, 0, 0, 1.2, 0.1)
        with self.assertRaises(ValueError):
            transition_one_period(bad, 0.1)

    def test_negative_penalty_weight_rejected(self):
        with self.assertRaises(ValueError):
            policy_loss(self.state, StructuralParameters(sdr_penalty_weight=-1))


if __name__ == "__main__":
    unittest.main()
