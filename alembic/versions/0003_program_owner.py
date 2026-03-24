"""Programs belong to a user (tenant isolation)."""

from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "0003_program_owner"
down_revision: Union[str, Sequence[str], None] = "0002_users"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "programs",
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), nullable=True),
    )
    op.create_index("ix_programs_owner_id", "programs", ["owner_id"], unique=False)

    conn = op.get_bind()
    user_count = conn.execute(sa.text("SELECT COUNT(*) FROM users")).scalar() or 0
    if user_count == 0:
        conn.execute(sa.text("DELETE FROM programs"))
    else:
        conn.execute(
            sa.text(
                """
                UPDATE programs
                SET owner_id = (SELECT id FROM users ORDER BY created_at ASC LIMIT 1)
                WHERE owner_id IS NULL
                """
            ),
        )

    op.alter_column("programs", "owner_id", nullable=False)
    op.create_foreign_key(
        "fk_programs_owner_id_users",
        "programs",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_programs_owner_id_users", "programs", type_="foreignkey")
    op.drop_index("ix_programs_owner_id", table_name="programs")
    op.drop_column("programs", "owner_id")
