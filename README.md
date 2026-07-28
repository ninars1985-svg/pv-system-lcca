# PV System Life Cycle Cost Analysis (LCCA)

A Python-based techno-economic model for evaluating the life cycle cost of
utility-scale photovoltaic (PV) systems. The model compares several system
sizes on the basis of their total cost of ownership over the project lifetime
and computes the Levelised Cost of Electricity (LCOE) and Net Present Value (NPV).

## Overview

Utility-scale PV projects differ widely in their economics depending on size,
CAPEX, operating costs and financing assumptions. This project performs a
comprehensive Life Cycle Cost Analysis (LCCA) for three representative system
sizes (1 MW, 5 MW and 10 MW) and quantifies how the key financial drivers
affect the outcome through a one-way sensitivity analysis.

## Methodology

All cash flows and energy volumes are discounted to present value at a common
discount rate. Annual energy yield declines each year according to a fixed
panel degradation rate.

The Levelised Cost of Electricity is computed as the ratio of discounted
lifetime cost to discounted lifetime energy:

```
LCOE = (CAPEX + Σ discounted OPEX) / (Σ discounted energy)
```

Net Present Value is the discounted revenue less the discounted costs, with
CAPEX incurred at year zero:

```
NPV = Σ discounted revenue − CAPEX − Σ discounted OPEX
```

## Key assumptions

| Parameter          | Value            |
| ------------------ | ---------------- |
| Project lifetime   | 25 years         |
| Discount rate      | 5%               |
| Electricity price  | 0.10 EUR/kWh     |
| Degradation rate   | 0.5% per year    |
| Capacity factor    | 0.15 (Austria)   |

System-specific CAPEX and OPEX values reflect economies of scale, with larger
systems benefiting from lower per-kW costs.

## Results (base case)

| System           | CAPEX (M€) | LCOE (€/kWh) | NPV (M€) |
| ---------------- | ---------- | ------------ | -------- |
| Small PV (1 MW)  | 0.80       | 0.06         | 0.75     |
| Medium PV (5 MW) | 3.50       | 0.05         | 4.44     |
| Large PV (10 MW) | 6.20       | 0.04         | 9.97     |

Larger systems achieve a lower LCOE and a higher NPV, driven by lower per-kW
CAPEX and OPEX. The sensitivity analysis shows that NPV is most responsive to
the electricity price, followed by the discount rate and CAPEX.

![LCCA results](lcca_results.png)

## Features

- CAPEX and OPEX modelling
- Discounted multi-year cash flow analysis
- Discounted LCOE and NPV calculation
- One-way sensitivity analysis on electricity price, discount rate and CAPEX
- Visual comparison of system configurations

## Technologies

- Python 3.x
- NumPy
- pandas
- Matplotlib

## Getting started

Clone the repository and install the dependencies:

```bash
git clone https://github.com/ninars1985-svg/pv-system-lcca.git
cd pv-system-lcca
pip install -r requirements.txt
```

Run the analysis:

```bash
python lcca_pv_system.py
```

The script prints the results and sensitivity tables to the console and saves
the comparison charts as `lcca_results.png`.

## Author

**Nina Ranjbar Sistani** — Energy Systems Analyst
MSc Energy Management, BOKU Vienna
Research experience at the Austrian Institute of Technology (AIT)

## License

This project is released under the MIT License. See the [LICENSE](LICENSE) file
for details.
