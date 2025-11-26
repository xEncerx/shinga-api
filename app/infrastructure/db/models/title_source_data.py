from sqlmodel import SQLModel, Field, Column, DateTime, func, Index
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Enum as SQLEnum

from datetime import datetime, timezone
from typing import Any

from app.domain.enums import SourceProvider, ConsolidationStatus


class TitleSourceData(SQLModel, table=True):
    """
    Model for storing raw data from each source.

    Contains all data received from the provider, unchanged.
    """

    __tablename__ = "title_source_data"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    # Connection to master title (can be None before consolidation)
    master_title_id: int | None = Field(
        default=None, foreign_key="titles.id", index=True
    )

    # Source data
    source_provider: SourceProvider = Field(
        sa_column=Column(
            SQLEnum(SourceProvider),
            nullable=False,
            index=True,
        )
    )
    source_id: str = Field(index=True, max_length=255)
    source_url: str | None = Field(default=None, max_length=1024)

    # Raw JSON data from provider
    raw_data: dict[str, Any] = Field(default={}, sa_type=JSONB)

    # Consolidation status
    consolidation_status: ConsolidationStatus = Field(
        default=ConsolidationStatus.PENDING,
        sa_column=Column(
            SQLEnum(ConsolidationStatus),
            nullable=False,
            index=True,
        ),
    )

    # Timestamps
    fetched_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            index=True,
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )
    last_verified_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
    )

    # Deletion flag from source
    is_deleted_from_source: bool = Field(default=False, index=True)

    # Versioning for change tracking
    version: int = Field(default=1, ge=1, index=True)

    # For storing parsing errors (if any)
    parse_error: str | None = Field(default=None)

    __table_args__ = (
        # Unique index for source_provider + source_id
        Index(
            "idx_source_data_provider_id",
            "source_provider",
            "source_id",
            unique=True,
        ),
        # Index for searching unmapped sources
        Index(
            "idx_source_data_unmapped",
            "master_title_id",
            postgresql_where=Column("master_title_id").is_(None),
        ),
        Index(
            "idx_source_data_pending",
            "consolidation_status",
            "fetched_at",
            postgresql_where=Column("consolidation_status")
            == ConsolidationStatus.PENDING.value.upper(),
        ),
        # GIN index for searching by raw_data (JSONB)
        Index(
            "idx_source_data_raw_data_gin",
            "raw_data",
            postgresql_using="gin",
        ),
        # Index for searching by mal_id in raw_data (for ExternalIdMatcher)
        Index(
            "idx_source_data_mal_id",
            func.jsonb_extract_path_text(Column("raw_data"), "mal_id"),
        ),
        # Partial index for is_deleted_from_source
        Index(
            "idx_source_data_deleted",
            "is_deleted_from_source",
            postgresql_where=Column("is_deleted_from_source") == True,
        ),
    )

    class Config:
        # PostgreSQL composite types
        arbitrary_types_allowed = True
