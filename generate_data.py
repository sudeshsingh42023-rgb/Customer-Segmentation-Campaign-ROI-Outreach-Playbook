"""
Generates SYNTHETIC data so the project runs end to end:
  data/transactions.csv   - e-commerce style orders (like the UCI Online Retail schema)
  data/campaigns.csv      - marketing channel spend & results

To use REAL data: put the UCI "Online Retail II" (or any CSV with CustomerID,
InvoiceNo, InvoiceDate, Quantity, UnitPrice) at data/transactions.csv and replace
campaigns.csv with your own channel spend data.
"""
import numpy as np, pandas as pd
from pathlib import Path
rng = np.random.default_rng(7)
Path("data").mkdir(exist_ok=True)

# --- customers with latent behaviour types ---
n_cust = 2500
types = rng.choice(["champion", "loyal", "occasional", "at_risk", "new"],
                   n_cust, p=[0.10, 0.22, 0.33, 0.20, 0.15])
params = {  # orders/yr, avg basket value, recency window (days since last order)
    "champion": (14, 90, (1, 30)), "loyal": (7, 60, (5, 60)),
    "occasional": (3, 45, (30, 200)), "at_risk": (4, 55, (180, 360)),
    "new": (1, 40, (1, 40)),
}
rows = []
end = pd.Timestamp("2026-10-31")
for cid, t in enumerate(types, start=10000):
    n_orders, basket, (rlo, rhi) = params[t]
    k = max(1, rng.poisson(n_orders))
    last = end - pd.Timedelta(days=int(rng.integers(rlo, rhi)))
    for j in range(k):
        d = last - pd.Timedelta(days=int(rng.integers(0, 330 if t != "new" else 30)) if j else 0)
        rows.append((f"INV{len(rows):06d}", cid, d,
                     int(rng.integers(1, 6)),
                     round(float(rng.gamma(4, basket / 4 / 2.5)), 2),
                     rng.choice(["Organic", "Paid Search", "Email", "Social", "Referral"],
                                p=[0.25, 0.25, 0.2, 0.2, 0.1])))
tx = pd.DataFrame(rows, columns=["InvoiceNo", "CustomerID", "InvoiceDate",
                                 "Quantity", "UnitPrice", "AcquisitionChannel"])
tx.to_csv("data/transactions.csv", index=False)

# --- campaign / channel performance ---
camp = pd.DataFrame({
    "channel": ["Paid Search", "Social", "Email", "Referral", "Organic/SEO", "Influencer"],
    "spend":   [420000, 310000, 60000, 90000, 120000, 250000],
    "impressions": [5200000, 6100000, 900000, 150000, 1800000, 4200000],
    "clicks":  [124000, 98000, 41000, 9500, 52000, 61000],
    "leads":   [9800, 6100, 5200, 2100, 3900, 3300],
    "customers": [1250, 640, 1010, 520, 760, 310],
    "revenue": [1980000, 910000, 1560000, 880000, 1190000, 480000],
})
camp.to_csv("data/campaigns.csv", index=False)
print(f"transactions={len(tx)} customers={tx.CustomerID.nunique()}; campaigns={len(camp)}")
