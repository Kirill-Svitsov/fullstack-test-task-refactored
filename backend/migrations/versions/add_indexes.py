"""add indexes

Revision ID: add_indexes
Revises: 0d6439d2e79f
Create Date: 2026-07-12 14:00:00.000000

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "add_indexes"
down_revision: Union[str, Sequence[str], None] = "0d6439d2e79f"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Индексы для таблицы files
    op.create_index("idx_files_created_at", "files", ["created_at"])
    op.create_index("idx_files_processing_status", "files", ["processing_status"])
    op.create_index("idx_files_requires_attention", "files", ["requires_attention"])

    # Индексы для таблицы alerts
    op.create_index("idx_alerts_file_id", "alerts", ["file_id"])
    op.create_index("idx_alerts_level", "alerts", ["level"])
    op.create_index("idx_alerts_created_at", "alerts", ["created_at"])


def downgrade() -> None:
    op.drop_index("idx_alerts_created_at", table_name="alerts")
    op.drop_index("idx_alerts_level", table_name="alerts")
    op.drop_index("idx_alerts_file_id", table_name="alerts")
    op.drop_index("idx_files_requires_attention", table_name="files")
    op.drop_index("idx_files_processing_status", table_name="files")
    op.drop_index("idx_files_created_at", table_name="files")
