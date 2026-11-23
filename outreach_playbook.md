# Segment Outreach Playbook & A/B Test Plan

Edit the names, offers and numbers to match your real output (outputs/segments.csv).

| Segment | Goal | Channel | Cadence | Offer / angle |
|---|---|---|---|---|
| Champions | Retain, upsell, referrals | Email + WhatsApp | 2 touches/month | Early access, loyalty tier, referral reward |
| Loyal | Grow basket size | Email | 2 touches/month | Bundles, "you may also like", free-shipping threshold |
| New / Promising | Second purchase within 30 days | Email + SMS | Day 3, 10, 21 | Welcome series, 10% off 2nd order |
| At Risk - High Value | Win back before they churn | WhatsApp + Email | 3-step over 14 days | Personal check-in, "we miss you" + time-limited offer |
| Lapsed / Low Value | Cheap reactivation or suppress | Email only | 1-2 touches then stop | Strong discount; suppress if no response (protects deliverability, saves cost) |

## Message templates

**Win-back email (At Risk - High Value)**
Subject: {{first_name}}, we saved something for you
> Hi {{first_name}}, it's been a while since your last order. We've picked a few things based on what you bought before, and added {{offer}} valid until {{date}}. Reply to this mail if there's anything we can fix. - {{sender}}

**WhatsApp nudge (Champions referral)**
> Hi {{first_name}}! Thanks for being one of our best customers. Refer a friend and you both get {{reward}}. Your link: {{link}}

**Welcome series, email 2 (New / Promising, Day 10)**
Subject: Getting the most out of {{product_category}}
> Hi {{first_name}}, here are 3 things customers like you do next... [content]. Your second-order offer: {{offer}}.

## A/B test plan (At Risk - High Value segment)
- **Hypothesis:** A personalised, product-based subject line beats a generic discount subject line on win-back rate.
- **Variants:** A = "We miss you: 15% off" | B = "{{first_name}}, picks based on your last order"
- **Split:** random 50/50 within the segment; fixed send time.
- **Primary metric:** reactivation rate (order within 14 days). **Secondary:** open rate, click rate, revenue per recipient.
- **Sample size:** use a two-proportion calculator for a baseline of ~5% and a minimum detectable lift of ~2 points (roughly 1,500 per arm at 80% power).
- **Decision rule:** ship the winner only if p < 0.05 and revenue per recipient is not lower.

## 30-day action plan
| Week | Action |
|---|---|
| 1 | Load segments into CRM/email tool; set up suppression for Lapsed; build welcome series |
| 2 | Launch win-back A/B test; start Champions referral push |
| 3 | Read A/B results; roll out the winner; begin budget shift (first 10%) |
| 4 | Review channel ROAS and CAC; complete reallocation if ROAS holds; report to leadership |
