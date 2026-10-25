from collections.abc import Sequence

from alembic import op
import sqlalchemy as sa


revision: str = "20261025_03"
down_revision: str | None = "20261017_02"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)
    op.add_column("transactions", sa.Column("user_id", sa.Integer(), nullable=True))
    op.create_foreign_key(
        "fk_transactions_user_id_users",
        "transactions",
        "users",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_index("ix_transactions_user_id", "transactions", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_transactions_user_id", table_name="transactions")
    op.drop_constraint(
        "fk_transactions_user_id_users",
        "transactions",
        type_="foreignkey",
    )
    op.drop_column("transactions", "user_id")
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
