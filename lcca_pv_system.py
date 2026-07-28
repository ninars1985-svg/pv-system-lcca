"""
PV System Life Cycle Cost Analysis (LCCA)
==========================================
Author: Nina Ranjbar Sistani — Energy Systems Analyst
Description: Techno-economic analysis of utility-scale PV systems.
Based on research experience at AIT (Austrian Institute of Technology).

The model compares several PV system sizes on the basis of their
life cycle cost, computing CAPEX, discounted OPEX, discounted revenue,
Levelised Cost of Electricity (LCOE) and Net Present Value (NPV).
A one-way sensitivity analysis on the key financial drivers is included.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# SYSTEM PARAMETERS
# ─────────────────────────────────────────
SYSTEMS = {
    "Small PV (1 MW)": {
        "capacity_kw": 1_000,
        "capex_per_kw": 800,        # EUR/kW
        "opex_per_kw_year": 15,     # EUR/kW/year
        "degradation_rate": 0.005,  # 0.5% per year
        "capacity_factor": 0.15,    # Austria average
    },
    "Medium PV (5 MW)": {
        "capacity_kw": 5_000,
        "capex_per_kw": 700,
        "opex_per_kw_year": 12,
        "degradation_rate": 0.005,
        "capacity_factor": 0.15,
    },
    "Large PV (10 MW)": {
        "capacity_kw": 10_000,
        "capex_per_kw": 620,
        "opex_per_kw_year": 10,
        "degradation_rate": 0.005,
        "capacity_factor": 0.15,
    },
}

# ─────────────────────────────────────────
# FINANCIAL PARAMETERS
# ─────────────────────────────────────────
PROJECT_LIFETIME = 25       # years
DISCOUNT_RATE = 0.05        # 5%
ELECTRICITY_PRICE = 0.10    # EUR/kWh
HOURS_PER_YEAR = 8_760


# ─────────────────────────────────────────
# LCCA CALCULATION
# ─────────────────────────────────────────
def calculate_lcca(system, lifetime=PROJECT_LIFETIME,
                   discount_rate=DISCOUNT_RATE,
                   electricity_price=ELECTRICITY_PRICE):
    """Calculate the Life Cycle Cost Analysis for a single PV system.

    Both costs and energy are discounted at the same rate, which is the
    methodologically correct way to compute a levelised cost.

        LCOE = (CAPEX + Σ discounted OPEX) / (Σ discounted energy)

    Returns a dict with CAPEX, discounted OPEX, discounted revenue,
    LCOE (EUR/kWh) and NPV (EUR).
    """
    capacity_kw = system["capacity_kw"]
    capex = system["capex_per_kw"] * capacity_kw
    opex_annual = system["opex_per_kw_year"] * capacity_kw
    cf = system["capacity_factor"]
    deg = system["degradation_rate"]

    total_opex = 0.0
    total_revenue = 0.0
    discounted_energy = 0.0  # denominator of LCOE, discounted

    for year in range(1, lifetime + 1):
        # Energy production, reduced each year by panel degradation
        energy_kwh = capacity_kw * cf * HOURS_PER_YEAR * ((1 - deg) ** year)

        # Discount factor for this year
        discount_factor = 1 / ((1 + discount_rate) ** year)

        total_opex += opex_annual * discount_factor
        total_revenue += energy_kwh * electricity_price * discount_factor
        discounted_energy += energy_kwh * discount_factor

    # LCOE: discounted total cost / discounted total energy
    lcoe = (capex + total_opex) / discounted_energy

    # NPV: discounted revenue minus discounted costs (CAPEX at year 0)
    npv = total_revenue - capex - total_opex

    return {
        "CAPEX (EUR)": capex,
        "Total OPEX - NPV (EUR)": round(total_opex, 0),
        "Total Revenue - NPV (EUR)": round(total_revenue, 0),
        "LCOE (EUR/kWh)": round(lcoe, 4),
        "NPV (EUR)": round(npv, 0),
    }


def run_all_systems():
    """Run the LCCA for every system and return a tidy DataFrame."""
    rows = {name: calculate_lcca(params) for name, params in SYSTEMS.items()}
    return pd.DataFrame(rows).T


# ─────────────────────────────────────────
# SENSITIVITY ANALYSIS
# ─────────────────────────────────────────
def sensitivity_analysis(system, variations=np.linspace(-0.3, 0.3, 13)):
    """One-way sensitivity of NPV to three key drivers.

    Each driver is varied from -30% to +30% around its base value while
    everything else is held constant. Returns a DataFrame of NPV (EUR)
    indexed by the percentage change.
    """
    base = {
        "Electricity price": ELECTRICITY_PRICE,
        "Discount rate": DISCOUNT_RATE,
        "CAPEX per kW": system["capex_per_kw"],
    }
    out = {}
    for driver, base_val in base.items():
        npvs = []
        for v in variations:
            sys = dict(system)
            price = ELECTRICITY_PRICE
            disc = DISCOUNT_RATE
            if driver == "Electricity price":
                price = base_val * (1 + v)
            elif driver == "Discount rate":
                disc = base_val * (1 + v)
            elif driver == "CAPEX per kW":
                sys["capex_per_kw"] = base_val * (1 + v)
            res = calculate_lcca(sys, discount_rate=disc, electricity_price=price)
            npvs.append(res["NPV (EUR)"])
        out[driver] = npvs
    df = pd.DataFrame(out, index=np.round(variations * 100).astype(int))
    df.index.name = "Change (%)"
    return df


# ─────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────
def plot_results(results_df, sensitivity_df):
    labels = list(results_df.index)
    capex_vals = results_df["CAPEX (EUR)"] / 1e6
    opex_vals = results_df["Total OPEX - NPV (EUR)"] / 1e6
    npv_vals = results_df["NPV (EUR)"] / 1e6

    x = np.arange(len(labels))
    width = 0.25

    fig, axes = plt.subplots(1, 3, figsize=(18, 6))
    fig.suptitle(
        "PV System Life Cycle Cost Analysis\nNina Ranjbar Sistani — AIT Research",
        fontsize=13, fontweight="bold",
    )

    # Chart 1: Cost breakdown
    ax1 = axes[0]
    ax1.bar(x - width / 2, capex_vals, width, label="CAPEX", color="#1E4D3B")
    ax1.bar(x + width / 2, opex_vals, width, label="OPEX (NPV)", color="#4CAF82")
    ax1.set_title("Cost Breakdown (Million EUR)")
    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=10, ha="right")
    ax1.set_ylabel("Million EUR")
    ax1.legend()
    ax1.grid(axis="y", alpha=0.3)

    # Chart 2: NPV comparison
    ax2 = axes[1]
    colors = ["#2E7D5A" if v >= 0 else "#CC0000" for v in npv_vals]
    ax2.bar(labels, npv_vals, color=colors)
    ax2.set_title("Net Present Value (Million EUR)")
    ax2.set_ylabel("Million EUR")
    ax2.axhline(0, color="black", linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels(labels, rotation=10, ha="right")
    ax2.grid(axis="y", alpha=0.3)

    # Chart 3: Sensitivity of NPV (Large PV system)
    ax3 = axes[2]
    for col in sensitivity_df.columns:
        ax3.plot(sensitivity_df.index, sensitivity_df[col] / 1e6,
                 marker="o", markersize=3, label=col)
    ax3.set_title("NPV Sensitivity — Large PV (Million EUR)")
    ax3.set_xlabel("Change in parameter (%)")
    ax3.set_ylabel("Million EUR")
    ax3.axhline(0, color="black", linewidth=0.8)
    ax3.legend()
    ax3.grid(alpha=0.3)

    plt.tight_layout()
    plt.savefig("lcca_results.png", dpi=150, bbox_inches="tight")
    plt.close(fig)


# ─────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────
def main():
    results_df = run_all_systems()

    pd.set_option("display.float_format", lambda v: f"{v:,.2f}")
    print("\n" + "=" * 60)
    print(" LIFE CYCLE COST ANALYSIS — RESULTS")
    print("=" * 60)
    print(results_df.to_string())

    sensitivity_df = sensitivity_analysis(SYSTEMS["Large PV (10 MW)"])
    print("\n" + "=" * 60)
    print(" SENSITIVITY ANALYSIS — NPV of Large PV (EUR)")
    print("=" * 60)
    print(sensitivity_df.to_string())

    plot_results(results_df, sensitivity_df)
    print("\nChart saved as lcca_results.png")


if __name__ == "__main__":
    main()
