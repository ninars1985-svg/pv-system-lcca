"""
PV System Life Cycle Cost Analysis (LCCA)
==========================================
Author: Nina Ranjbar Sistani
Description: Techno-economic analysis of utility-scale PV systems
             Based on research experience at AIT (Austrian Institute of Technology)
"""

import numpy as np
import matplotlib.pyplot as plt

# ─────────────────────────────────────────
# SYSTEM PARAMETERS
# ─────────────────────────────────────────

systems = {
    "Small PV (1 MW)": {
        "capacity_kw": 1000,
        "capex_per_kw": 800,       # EUR/kW
        "opex_per_kw_year": 15,    # EUR/kW/year
        "degradation_rate": 0.005, # 0.5% per year
        "capacity_factor": 0.15,   # Austria average
    },
    "Medium PV (5 MW)": {
        "capacity_kw": 5000,
        "capex_per_kw": 700,
        "opex_per_kw_year": 12,
        "degradation_rate": 0.005,
        "capacity_factor": 0.15,
    },
    "Large PV (10 MW)": {
        "capacity_kw": 10000,
        "capex_per_kw": 620,
        "opex_per_kw_year": 10,
        "degradation_rate": 0.005,
        "capacity_factor": 0.15,
    },
}

# ─────────────────────────────────────────
# FINANCIAL PARAMETERS
# ─────────────────────────────────────────

project_lifetime = 25   # years
discount_rate = 0.05    # 5%
electricity_price = 0.10  # EUR/kWh

# ─────────────────────────────────────────
# LCCA CALCULATION
# ─────────────────────────────────────────

def calculate_lcca(system, lifetime, discount_rate, electricity_price):
    """
    Calculate Life Cycle Cost Analysis for a PV system.
    Returns CAPEX, total OPEX, total revenue, LCOE and NPV.
    """
    capacity_kw = system["capacity_kw"]
    capex = system["capex_per_kw"] * capacity_kw
    opex_annual = system["opex_per_kw_year"] * capacity_kw
    cf = system["capacity_factor"]
    deg = system["degradation_rate"]

    total_opex = 0
    total_revenue = 0
    annual_energy = []

    for year in range(1, lifetime + 1):
        # Energy production with degradation
        energy_kwh = capacity_kw * cf * 8760 * ((1 - deg) ** year)
        annual_energy.append(energy_kwh)

        # Discount factor
        discount_factor = 1 / ((1 + discount_rate) ** year)

        # OPEX and Revenue (discounted)
        total_opex += opex_annual * discount_factor
        total_revenue += energy_kwh * electricity_price * discount_factor

    # LCOE: total cost / total energy produced
    total_energy = sum(annual_energy)
    lcoe = (capex + total_opex) / total_energy

    # NPV
    npv = total_revenue - capex - total_opex

    return {
        "CAPEX (EUR)": capex,
        "Total OPEX - NPV (EUR)": round(total_opex, 0),
        "Total Revenue - NPV (EUR)": round(total_revenue, 0),
        "LCOE (EUR/kWh)": round(lcoe, 4),
        "NPV (EUR)": round(npv, 0),
    }

# ─────────────────────────────────────────
# RUN ANALYSIS
# ─────────────────────────────────────────

results = {}
for name, params in systems.items():
    results[name] = calculate_lcca(
        params, project_lifetime, discount_rate, electricity_price
    )
    print(f"\n{'='*45}")
    print(f"  {name}")
    print(f"{'='*45}")
    for key, value in results[name].items():
        print(f"  {key}: {value:,.2f}")

# ─────────────────────────────────────────
# VISUALISATION
# ─────────────────────────────────────────

labels = list(results.keys())
capex_vals = [results[s]["CAPEX (EUR)"] / 1e6 for s in labels]
opex_vals  = [results[s]["Total OPEX - NPV (EUR)"] / 1e6 for s in labels]
rev_vals   = [results[s]["Total Revenue - NPV (EUR)"] / 1e6 for s in labels]
npv_vals   = [results[s]["NPV (EUR)"] / 1e6 for s in labels]

x = np.arange(len(labels))
width = 0.25

fig, axes = plt.subplots(1, 2, figsize=(14, 6))
fig.suptitle(
    "PV System Life Cycle Cost Analysis\nNina Ranjbar Sistani — AIT Research",
    fontsize=13, fontweight="bold"
)

# Chart 1: Cost breakdown
ax1 = axes[0]
bars1 = ax1.bar(x - width/2, capex_vals, width, label="CAPEX", color="#1E4D3B")
bars2 = ax1.bar(x + width/2, opex_vals,  width, label="OPEX (NPV)", color="#4CAF82")
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
ax2.set_xticklabels(labels, rotation=10, ha="right")
ax2.grid(axis="y", alpha=0.3)

plt.tight_layout()
plt.savefig("lcca_results.png", dpi=150, bbox_inches="tight")
plt.show()
print("\nChart saved as lcca_results.png")
