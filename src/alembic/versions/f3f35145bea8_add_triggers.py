"""add_triggers

Revision ID: f3f35145bea8_add_triggers
Revises: f3f35145bea8
Create Date: 2026-02-12 16:10:34.876598

"""

from typing import Sequence, Union

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f3f35145bea8_add_triggers"
down_revision: Union[str, Sequence[str], None] = "f3f35145bea8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")
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
