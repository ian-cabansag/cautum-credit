"""Independent golden arithmetic, Fraction reference, input boundary and export scope."""

import json
import random
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

from cautum.api import app
from cautum.change_review import render_packet
from cautum.parser import DataError
from cautum.schema import Policy
from cautum.snapshot_io import parse_manifest
from cautum.surveillance import compare, snapshot

HEADER = "provider,payer,payer_type,aging_bucket,gross_ar,contractual_adjustment_rate,historical_collection_factor,denial_rate\n"


def meta(day, names=None, payers=None):
    return dict(
        snapshot_id="case-" + day[-2:],
        reporting_date=day,
        revision=1,
        kind="synthetic",
        borrower_ids=names or {"Test Clinic": "borrower-one"},
        payer_ids=payers or {"Test Payer": "payer-one"},
        source_note="Constructed test",
        imported_at=None,
    )


def pair(old="1000,.2,.9,.05", new="1200,.1,.8,.1", policy=None):
    def raw(values):
        return (HEADER + "Test Clinic,Test Payer,Commercial,0-30," + values + "\n").encode()

    return compare(
        snapshot(raw(old), meta("2026-08-01"), policy),
        snapshot(raw(new), meta("2026-09-02"), policy),
    )


def test_independent_golden_driver_values_and_source_chain():
    r = pair()
    c = r["change_review"]
    b = c["borrowers"][0]
    row = c["rows"][0]
    assert r["bridge"]["borrowing_base"]["opening"] == "547.20"
    assert r["bridge"]["borrowing_base"]["closing"] == "622.08"
    assert c["effects"] == {
        "gross_ar": "109.44",
        "contractual_adjustment_rate": "82.08",
        "historical_collection_factor": "-82.08",
        "denial_rate": "-34.56",
        "added": "0.00",
        "removed": "0.00",
    }
    assert b["delta"] == "74.88" and c["unexplained_model_delta"] == "0.00"
    assert row["before"]["inputs_exact"]["gross_ar"] == "1000"
    assert row["after"]["inputs_exact"]["gross_ar"] == "1200"
    assert [s["base_after"] for s in row["steps"]] == ["656.64", "738.72", "656.64", "622.08"]
    assert any("denominator" in q for q in b["questions"])


def test_fraction_reference_under_seeded_changes_and_fractional_factors():
    rng = random.Random(414)
    policy = Policy(advance_rate=".712345", aging_0_30=".923456", payer_commercial=".812345")
    coefficient = Fraction("0.712345") * Fraction("0.923456") * Fraction("0.812345")

    def reference(x):
        gross, contract, collection, denial = map(Fraction, x)
        v = gross * (1 - contract) * collection * (1 - denial) * coefficient
        return (v.numerator * 200 + v.denominator) // (2 * v.denominator)

    for _ in range(64):
        cases = [
            [
                str(Decimal(rng.randint(1, 100000000)) / 100),
                *[str(Decimal(rng.randint(0, 1000000)) / 1000000) for _ in range(3)],
            ]
            for _ in range(2)
        ]
        old, new = cases
        c = pair(",".join(old), ",".join(new), policy)["change_review"]
        current = list(old)
        last = reference(current)
        expected = []
        for i in range(4):
            current[i] = new[i]
            n = reference(current)
            expected.append(Decimal(n - last) / 100)
            last = n
        assert [Decimal(c["effects"][k]) for k in list(c["driver_labels"])[:4]] == expected
        assert (
            sum(map(Decimal, c["effects"].values()))
            == Decimal(reference(new) - reference(old)) / 100
        )


