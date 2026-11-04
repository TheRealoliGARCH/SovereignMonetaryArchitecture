import json
from pathlib import Path
import tempfile
import unittest

import pandas as pd

from bsmpm.data_io import (
    build_provenance_manifest, load_country_panel, validate_empirical_dataset,
    validate_source_registry, write_provenance_manifest,
)


def sample_panel():
    return pd.DataFrame({
        "country": ["A", "A", "B", "B"],
        "period": ["2020Q1", "2020Q2", "2020Q1", "2020Q2"],
        "outcome": [1.2, 1.1, 0.9, 0.8],
        "policy_shock": [0.1, -0.1, 0.2, -0.2],
        "btc_use_share": [0.01, 0.02, 0.03, 0.04],
    })


def sample_registry():
    return pd.DataFrame([{
        "source_id": "SRC-001", "variable": "policy_shock",
        "provider": "Example statistical provider", "url": "https://example.org/series",
        "definition": "Documented policy surprise series", "unit": "percentage points",
        "frequency": "quarterly", "coverage": "2020Q1-2020Q2",
        "retrieval_date": "2026-11-04",
        "license": "Review provider terms before redistribution",
        "transformation": "None", "status": "metadata-example-not-an-observation",
    }])


class DataIngestionTests(unittest.TestCase):
    def test_valid_panel_summary(self):
        summary = validate_empirical_dataset(sample_panel())
        self.assertEqual(summary["rows"], 4)
        self.assertEqual(summary["countries"], 2)
        self.assertEqual(summary["periods"], 2)

    def test_missing_numeric_values_are_counted(self):
        frame = sample_panel()
        frame.loc[0, "outcome"] = float("nan")
        self.assertEqual(validate_empirical_dataset(frame)["missing_numeric"]["outcome"], 1)

    def test_duplicate_country_period_rejected(self):
        frame = sample_panel()
        frame.loc[1, "period"] = "2020Q1"
        with self.assertRaisesRegex(ValueError, "unique"):
            validate_empirical_dataset(frame)

    def test_out_of_range_use_share_rejected(self):
        frame = sample_panel()
        frame.loc[0, "btc_use_share"] = 1.2
        with self.assertRaisesRegex(ValueError, r"\[0, 1\]"):
            validate_empirical_dataset(frame)

    def test_nonnumeric_outcome_rejected(self):
        frame = sample_panel()
        frame.loc[0, "outcome"] = "not-a-number"
        with self.assertRaisesRegex(ValueError, "nonnumeric"):
            validate_empirical_dataset(frame)

    def test_valid_source_registry(self):
        summary = validate_source_registry(sample_registry())
        self.assertEqual(summary["records"], 1)
        self.assertIn("policy_shock", summary["variables"])

    def test_manifest_hashes_and_round_trip(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            dataset, registry, output = root / "panel.csv", root / "sources.csv", root / "manifest.json"
            sample_panel().to_csv(dataset, index=False)
            sample_registry().to_csv(registry, index=False)
            loaded, summary = load_country_panel(dataset)
            self.assertEqual(len(loaded), summary["rows"])
            manifest = build_provenance_manifest(
                dataset, source_registry_path=registry, metadata={"sample": "test-fixture"}
            )
            self.assertEqual(len(manifest["dataset"]["sha256"]), 64)
            written = write_provenance_manifest(
                dataset, source_registry_path=registry, output_path=output
            )
            self.assertTrue(output.is_file())
            self.assertEqual(json.loads(output.read_text())["manifest_version"], "1.0")
            self.assertEqual(written["dataset"]["rows"], 4)


if __name__ == "__main__":
    unittest.main()
