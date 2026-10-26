"""Small constructed lender-review stories. No real providers or patient information."""

from .schema import CSV_COLUMNS

EXAMPLES = {
    "growth-aging": {
        "title": "More receivables, less modeled backing",
        "story": "A fictional community clinic reports $120,000 of receivables after $100,000 last period. Its 91+ balance is now $60,000 rather than $20,000. A lender needs to understand why a larger headline balance can support a smaller illustrative base.",
        "question": "Which aging cohorts changed, and what does the current policy do to them?",
        "meaning": "Compare the two source schedules before discussing availability. Changes between aggregate aging buckets do not prove that the same claims aged or that cash was collected.",
        "provider": "Example Community Clinic",
        "old": [
            ("Example Health Plan", "0-30", "80000", ".05"),
            ("Example Health Plan", "91+", "20000", ".05"),
        ],
        "new": [
            ("Example Health Plan", "0-30", "60000", ".05"),
            ("Example Health Plan", "91+", "60000", ".05"),
        ],
    },
    "denial-input": {
        "title": "Same billing, a changed denial assumption",
        "story": "A fictional imaging practice reports the same $100,000 balance in both periods, but changes its modeled denial input from 5% to 15%. The reported receivables have not fallen, while the illustrative base has.",
        "question": "Is the changed denial input supported, and is that loss already included in the collection factor?",
        "meaning": "The calculation isolates the effect of an input change. It cannot verify denial outcomes, establish a recovery forecast or resolve double counting without source definitions.",
        "provider": "Example Imaging Practice",
        "old": [("Example Health Plan", "0-30", "100000", ".05")],
        "new": [("Example Health Plan", "0-30", "100000", ".15")],
    },
    "mapped-rename": {
        "title": "A payer rename with continuous identity",
        "story": "A fictional therapy group changes the payer label in its export from Example Health Plan to Example Health Network. Both manifests deliberately use one stable payer ID, and the $50,000 balance and assumptions are unchanged.",
        "question": "Does the mapped identity preserve the same exposure without inventing an addition, removal or collection?",
        "meaning": "Only an explicit map establishes this continuity. Similar names are not enough. Different IDs would remain separate added and removed balances until reviewed.",
        "provider": "Example Therapy Group",
        "old": [("Example Health Plan", "0-30", "50000", ".05")],
        "new": [("Example Health Network", "0-30", "50000", ".05")],
    },
}


def example_sources(name):
    case = EXAMPLES[name]
    out = []
    for period, side, day in [("opening", "old", "2026-08-31"), ("closing", "new", "2026-09-30")]:
        values = case[side]
        csv = (
            ",".join(CSV_COLUMNS)
            + "\n"
            + "".join(
                f"{case['provider']},{payer},Commercial,{age},{gross},.2,.9,{denial}\n"
                for payer, age, gross, denial in values
            )
        )
        manifest = dict(
            snapshot_id=name + "-" + period,
            reporting_date=day,
            revision=1,
            kind="synthetic",
            borrower_ids={case["provider"]: "example-borrower"},
            payer_ids={v[0]: "example-payer" for v in values},
            source_note="Constructed educational example; no actual healthcare data.",
            imported_at=None,
        )
        out.append((csv.encode(), manifest))
    return out


def description(name):
    return {k: EXAMPLES[name][k] for k in ("title", "story", "question", "meaning")} | {"id": name}