def test_added_removed_zero_base_and_explicit_rename():
    before = (HEADER + "Test Clinic,Test Payer,Commercial,0-30,1000,.2,.9,.05\n").encode()
    after = (HEADER + "Renamed Clinic,Renamed Payer,Commercial,0-30,1000,.2,.9,.05\n").encode()
    r = compare(
        snapshot(before, meta("2026-08-01")),
        snapshot(
            after,
            meta("2026-09-02", {"Renamed Clinic": "borrower-one"}, {"Renamed Payer": "payer-one"}),
        ),
    )
    assert (
        r["change_review"]["rows"][0]["explicit_rename"]
        and r["change_review"]["rows"][0]["delta_exact"]["borrowing_base"] == "0.00"
    )
    r = compare(
        snapshot(before, meta("2026-08-01")),
        snapshot(
            after,
            meta("2026-09-02", {"Renamed Clinic": "borrower-two"}, {"Renamed Payer": "payer-two"}),
        ),
    )
    assert (
        r["change_review"]["effects"]["added"] == "547.20"
        and r["change_review"]["effects"]["removed"] == "-547.20"
    )
    assert r["change_review"]["effects"]["denial_rate"] == "0.00"
    zero = pair("1000,.2,.9,1", "1200,.2,.9,1")["change_review"]
    assert zero["declining_borrowers"] == 0 and zero["effects"]["gross_ar"] == "0.00"


def test_comparison_id_stability_and_sensitivity():
    a = pair()
    assert a["change_review"]["review_id"] == pair()["change_review"]["review_id"]
    assert (
        a["change_review"]["review_id"] != pair(new="1201,.1,.8,.1")["change_review"]["review_id"]
    )
    assert (
        a["change_review"]["review_id"]
        != pair(policy=Policy(advance_rate=".7"))["change_review"]["review_id"]
    )


def test_manifest_rejects_extra_duplicate_non_synthetic_and_incomplete_fields():
    m = meta("2026-08-01")
    assert parse_manifest(json.dumps(m)) == m
    for bad in [
        dict(m, patient_name="Synthetic"),
        dict(m, kind="production"),
        dict(m, revision="1"),
        dict(m, imported_at="2026-10-25"),
        {"kind": "synthetic"},
    ]:
        with pytest.raises(DataError):
            parse_manifest(json.dumps(bad))
    text = json.dumps(m).replace('"revision": 1', '"revision": 1, "revision": 2')
    with pytest.raises(DataError):
        parse_manifest(text)
    with pytest.raises(DataError):
        parse_manifest(" " * 32769)


def uploaded():
    d = Path("cautum/data")
    return {
        "opening": ("opening.csv", (d / "synthetic_T0.csv").read_bytes()),
        "closing": ("closing.csv", (d / "synthetic_T1.csv").read_bytes()),
    }, {
        "opening_manifest": (d / "synthetic_T0.json").read_text(),
        "closing_manifest": (d / "synthetic_T1.json").read_text(),
        "synthetic": "true",
    }


def test_real_pair_import_matches_bundled_and_server_packet_is_scoped():
    c = TestClient(app, base_url="http://127.0.0.1")
    files, data = uploaded()
    bundled = c.post("/api/surveillance").json()
    r = c.post("/api/surveillance", files=files, data=data)
    assert r.status_code == 200
    assert r.json()["source_kind"] == "uploaded synthetic pair"
    assert r.json()["change_review"] == bundled["change_review"]
    bid = r.json()["change_review"]["borrowers"][0]["borrower_id"]
    packet = c.post(
        "/api/surveillance", files=files, data={**data, "output_format": "html", "borrower": bid}
    )
    assert packet.status_code == 200 and "attachment" in packet.headers["content-disposition"]
    assert bundled["change_review"]["review_id"] in packet.text and "SHA-256" in packet.text
    assert "SYNTHETIC / HUMAN REVIEW REQUIRED" in packet.text and "cash receipts" in packet.text
    assert packet.text.count("<article>") == len(
        next(b for b in bundled["change_review"]["borrowers"] if b["borrower_id"] == bid)[
            "cohort_keys"
        ]
    )
    assert (
        c.post(
            "/api/surveillance", data={"output_format": "html", "borrower": "missing"}
        ).status_code
        == 400
    )


@pytest.mark.parametrize(
    "case",
    [
        "incomplete",
        "no_consent",
        "wrong_date",
        "unknown_column",
        "changed_taxonomy",
        "malformed_manifest",
        "bad_format",
    ],
)
def test_bad_pair_rejects_without_silent_fixture_fallback(case):
    c = TestClient(app, base_url="http://127.0.0.1")
    files, data = uploaded()
    if case == "incomplete":
        del files["closing"]
    if case == "no_consent":
        data["synthetic"] = "false"
    if case == "wrong_date":
        data["closing_manifest"] = data["closing_manifest"].replace("2026-09-30", "2026-08-31")
    if case == "unknown_column":
        files["closing"] = ("closing.csv", b"patient_name\nSYNTHETIC")
    if case == "changed_taxonomy":
        files["closing"] = (
            "closing.csv",
            files["closing"][1].replace(b",Commercial,", b",Medicare,"),
        )
    if case == "malformed_manifest":
        data["closing_manifest"] = "[]"
    if case == "bad_format":
        data["output_format"] = "execute"
    assert c.post("/api/surveillance", files=files, data=data).status_code == 400


