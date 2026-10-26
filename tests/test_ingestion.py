import csv
import io
import json

import pytest
from test_api import CSV

from cautum.ingestion import ALIASES, normalize_csv
from cautum.parser import DataError, parse_csv
from cautum.schema import CSV_COLUMNS

MAP = {k: v[-1] for k, v in ALIASES.items()}


def aliased():
    rows = list(csv.reader(io.StringIO(CSV.decode())))
    rows[0] = [MAP[k] for k in CSV_COLUMNS]
    output = io.StringIO()
    csv.writer(output).writerows([list(reversed(r)) for r in rows])
    return output.getvalue().encode()


def test_explicit_aliases_and_order_reconcile():
    assert parse_csv(normalize_csv(aliased(), MAP)) == parse_csv(CSV)
    from fastapi.testclient import TestClient

    from cautum.api import app

    r = TestClient(app, base_url="http://127.0.0.1").post(
        "/api/analyze",
        files={"file": ("safe.csv", aliased())},
        data={"mapping": json.dumps(MAP)},
    )
    assert r.status_code == 200
    assert r.json()["summary"]["gross_ar"] == 1934634


@pytest.mark.parametrize(
    "mapping",
    [
        {},
        [],
        {**MAP, "gross_ar": "denial_rate"},
        {**MAP, "denial_rate": "patient_name"},
    ],
)
def test_reject_incomplete_or_semantically_invalid_mapping(mapping):
    with pytest.raises(DataError):
        normalize_csv(aliased(), mapping)


def test_reject_extra_columns_without_dropping():
    with pytest.raises(DataError):
        normalize_csv(aliased().replace(b"borrower", b"patient_name,borrower", 1), MAP)


def test_reject_unconfirmed_denominators():
    with pytest.raises(DataError):
        normalize_csv(aliased().replace(b"collection_factor_pre_denial", b"collection_rate"), MAP)
