"""Add SIVIGILA definitions for additional transmissible diseases."""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: str | None = "0004"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

SOURCE_SIVIGILA = "datos-gov-sivigila"

NEW_DEFINITIONS = (
    ("chikungunya-weekly-cases", "Casos semanales de chikungunya (SIVIGILA)", "217"),
    ("dengue-severe-weekly-cases", "Casos semanales de dengue grave (SIVIGILA)", "220"),
    ("hepatitis-a-weekly-cases", "Casos semanales de hepatitis A (SIVIGILA)", "330"),
    ("hepatitis-b-weekly-cases", "Casos semanales de hepatitis B (SIVIGILA)", "340"),
    ("typhoid-weekly-cases", "Casos semanales de fiebre tifoidea (SIVIGILA)", "320"),
)


def upgrade() -> None:
    definitions = sa.table(
        "health_indicator_definitions",
        sa.column("id", sa.String()),
        sa.column("name", sa.String()),
        sa.column("measurement_unit", sa.String()),
        sa.column("source_indicator_key", sa.String()),
        sa.column("source_id", sa.String()),
    )
    op.bulk_insert(
        definitions,
        [
            {
                "id": definition_id,
                "name": name,
                "measurement_unit": "cases",
                "source_indicator_key": event_code,
                "source_id": SOURCE_SIVIGILA,
            }
            for definition_id, name, event_code in NEW_DEFINITIONS
        ],
    )


def downgrade() -> None:
    ids = ", ".join(f"'{definition_id}'" for definition_id, _, _ in NEW_DEFINITIONS)
    op.execute(
        sa.text(f"DELETE FROM health_indicator_definitions WHERE id IN ({ids})"),
    )
