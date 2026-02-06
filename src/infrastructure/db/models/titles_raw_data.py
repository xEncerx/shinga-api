from sqlmodel import SQLModel, Field, Column, DateTime, func, Index, UniqueConstraint
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import Enum as SQLEnum

from datetime import datetime, timezone
from typing import Any

from src.domain.models.services import ConsolidationStatus
from src.domain.models.source import Source


class TitleRawDataDBModel(SQLModel, table=True):
    __tablename__ = "titles_raw_data"  # type: ignore

    id: int | None = Field(default=None, primary_key=True, index=True)

    master_title_id: int | None = Field(
        default=None,
        foreign_key="titles.id",
        index=True,
        description="Reference to consolidated master title",
    )

    # === Source information ===
    source: Source = Field(
        sa_column=Column(SQLEnum(Source), nullable=False, index=True)
    )
    external_id: str = Field(
        index=True,
        description="ID of the title in the source system",
    )
    source_url: str | None = Field(
        default=None,
        description="Direct URL to the title on the source",
    )
    is_deleted: bool = Field(
        default=False,
        index=True,
        description="Marks if title was deleted/hidden on source",
    )

    # === Raw data ===
    raw_data: dict[str, Any] = Field(
        default={},
        sa_type=JSONB,
        description="Serialized SourceTitleData in JSONB format",
    )

    # === Consolidation info ===
    consolidation_status: ConsolidationStatus = Field(
        sa_column=Column(
            SQLEnum(ConsolidationStatus),
            default=ConsolidationStatus.PENDING,
            index=True,
        ),
    )
    consolidation_detail: str | None = Field(
        default=None,
        description="Additional details about the consolidation process",
    )

    # === Timestamps ===
    fetched_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            index=True,
        ),
        default_factory=lambda: datetime.now(timezone.utc),
        description="When data was first fetched from source",
    )
    last_verified_at: datetime = Field(
        sa_column=Column(
            DateTime(timezone=True),
            nullable=False,
            server_default=func.now(),
            onupdate=func.now(),
        ),
        default_factory=lambda: datetime.now(timezone.utc),
        description="Last time parser verified this record (even if unchanged)",
    )

    extended_data: dict[str, Any] = Field(
        default={},
        sa_type=JSONB,
        description="Additional metadata about the fetching/parsing process",
    )

    __table_args__ = (
        # Unique constraint: one external_id per source
        UniqueConstraint("source", "external_id", name="uq_source_external_id"),
        # Index for searching unmapped sources
        Index(
            "idx_source_data_unmapped",
            "master_title_id",
            postgresql_where=Column("master_title_id").is_(None),
        ),
        # Composite index for consolidation processing
        Index(
            "ix_raw_consolidation_pending",
            "consolidation_status",
            "fetched_at",
            postgresql_where=Column("consolidation_status")
            == ConsolidationStatus.PENDING.name,
        ),
        # Composite index for finding raw titles by master_title_id (for updates)
        Index(
            "ix_raw_master_not_deleted",
            "master_title_id",
            "is_deleted",
            postgresql_where=Column("is_deleted") == False,
        ),
        # GIN index for JSONB raw_data (for querying specific fields inside JSONB)
        Index(
            "ix_raw_data_gin",
            "raw_data",
            postgresql_using="gin",
        ),
    )
