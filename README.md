# Customer Segmentation, Campaign ROI & Outreach Playbook

Segments customers with RFM + K-Means, scores marketing channels on CAC / ROAS / ROI, proposes a budget reallocation, and turns the findings into a segment-wise outreach playbook.

> **Data note:** `generate_data.py` creates SYNTHETIC data so the code runs end to end. For real results, use the UCI "Online Retail II" dataset as `data/transactions.csv` (columns CustomerID, InvoiceNo, InvoiceDate, Quantity, UnitPrice) and your own channel spend in `data/campaigns.csv`. Re-run and update any numbers you quote.

## Run
```bash
pip install -r requirements.txt
python generate_data.py     # skip if you use real data
python segmentation.py
```

## What it does
1. Cleans transactions (drops missing IDs, returns/negatives, duplicates)
2. Builds Recency / Frequency / Monetary per customer
3. K-Means on log-scaled, standardised RFM; checks silhouette for k = 2-8
4. Names personas from cluster profiles and reports revenue share
5. Channel scorecard: CTR, click-to-lead, lead-to-customer, CAC, ROAS, ROI
6. Budget reallocation rule (20% from below-median ROAS channels to above-median, proportional to ROAS, assuming only 60% of past ROAS on new money)
7. `outreach_playbook.md`: templates, A/B test plan, 30-day plan

## Outputs (`outputs/`)
`segments.csv`, `customer_segments.csv`, `segments.png`, `channel_scorecard.csv`, `channel_roi.png`, `budget_reallocation.csv`, `summary.json`

## Limitations (say this in interviews)
- K-Means assumes roughly spherical clusters; silhouette was best at k=3 but k=5 was chosen for actionable personas.
- ROAS is not incrementality; a holdout test would be needed to prove causal lift.
- Reallocation uses a simple heuristic, not a media-mix model.
