# Empirical data directory

This directory contains schemas and metadata templates only. No country-level
observations are bundled in this initial ingestion release.

Before adding a series, define its construct; record provider, direct source URL,
retrieval date, unit, frequency, coverage, license/redistribution terms, and
transformations; preserve original series separately; and document revisions,
missingness, aggregation, exchange-rate conversion, and country/period mapping.

Distinguish Bitcoin asset ownership from payment/transaction use, settlement use,
and contract denomination. These are not interchangeable measures. Never label
illustrative or synthetic values as observed country data.

- panel_template.csv: minimum country-period panel contract.
- source_registry_template.csv: required provenance fields.

After placing a real dataset and completed source registry in a controlled data
directory, use bsmpm.data_io.write_provenance_manifest to generate a JSON
manifest. The manifest records SHA-256 hashes and structural summaries. It does
not prove source authenticity, licensing compliance, or measurement validity.
Do not commit restricted or personally identifiable data.