def test_html_packet_escapes_labels_and_has_no_external_assets():
    r = pair()
    r["change_review"]["borrowers"][0]["provider"] = "<img src=x onerror=alert(1)>"
    h = render_packet(r)
    assert "<img src=x" not in h and "&lt;img" in h
    assert "<script" not in h and 'src="http' not in h


def test_hostile_json_encoding_depth_and_full_request_bound():
    m = meta("2026-08-01")
    for text in [
        "[" * 1500 + "0" + "]" * 1500,
        json.dumps(dict(m, source_note="bad\ud800")),
        json.dumps(dict(m, source_note="bad\x00")),
    ]:
        with pytest.raises(DataError):
            parse_manifest(text)
    c = TestClient(app, base_url="http://127.0.0.1")
    assert (
        c.post(
            "/api/surveillance",
            files={
                "opening": ("opening.csv", b"x" * 1100000),
                "closing": ("closing.csv", b"x" * 1100000),
            },
        ).status_code
        == 413
    )


def test_combined_source_cohort_limit():
    from itertools import product

    names = {f"Test Clinic {i}": f"borrower-{i}" for i in range(55)}
    payers = {f"Test Payer {i}": f"payer-{i}" for i in range(6)}
    raw = (
        HEADER
        + "".join(
            f"{n},{p},Commercial,{age},1000,.2,.9,.05\n"
            for n, p, age in list(product(names, payers, ["0-30", "31-60", "61-90", "91+"]))[:1251]
        )
    ).encode()
    data = {
        "opening_manifest": json.dumps(meta("2026-08-01", names, payers)),
        "closing_manifest": json.dumps(meta("2026-09-02", names, payers)),
        "synthetic": "true",
    }
    c = TestClient(app, base_url="http://127.0.0.1")
    r = c.post(
        "/api/surveillance",
        files={"opening": ("opening.csv", raw), "closing": ("closing.csv", raw)},
        data=data,
    )
    assert r.status_code == 400 and "2,500" in r.json()["detail"]


@pytest.mark.parametrize(
    "name,gross,base",
    [
        ("growth-aging", "20000.00", "-10944.00"),
        ("denial-input", "0.00", "-5760.00"),
        ("mapped-rename", "0.00", "0.00"),
    ],
)
def test_relatable_examples_have_independent_expected_results(name, gross, base):
    c = TestClient(app, base_url="http://127.0.0.1")
    r = c.post("/api/surveillance", data={"example": name})
    assert r.status_code == 200
    a = r.json()
    assert a["bridge"]["gross_ar"]["delta"] == gross
    assert a["bridge"]["borrowing_base"]["delta"] == base
    assert a["example"]["question"] and a["example"]["story"]
    from hashlib import sha256

    for side, period in [("opening", "before"), ("closing", "after")]:
        raw = c.get(f"/api/examples/{name}/{side}.csv")
        assert raw.status_code == 200
        assert sha256(raw.content).hexdigest() == a[period]["source_sha256"]
        manifest = c.get(f"/api/examples/{name}/{side}.json").json()
        assert manifest == a[period]["manifest"]
    if name == "mapped-rename":
        assert a["change_review"]["rows"][0]["explicit_rename"]
    packet = c.post("/api/surveillance", data={"example": name, "output_format": "html"})
    assert packet.status_code == 200 and a["change_review"]["review_id"] in packet.text


def test_examples_fail_closed_when_unknown_or_mixed_with_uploads():
    c = TestClient(app, base_url="http://127.0.0.1")
    assert c.post("/api/surveillance", data={"example": "../other"}).status_code == 400
    files, data = uploaded()
    assert (
        c.post(
            "/api/surveillance", files=files, data={**data, "example": "denial-input"}
        ).status_code
        == 400
    )
