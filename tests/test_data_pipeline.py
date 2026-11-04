import json
import tempfile
import unittest
from pathlib import Path

import pandas as pd

from bsmpm.data_pipeline import (
    load_documented_csv, merge_country_period_sources,
    write_acquisition_manifest,
)


class DataPipelineTests(unittest.TestCase):
    def test_load_and_hash_documented_csv(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rates.csv"
            pd.DataFrame({"iso3": ["IND"], "period": ["2025Q1"], "rate": [6.5]}).to_csv(path, index=False)
            frame, record = load_documented_csv(
                path, source_id="RBI-1", source_name="Example source",
                source_url="https://example.org/data", access_date="2026-11-04",
                license_status="review required", required_columns=["iso3", "period", "rate"],
            )
            self.assertEqual(len(frame), 1)
            self.assertEqual(len(record["sha256"]), 64)
            manifest = write_acquisition_manifest([record], Path(tmp) / "manifest.json")
            payload = json.loads(manifest.read_text())
            self.assertEqual(payload["source_count"], 1)

    def test_merge_requires_unique_keys_and_preserves_frequency(self):
        left = pd.DataFrame({"iso3": ["IND"], "period": ["2025Q1"], "rate": [6.5]})
        right = pd.DataFrame({"iso3": ["IND"], "period": ["2025Q1"], "inflation": [4.2]})
        result = merge_country_period_sources({"rates": left, "prices": right})
        self.assertEqual(result.loc[0, "inflation"], 4.2)
        duplicate = pd.concat([right, right], ignore_index=True)
        with self.assertRaises(ValueError):
            merge_country_period_sources({"rates": left, "prices": duplicate})

    def test_rejects_invalid_source_metadata(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rates.csv"
            pd.DataFrame({"iso3": ["IND"], "period": ["2025Q1"], "rate": [6.5]}).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "ISO YYYY-MM-DD"):
                load_documented_csv(
                    path, source_id="RBI-1", source_name="Example",
                    source_url="https://example.org/data", access_date="04-11-2026",
                    license_status="review required", required_columns=["iso3", "period", "rate"],
                )

    def test_rejects_empty_required_columns(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "rates.csv"
            pd.DataFrame({"rate": [6.5]}).to_csv(path, index=False)
            with self.assertRaisesRegex(ValueError, "required_columns"):
                load_documented_csv(
                    path, source_id="RBI-1", source_name="Example",
                    source_url="https://example.org/data", access_date="2026-11-04",
                    license_status="review required", required_columns=[],
                )

    def test_rejects_overlapping_columns(self):
        a = pd.DataFrame({"iso3": ["IND"], "period": ["Q1"], "value": [1]})
        b = pd.DataFrame({"iso3": ["IND"], "period": ["Q1"], "value": [2]})
        with self.assertRaises(ValueError):
            merge_country_period_sources({"a": a, "b": b})


if __name__ == "__main__":
    unittest.main()
