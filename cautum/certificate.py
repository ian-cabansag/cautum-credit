"""Reproducible, illustrative review exhibit. No signature or legal certification."""

from decimal import Decimal
from html import escape

from .engine import MONEY_FIELDS

LABELS = {
    "gross_ar": "Gross A/R",
    "net_allowed": "Modeled allowed",
    "expected_collectible": "Modeled collectible",
    "eligible_collateral": "Policy-adjusted collateral",
    "borrowing_base": "Illustrative borrowing base",
}


def render_certificate(a: dict, borrower: str = "") -> str:
    if borrower and borrower not in {b["name"] for b in a["borrowers"]}:
        raise ValueError("Borrower is not present in the accepted portfolio.")
    rows = [r for r in a["audit"] if not borrower or r["provider"] == borrower]
    amounts = {
        k: sum((Decimal(r["amounts_exact"][k]) for r in rows), Decimal(0)) for k in MONEY_FIELDS
    }
    esc = lambda v: escape(str(v), quote=True)
    usd = lambda v: f"${v:,.2f}"
    stages = "".join(f"<tr><th>{LABELS[k]}</th><td>{usd(v)}</td></tr>" for k, v in amounts.items())
    flags = [f for f in a["alerts"] if not borrower or f["provider"] == borrower]
    exceptions = "".join(
        f"<tr><td>{esc(f['provider'])}</td><td>{esc(f['code'])}</td><td>{esc(f['observed_exact'])}</td><td>{esc(f['operator'])} {esc(f['threshold_exact'])}</td><td>{len(f['cohort_ids'])}</td></tr>"
        for f in flags
    )
    details = "".join(
        "<tr>"
        + "".join(
            f"<td>{esc(v)}</td>"
            for v in [
                r["cohort_id"],
                r["provider"],
                r["payer"],
                r["age"],
                *[r["amounts_exact"][k] for k in MONEY_FIELDS],
            ]
        )
        + "</tr>"
        for r in rows
    )
    policy = "".join(
        f"<tr><th>{esc(k)}</th><td>{esc(v)}</td></tr>" for k, v in a["policy_exact"].items()
    )
    return f"""<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Cautum | Illustrative borrowing base certificate</title>
<style>body{{font:14px/1.6 system-ui;color:#173d33;background:#f6f7f4;max-width:1100px;padding:40px;margin:auto}}h1,h2{{font-family:Georgia,serif;font-weight:400}}h1{{font-size:34px}}table{{width:100%;border-collapse:collapse;background:white;margin:20px 0}}th,td{{text-align:left;border-bottom:1px solid #dce3de;padding:10px;font-variant-numeric:tabular-nums;overflow-wrap:anywhere}}.notice{{padding:18px;background:#eee9dc;border-left:3px solid #c78e53}}.trace{{font-size:10px}}.scroll{{overflow:auto}}@page{{size:A4 landscape;margin:16mm}}@media print{{body{{background:white;padding:0;max-width:none}}thead{{display:table-header-group}}tr{{break-inside:avoid}}h2{{break-after:avoid}}}}</style>
<header>CAUTUM CREDIT / REVIEW EXHIBIT</header><h1>Illustrative borrowing base certificate</h1><p class="notice"><strong>Unapproved synthetic demonstration.</strong> This is a reproducible calculation exhibit, not a lender certificate, valuation, legal opinion, financing commitment or authenticated approval.</p>
<p>Scope: {esc(borrower or "Full synthetic portfolio")} · {len(rows)} cohorts<br>Analysis: {esc(a["analysis_id"])} · Policy: {esc(a["policy_id"])} · Engine: {esc(a["engine_version"])}<br>Reporting vintage: not supplied. Source hash: {esc(a.get("import_evidence", {}).get("source_sha256", "not supplied"))}</p>
<h2>Gross-to-base reconciliation</h2><table>{stages}</table><p>{esc(a["rounding"])}</p>
<h2>Outstanding decisions</h2><ul><li>Legal enforceability and permitted collateral: unreviewed.</li><li>Reserves, disputes, offsets and outstandings: not supplied or modeled. Net undrawn availability: not calculated.</li><li>Denial/collection independence and policy factors: not calibrated or lender-approved.</li><li>Analyst owner, risk approval and counsel review: TO REVIEW. No authenticated sign-off recorded.</li></ul>
<h2>Policy exceptions ({len(flags)})</h2><p>Observed and threshold values below are ratios, compared at full Decimal precision.</p><table><thead><tr><th>Borrower</th><th>Reason</th><th>Observed ratio</th><th>Comparator / threshold</th><th>Evidence cohorts</th></tr></thead><tbody>{exceptions or '<tr><td colspan="5">No selected-policy threshold breach. No approval implied.</td></tr>'}</tbody></table>
<h2>Exact illustrative policy</h2><table>{policy}</table>
<h2>Cohort evidence · USD</h2><div class="scroll"><table class="trace"><thead><tr><th>Cohort</th><th>Borrower</th><th>Payer</th><th>Age</th><th>Gross</th><th>Allowed</th><th>Collectible</th><th>Policy-adjusted</th><th>Illustrative base</th></tr></thead><tbody>{details}</tbody></table></div><p>Use the JSON and trace CSV exports for original rates, unrounded amounts and adjustment detail. Technical reconciliation does not validate real-world recovery, legal collateral rights or underwriting outcomes.</p></html>"""
