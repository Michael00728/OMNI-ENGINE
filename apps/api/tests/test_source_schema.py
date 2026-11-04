from datetime import date

import pytest
from pydantic import ValidationError

from omni_api.knowledge.sources import AuthorityClass, LegalForce, SourceRecord

BASE = {
    "source_id": "cfpb-fcra-guide-001",
    "title": "Fair Credit Reporting Act reference",
    "publisher": "Consumer Financial Protection Bureau",
    "canonical_url": "https://www.consumerfinance.gov/consumer-tools/credit-reports-and-scores/",
    "authority_class": AuthorityClass.EDUCATIONAL_MATERIAL,
    "legal_force": LegalForce.NON_BINDING,
    "jurisdiction": "United States",
    "publication_date": date(2024, 1, 1),
    "effective_date": date(2024, 1, 1),
    "content_sha256": "a" * 64,
}


def test_valid_source_preserves_authority_and_hash() -> None:
    source = SourceRecord.model_validate(BASE)
    assert source.authority_class is AuthorityClass.EDUCATIONAL_MATERIAL
    assert source.legal_force is LegalForce.NON_BINDING
    assert source.content_sha256 == "a" * 64


def test_http_source_is_rejected() -> None:
    with pytest.raises(ValidationError, match="HTTPS"):
        SourceRecord.model_validate({**BASE, "canonical_url": "http://example.gov/source"})


def test_invalid_hash_is_rejected() -> None:
    with pytest.raises(ValidationError, match="64 hexadecimal"):
        SourceRecord.model_validate({**BASE, "content_sha256": "not-a-hash"})


def test_effective_date_before_publication_date_is_rejected() -> None:
    with pytest.raises(ValidationError, match="cannot precede"):
        SourceRecord.model_validate({**BASE, "effective_date": date(2023, 12, 31)})


def test_unrecognized_fields_are_rejected() -> None:
    with pytest.raises(ValidationError, match="Extra inputs are not permitted"):
        SourceRecord.model_validate({**BASE, "consumer_ssn": "123-45-6789"})
