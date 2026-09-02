"""race external id

Revision ID: 9b284c584779
Revises: b17192f52c8a
Create Date: 2026-09-03 00:16:44.307344

"""
import re
import unicodedata
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel


# revision identifiers, used by Alembic.
revision: str = '9b284c584779'
down_revision: Union[str, Sequence[str], None] = 'b17192f52c8a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _slug(value: str) -> str:
    """Frozen copy of services.ingest.slugify - this migration must not change if that does."""
    ascii_value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode()
    return re.sub(r"[^a-z0-9]+", "_", ascii_value.lower()).strip("_")


def upgrade() -> None:
    """Upgrade schema."""
    # Nullable first, so the column can be added to a table that already has rows.
    op.add_column('race', sa.Column('external_id', sqlmodel.sql.sqltypes.AutoString(), nullable=True))

    bind = op.get_bind()
    for row in bind.execute(sa.text("select id, season, name from race")).fetchall():
        bind.execute(
            sa.text("update race set external_id = :external_id where id = :id"),
            {"external_id": f"{row.season}_{_slug(row.name)}", "id": row.id},
        )

    op.alter_column('race', 'external_id', nullable=False)
    op.drop_constraint(op.f('race_season_round_key'), 'race', type_='unique')
    op.create_index(op.f('ix_race_external_id'), 'race', ['external_id'], unique=True)


def downgrade() -> None:
    """Downgrade schema. Fails if any season now has two races on the same round."""
    op.drop_index(op.f('ix_race_external_id'), table_name='race')
    op.create_unique_constraint(op.f('race_season_round_key'), 'race', ['season', 'round'], postgresql_nulls_not_distinct=False)
    op.drop_column('race', 'external_id')
