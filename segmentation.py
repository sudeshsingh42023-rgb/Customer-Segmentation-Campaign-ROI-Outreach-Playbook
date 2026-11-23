"""
Customer segmentation (RFM + K-Means) and campaign ROI analysis.
Outputs charts, segment table, channel scorecard and budget reallocation.
"""
from pathlib import Path
import json
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

OUT = Path("outputs"); OUT.mkdir(exist_ok=True)
tx = pd.read_csv("data/transactions.csv", parse_dates=["InvoiceDate"])
camp = pd.read_csv("data/campaigns.csv")

# ---------- 1. Clean ----------
tx = tx.dropna(subset=["CustomerID"])
tx = tx[(tx.Quantity > 0) & (tx.UnitPrice > 0)].drop_duplicates()
tx["Revenue"] = tx.Quantity * tx.UnitPrice

# ---------- 2. RFM ----------
snapshot = tx.InvoiceDate.max() + pd.Timedelta(days=1)
rfm = tx.groupby("CustomerID").agg(
    Recency=("InvoiceDate", lambda s: (snapshot - s.max()).days),
    Frequency=("InvoiceNo", "nunique"),
    Monetary=("Revenue", "sum"))
print(rfm.describe().round(1))

# ---------- 3. K-Means (log-scale, standardised) ----------
X = StandardScaler().fit_transform(np.log1p(rfm))
scores = {}
for k in range(2, 9):
    km = KMeans(n_clusters=k, n_init=10, random_state=42).fit(X)
    scores[k] = silhouette_score(X, km.labels_)
best_k = 5  # business-friendly; compare with silhouette-best below
print("Silhouette by k:", {k: round(v, 3) for k, v in scores.items()})
rfm["Cluster"] = KMeans(n_clusters=best_k, n_init=10, random_state=42).fit_predict(X)

# ---------- 4. Name the personas from cluster profile ----------
prof = rfm.groupby("Cluster").agg(Customers=("Recency", "size"),
                                  Recency=("Recency", "mean"),
                                  Frequency=("Frequency", "mean"),
                                  Monetary=("Monetary", "mean"))
prof["RevenueShare"] = rfm.groupby("Cluster")["Monetary"].sum() / rfm["Monetary"].sum()

def name(row):
    recent = row.Recency < 60
    if recent and row.Monetary >= prof.Monetary.quantile(.8): return "Champions"
    if recent and row.Frequency >= prof.Frequency.median():   return "Loyal"
    if recent:                                                return "New / Promising"
    if row.Monetary >= prof.Monetary.median():                return "At Risk - High Value"
    return "Lapsed / Low Value"
prof["Segment"] = prof.apply(name, axis=1)
# if two clusters collide on a name, number them
dup = prof.Segment.duplicated(keep=False)
prof.loc[dup, "Segment"] = prof.loc[dup, "Segment"] + " " + (prof[dup].groupby("Segment").cumcount() + 1).astype(str)
rfm["Segment"] = rfm.Cluster.map(prof.Segment)
seg = (prof.set_index("Segment").round({"Recency": 0, "Frequency": 1, "Monetary": 0, "RevenueShare": 3})
       .sort_values("RevenueShare", ascending=False))
seg.to_csv(OUT / "segments.csv"); rfm.to_csv(OUT / "customer_segments.csv")
print(seg)

fig, axes = plt.subplots(1, 2, figsize=(11, 4))
axes[0].bar(seg.index, seg.Customers, color="#2f6fb0"); axes[0].set_title("Customers per segment")
axes[1].bar(seg.index, seg.RevenueShare * 100, color="#2a9d8f"); axes[1].set_title("Revenue share (%)")
for a in axes: a.tick_params(axis="x", rotation=30)
plt.tight_layout(); plt.savefig(OUT / "segments.png", dpi=150); plt.close()

# ---------- 5. Campaign / channel ROI ----------
c = camp.copy()
c["CTR_%"] = c.clicks / c.impressions * 100
c["Click_to_Lead_%"] = c.leads / c.clicks * 100
c["Lead_to_Cust_%"] = c.customers / c.leads * 100
c["CAC"] = c.spend / c.customers
c["ROAS"] = c.revenue / c.spend
c["ROI_%"] = (c.revenue - c.spend) / c.spend * 100
c = c.round(2).sort_values("ROAS", ascending=False)
c.to_csv(OUT / "channel_scorecard.csv", index=False)
print(c[["channel", "spend", "CAC", "ROAS", "ROI_%"]])

fig, ax = plt.subplots(1, 2, figsize=(11, 4))
ax[0].barh(c.channel[::-1], c.ROAS[::-1], color="#2a9d8f"); ax[0].set_title("ROAS by channel")
ax[0].axvline(1, color="red", ls="--")
ax[1].barh(c.channel[::-1], c.CAC[::-1], color="#e76f51"); ax[1].set_title("CAC by channel (INR)")
plt.tight_layout(); plt.savefig(OUT / "channel_roi.png", dpi=150); plt.close()

# ---------- 6. Budget reallocation (simple, transparent rule) ----------
# Move 20% of spend from below-median-ROAS channels to above-median ones,
# proportional to ROAS. Conservative assumption: new money earns only 60% of past ROAS
# (diminishing returns).
ci = c.set_index("channel")
total = ci.spend.sum()
low = ci[ci.ROAS < ci.ROAS.median()]
high = ci[ci.ROAS >= ci.ROAS.median()]
shift = 0.20 * low.spend.sum()
weights = high.ROAS / high.ROAS.sum()
new = ci.spend.astype(float).copy()
new[low.index] = low.spend * 0.80
new[high.index] = high.spend + shift * weights
gain = float((shift * weights * high.ROAS * 0.6).sum())
loss = float((0.20 * low.spend * low.ROAS).sum())
extra_rev = gain - loss
realloc = pd.DataFrame({"current_spend": ci.spend, "proposed_spend": new.round(0)})
realloc["change_%"] = ((realloc.proposed_spend / realloc.current_spend - 1) * 100).round(1)
realloc.to_csv(OUT / "budget_reallocation.csv")
print(realloc)
print(f"Estimated net revenue change (conservative): INR {extra_rev:,.0f}")

json.dump({
    "n_customers": int(len(rfm)), "silhouette_by_k": {k: round(v, 3) for k, v in scores.items()},
    "total_spend": int(total), "blended_ROAS": round(float(camp.revenue.sum() / total), 2),
    "est_net_revenue_change_inr": round(extra_rev),
    "data_note": "SYNTHETIC unless data/ files were replaced with real data",
}, open(OUT / "summary.json", "w"), indent=2)
