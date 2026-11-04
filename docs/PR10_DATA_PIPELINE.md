# PR #10 — Reproducible empirical data pipeline

## Scope

This PR adds a provider-neutral local ingestion and assembly layer. It does not
scrape websites or bypass source access controls. Researchers acquire data
through official or licensed channels and supply local CSVs.

## Functions

- `load_documented_csv`: validates required columns and records source ID,
  source name, URL, access date, user-supplied license status, filename, row
  count, columns, and SHA-256 hash.
- `merge_country_period_sources`: performs validated one-to-one joins on
  explicit keys (ISO3 and period by default); rejects duplicate/missing keys
  and overlapping non-key fields.
- `write_acquisition_manifest`: writes a JSON provenance manifest.

## Frequency and legal safeguards

No temporal interpolation, imputation, or implicit frequency conversion is
performed. Event, daily, monthly, and quarterly sources should be prepared and
aggregated under their own documented conventions before merging. Hashes
identify files; they do not establish authenticity, construct validity, or
redistribution rights. License status is a researcher-supplied field and must
be reviewed independently.
