import unittest
import pandas as pd

from sma.source_audit import validate_country_roster
from sma.data_io import validate_source_registry


class CountryRosterTests(unittest.TestCase):
    def test_imf_wp24_roster_counts_and_shared_ecb_shock(self):
        roster = pd.read_csv("data/country_roster.csv", dtype=str)
        summary = validate_country_roster(roster)
        self.assertEqual(summary["countries"], 29)
        self.assertEqual(summary["advanced_economies"], 21)
        self.assertEqual(summary["emerging_markets"], 8)
        self.assertEqual(summary["monetary_authorities"], 20)
        self.assertEqual(summary["shock_series"], 20)
        self.assertEqual(summary["shared_euro_area_markets"], 10)

    def test_source_catalog_obeys_registry_contract(self):
        catalog = pd.read_csv("data/source_catalog.csv", dtype=str)
        summary = validate_source_registry(catalog)
        self.assertEqual(summary["records"], 8)
        self.assertIn("policy_shock_identified", summary["variables"])
        self.assertIn("btc_exchange_volume_proxy", summary["variables"])

    def test_duplicate_iso3_rejected(self):
        roster = pd.read_csv("data/country_roster.csv", dtype=str)
        roster.loc[1, "iso3"] = roster.loc[0, "iso3"]
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_country_roster(roster)

    def test_invalid_group_rejected(self):
        roster = pd.read_csv("data/country_roster.csv", dtype=str)
        roster.loc[0, "imf_wp24_group"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "AE or EM"):
            validate_country_roster(roster)

    def test_bad_iso3_rejected(self):
        roster = pd.read_csv("data/country_roster.csv", dtype=str)
        roster.loc[0, "iso3"] = "AUS1"
        with self.assertRaisesRegex(ValueError, "three uppercase"):
            validate_country_roster(roster)


if __name__ == "__main__":
    unittest.main()
