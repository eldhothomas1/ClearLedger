from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261112_05"
down_revision: str | None = "20261029_04"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.add_column(
        "transactions",
        sa.Column(
            "transaction_type",
            sa.String(length=20),
            server_default="expense",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("transactions", "transaction_type")
