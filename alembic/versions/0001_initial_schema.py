"""Initial graph schema: programs, assets, relations, jobs, findings, settings."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0001_initial"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "programs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("platform", sa.String(length=16), nullable=False),
        sa.Column("reward_type", sa.String(length=64), nullable=True),
        sa.Column(
            "in_scope",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "out_scope",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "settings",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_programs_name"), "programs", ["name"], unique=False)

    op.create_table(
        "framework_settings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(length=64), nullable=False),
        sa.Column(
            "api_keys",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "rate_limits",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "notification_webhooks",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    op.create_table(
        "assets",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("program_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("type", sa.String(length=32), nullable=False),
        sa.Column("value", sa.String(length=2048), nullable=False),
        sa.Column(
            "metadata",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'{}'::jsonb"),
            nullable=False,
        ),
        sa.Column(
            "first_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["program_id"], ["programs.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("program_id", "type", "value", name="uq_assets_program_type_value"),
    )
    op.create_index(op.f("ix_assets_program_id"), "assets", ["program_id"], unique=False)
    op.create_index(op.f("ix_assets_type"), "assets", ["type"], unique=False)
    op.create_index(op.f("ix_assets_value"), "assets", ["value"], unique=False)

    op.create_table(
        "asset_relations",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("parent_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("child_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("relation_type", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["child_id"], ["assets.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["parent_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint(
            "parent_id",
            "child_id",
            "relation_type",
            name="uq_asset_relations_parent_child_type",
        ),
    )
    op.create_index(op.f("ix_asset_relations_child_id"), "asset_relations", ["child_id"], unique=False)
    op.create_index(op.f("ix_asset_relations_parent_id"), "asset_relations", ["parent_id"], unique=False)
    op.create_index(
        op.f("ix_asset_relations_relation_type"),
        "asset_relations",
        ["relation_type"],
        unique=False,
    )

    op.create_table(
        "jobs",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("tool_name", sa.String(length=128), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("target_asset_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("start_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("end_time", sa.DateTime(timezone=True), nullable=True),
        sa.Column("raw_output_link", sa.String(length=2048), nullable=True),
        sa.ForeignKeyConstraint(["target_asset_id"], ["assets.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_jobs_status"), "jobs", ["status"], unique=False)
    op.create_index(op.f("ix_jobs_target_asset_id"), "jobs", ["target_asset_id"], unique=False)
    op.create_index(op.f("ix_jobs_tool_name"), "jobs", ["tool_name"], unique=False)

    op.create_table(
        "findings",
        sa.Column("id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("asset_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("tool_source", sa.String(length=128), nullable=False),
        sa.Column("severity", sa.String(length=32), nullable=False),
        sa.Column("title", sa.String(length=512), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("raw_output_link", sa.String(length=2048), nullable=True),
        sa.Column("dedupe_hash", sa.String(length=64), nullable=False),
        sa.Column("vulnerability_type", sa.String(length=255), nullable=False),
        sa.Column("endpoint", sa.String(length=2048), nullable=True),
        sa.Column(
            "last_seen",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["asset_id"], ["assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("dedupe_hash"),
    )
    op.create_index(op.f("ix_findings_asset_id"), "findings", ["asset_id"], unique=False)
    op.create_index(op.f("ix_findings_dedupe_hash"), "findings", ["dedupe_hash"], unique=False)
    op.create_index(op.f("ix_findings_severity"), "findings", ["severity"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_findings_severity"), table_name="findings")
    op.drop_index(op.f("ix_findings_dedupe_hash"), table_name="findings")
    op.drop_index(op.f("ix_findings_asset_id"), table_name="findings")
    op.drop_table("findings")
    op.drop_index(op.f("ix_jobs_tool_name"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_target_asset_id"), table_name="jobs")
    op.drop_index(op.f("ix_jobs_status"), table_name="jobs")
    op.drop_table("jobs")
    op.drop_index(op.f("ix_asset_relations_relation_type"), table_name="asset_relations")
    op.drop_index(op.f("ix_asset_relations_parent_id"), table_name="asset_relations")
    op.drop_index(op.f("ix_asset_relations_child_id"), table_name="asset_relations")
    op.drop_table("asset_relations")
    op.drop_index(op.f("ix_assets_value"), table_name="assets")
    op.drop_index(op.f("ix_assets_type"), table_name="assets")
    op.drop_index(op.f("ix_assets_program_id"), table_name="assets")
    op.drop_table("assets")
    op.drop_table("framework_settings")
    op.drop_index(op.f("ix_programs_name"), table_name="programs")
    op.drop_table("programs")
