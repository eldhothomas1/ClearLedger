from alembic import op


revision = "20261017_02"
down_revision = "20261017_01"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_transactions_date", "transactions", ["date"])
    op.create_index("ix_transactions_category", "transactions", ["category"])


def downgrade() -> None:
    op.drop_index("ix_transactions_category", table_name="transactions")
    op.drop_index("ix_transactions_date", table_name="transactions")
