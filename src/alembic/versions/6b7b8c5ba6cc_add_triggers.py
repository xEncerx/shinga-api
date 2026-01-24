"""add_triggers

Revision ID: 6b7b8c5ba6cc_add_triggers
Revises: 6b7b8c5ba6cc
Create Date: 2026-01-23 19:27:32.792014

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "6b7b8c5ba6cc_add_triggers"
down_revision: Union[str, Sequence[str], None] = "6b7b8c5ba6cc"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # === Trigger for calculating search_vector on titles table ===
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_titles_search_vector()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.search_vector := to_tsvector('simple', COALESCE(NEW.search_text, ''));
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )
    op.execute(
        """
    CREATE TRIGGER titles_search_vector_update
        BEFORE INSERT OR UPDATE OF search_text ON titles
        FOR EACH ROW
        EXECUTE FUNCTION update_titles_search_vector();
    """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS titles_search_vector_update ON titles;")
    op.execute("DROP FUNCTION IF EXISTS update_titles_search_vector();")
