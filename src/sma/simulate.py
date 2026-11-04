"""Run explicitly illustrative SMA scenarios and write CSV outputs."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .model import (
    critical_adoption_linear,
    liquidity_shortfall,
    monetary_transmission_linear,
    seigniorage_proxy,
    welfare,
)


def run(output: Path) -> tuple[pd.DataFrame, pd.DataFrame]:
    output.mkdir(parents=True, exist_ok=True)

    # Illustrative values solely to exercise the model; not estimates.
    kappa_fiat, kappa_btc = 0.80, 0.12
    minimum_capacity = 0.30
    threshold = critical_adoption_linear(kappa_fiat, kappa_btc, minimum_capacity)

    adoption = [i / 100 for i in range(101)]
    scenarios = pd.DataFrame(
        {
            "bitcoin_transaction_share": adoption,
            "transmission_capacity": [
                monetary_transmission_linear(s, kappa_fiat, kappa_btc) for s in adoption
            ],
            "real_seigniorage_proxy": [
                seigniorage_proxy(2.0, s, 0.65) for s in adoption
            ],
            "illustrative_welfare": [
                welfare(s, 0.50, 0.70, 0.12, 0.90) for s in adoption
            ],
            "above_transmission_threshold": [s > threshold for s in adoption],
        }
    )
    scenarios.to_csv(output / "scenario_grid.csv", index=False)

    stress_cases = pd.DataFrame(
        [
            {"case": "low_stress", "btc_liabilities": 10, "btc_liquidity": 7, "funding": 2},
            {"case": "medium_stress", "btc_liabilities": 20, "btc_liquidity": 8, "funding": 5},
            {"case": "high_stress", "btc_liabilities": 30, "btc_liquidity": 6, "funding": 4},
        ]
    )
    stress_cases["uncovered_btc_liquidity"] = stress_cases.apply(
        lambda r: liquidity_shortfall(
            r.btc_liabilities, r.btc_liquidity, r.funding
        ),
        axis=1,
    )
    stress_cases.to_csv(output / "liquidity_stress.csv", index=False)

    summary = pd.DataFrame(
        [
            {
                "kappa_fiat": kappa_fiat,
                "kappa_bitcoin": kappa_btc,
                "minimum_capacity": minimum_capacity,
                "critical_adoption_share": threshold,
                "parameter_status": "illustrative_not_estimated",
            }
        ]
    )
    summary.to_csv(output / "threshold_summary.csv", index=False)

    try:
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots()
        ax.plot(
            scenarios["bitcoin_transaction_share"],
            scenarios["transmission_capacity"],
            label="Transmission capacity",
        )
        ax.axhline(minimum_capacity, linestyle="--", label="Minimum requirement")
        ax.axvline(threshold, linestyle=":", label="Critical adoption share")
        ax.set(xlabel="Bitcoin transaction share", ylabel="Transmission coefficient")
        ax.legend()
        fig.tight_layout()
        fig.savefig(output / "transmission_curve.png", dpi=160)
        plt.close(fig)
    except ImportError:
        pass

    return scenarios, stress_cases


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=Path("outputs"))
    args = parser.parse_args()
    scenarios, stress = run(args.output)
    print(f"Wrote {len(scenarios)} scenario rows and {len(stress)} stress cases to {args.output}")


if __name__ == "__main__":
    main()
