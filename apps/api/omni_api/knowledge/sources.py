"""Source metadata schema and authority taxonomy.

This module stores provenance metadata only. It does not determine legal applicability.
"""

import re
from datetime import date, datetime, timezone
from enum import StrEnum
from typing import Annotated
from urllib.parse import urlsplit

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator


class AuthorityClass(StrEnum):
    STATUTE = "statute"
    REGULATION = "regulation"
    COURT_DECISION = "court_decision"
    AGENCY_GUIDANCE = "agency_guidance"
    ENFORCEMENT_ACTION = "enforcement_action"
    EDUCATIONAL_MATERIAL = "educational_material"
    INDUSTRY_STANDARD = "industry_standard"


class LegalForce(StrEnum):
    BINDING = "binding"
    NON_BINDING = "non_binding"
    INTERPRETIVE = "interpretive"
    NOT_APPLICABLE = "not_applicable"
    UNASSESSED = "unassessed"


class SourceRecord(BaseModel):
    """Version-aware, citable metadata for an authoritative or contextual source."""

    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    source_id: Annotated[str, Field(min_length=3, max_length=120)]
    title: Annotated[str, Field(min_length=3, max_length=500)]
    publisher: Annotated[str, Field(min_length=2, max_length=200)]
    canonical_url: str
    authority_class: AuthorityClass
    legal_force: LegalForce = LegalForce.UNASSESSED
    jurisdiction: Annotated[str, Field(min_length=2, max_length=100)]
    publication_date: date | None = None
    effective_date: date | None = None
    retrieved_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    content_sha256: str
    citation_locator: str | None = Field(default=None, max_length=500)

    @field_validator("canonical_url")
    @classmethod
    def require_https_url(cls, value: str) -> str:
        parsed = urlsplit(value)
        if parsed.scheme != "https" or not parsed.hostname:
            raise ValueError("canonical_url must be a valid HTTPS URL with a hostname")
        if parsed.username or parsed.password:
            raise ValueError("canonical_url must not contain embedded credentials")
        return value

    @field_validator("content_sha256")
    @classmethod
    def require_sha256(cls, value: str) -> str:
        if not re.fullmatch(r"[a-fA-F0-9]{64}", value):
            raise ValueError("content_sha256 must contain exactly 64 hexadecimal characters")
        return value.lower()

    @model_validator(mode="after")
    def validate_dates(self) -> "SourceRecord":
        if self.publication_date and self.effective_date:
            if self.effective_date < self.publication_date:
                raise ValueError("effective_date cannot precede publication_date")
        return self
