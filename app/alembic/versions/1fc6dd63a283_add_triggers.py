"""add_triggers

Revision ID: 1fc6dd63a283_add_triggers
Revises: 1fc6dd63a283
Create Date: 2025-11-16 17:43:51.791710

"""

from typing import Sequence, Union
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "1fc6dd63a283_add_triggers"
down_revision: Union[str, None] = "1fc6dd63a283"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add triggers and functions."""
    # Search vector function and trigger
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_title_search_vector()
    RETURNS TRIGGER AS $$
    BEGIN
        NEW.search_vector := 
            setweight(to_tsvector('russian', COALESCE(NEW.name_ru, '')), 'A') ||
            setweight(to_tsvector('english', COALESCE(NEW.name_en, '')), 'B');
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER title_search_vector_update
        BEFORE INSERT OR UPDATE ON titles
        FOR EACH ROW
        EXECUTE FUNCTION update_title_search_vector();
    """
    )

    # Ratings update function and trigger
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_ratings_trigger()
    RETURNS TRIGGER AS $$
    DECLARE
        old_rating INTEGER := 0;
        new_rating INTEGER := 0;
        user_current_votes INTEGER := 0;
        user_current_avg DECIMAL := 0;
        title_current_count INTEGER := 0;
        title_current_sum DECIMAL := 0;
    BEGIN
        -- Get old and new ratings
        IF TG_OP = 'DELETE' THEN
            old_rating := OLD.user_rating;
            new_rating := 0;
        ELSIF TG_OP = 'INSERT' THEN
            old_rating := 0;
            new_rating := NEW.user_rating;
        ELSE -- UPDATE
            old_rating := OLD.user_rating;
            new_rating := NEW.user_rating;
        END IF;

        -- Skip if ratings didn't change or both are 0
        IF old_rating = new_rating THEN
            IF TG_OP = 'DELETE' THEN
                RETURN OLD;
            ELSE
                RETURN NEW;
            END IF;
        END IF;

        -- Determine user_id and title_id based on operation
        DECLARE
            target_user_id INTEGER;
            target_title_id INTEGER;
        BEGIN
            IF TG_OP = 'DELETE' THEN
                target_user_id := OLD.user_id;
                target_title_id := OLD.title_id;
            ELSE
                target_user_id := NEW.user_id;
                target_title_id := NEW.title_id;
            END IF;

            -- Get current user stats
            SELECT count_votes, avg_rating INTO user_current_votes, user_current_avg
            FROM users WHERE id = target_user_id;

            -- Update user statistics
            IF old_rating = 0 AND new_rating > 0 THEN
                -- Add new rating
                UPDATE users SET 
                    count_votes = count_votes + 1,
                    avg_rating = CASE 
                        WHEN count_votes = 0 THEN new_rating::DECIMAL
                        ELSE (avg_rating * count_votes + new_rating) / (count_votes + 1)
                    END
                WHERE id = target_user_id;
                
            ELSIF old_rating > 0 AND new_rating = 0 THEN
                -- Remove rating
                UPDATE users SET 
                    count_votes = GREATEST(count_votes - 1, 0),
                    avg_rating = CASE 
                        WHEN count_votes <= 1 THEN 0
                        ELSE (avg_rating * count_votes - old_rating) / (count_votes - 1)
                    END
                WHERE id = target_user_id;
                
            ELSIF old_rating > 0 AND new_rating > 0 THEN
                -- Update existing rating
                UPDATE users SET 
                    avg_rating = CASE 
                        WHEN count_votes = 0 THEN new_rating::DECIMAL
                        ELSE (avg_rating * count_votes - old_rating + new_rating) / count_votes
                    END
                WHERE id = target_user_id;
            END IF;

            -- Get current title stats
            SELECT in_app_scored_by, 
                COALESCE(in_app_rating * in_app_scored_by, 0) as current_sum
            INTO title_current_count, title_current_sum
            FROM titles WHERE id = target_title_id;

            -- Update title statistics
            IF old_rating = 0 AND new_rating > 0 THEN
                -- Add new rating to title
                UPDATE titles SET 
                    in_app_scored_by = in_app_scored_by + 1,
                    in_app_rating = CASE 
                        WHEN in_app_scored_by = 0 THEN new_rating::DECIMAL
                        ELSE (title_current_sum + new_rating) / (in_app_scored_by + 1)
                    END
                WHERE id = target_title_id;
                
            ELSIF old_rating > 0 AND new_rating = 0 THEN
                -- Remove title rating
                UPDATE titles SET 
                    in_app_scored_by = GREATEST(in_app_scored_by - 1, 0),
                    in_app_rating = CASE 
                        WHEN in_app_scored_by <= 1 THEN 0
                        ELSE (title_current_sum - old_rating) / (in_app_scored_by - 1)
                    END
                WHERE id = target_title_id;
                
            ELSIF old_rating > 0 AND new_rating > 0 THEN
                -- Update existing title rating
                UPDATE titles SET 
                    in_app_rating = CASE 
                        WHEN in_app_scored_by = 0 THEN new_rating::DECIMAL
                        ELSE (title_current_sum - old_rating + new_rating) / in_app_scored_by
                    END
                WHERE id = target_title_id;
            END IF;
        END;

        -- Return appropriate record
        IF TG_OP = 'DELETE' THEN
            RETURN OLD;
        ELSE
            RETURN NEW;
        END IF;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER rating_update_trigger
        AFTER INSERT OR UPDATE OF user_rating OR DELETE
        ON user_titles
        FOR EACH ROW
        EXECUTE FUNCTION update_ratings_trigger();
    """
    )

    # Bookmarks count function and trigger
    op.execute(
        """
    CREATE OR REPLACE FUNCTION update_user_bookmarks_count()
    RETURNS TRIGGER AS $$
    BEGIN
        IF TG_OP = 'INSERT' THEN
            UPDATE users 
            SET count_bookmarks = jsonb_set(
                jsonb_set(
                    COALESCE(count_bookmarks, '{}'::jsonb),
                    '{total}',
                    to_jsonb(COALESCE((count_bookmarks->>'total')::int, 0) + 1)
                ),
                ARRAY[LOWER(NEW.bookmark::text)],
                to_jsonb(COALESCE((count_bookmarks->>LOWER(NEW.bookmark::text))::int, 0) + 1)
            )
            WHERE id = NEW.user_id;
            
            RETURN NEW;
        END IF;
        
        IF TG_OP = 'UPDATE' THEN
            IF OLD.bookmark != NEW.bookmark THEN
                UPDATE users 
                SET count_bookmarks = jsonb_set(
                    jsonb_set(
                        COALESCE(count_bookmarks, '{}'::jsonb),
                        ARRAY[LOWER(OLD.bookmark::text)],
                        to_jsonb(GREATEST(COALESCE((count_bookmarks->>LOWER(OLD.bookmark::text))::int, 0) - 1, 0))
                    ),
                    ARRAY[LOWER(NEW.bookmark::text)],
                    to_jsonb(COALESCE((count_bookmarks->>LOWER(NEW.bookmark::text))::int, 0) + 1)
                )
                WHERE id = NEW.user_id;
            END IF;
            
            RETURN NEW;
        END IF;
        
        IF TG_OP = 'DELETE' THEN
            UPDATE users 
            SET count_bookmarks = jsonb_set(
                jsonb_set(
                    COALESCE(count_bookmarks, '{}'::jsonb),
                    '{total}',
                    to_jsonb(GREATEST(COALESCE((count_bookmarks->>'total')::int, 0) - 1, 0))
                ),
                ARRAY[LOWER(OLD.bookmark::text)],
                to_jsonb(GREATEST(COALESCE((count_bookmarks->>LOWER(OLD.bookmark::text))::int, 0) - 1, 0))
            )
            WHERE id = OLD.user_id;
            
            RETURN OLD;
        END IF;
        
        RETURN NULL;
    END;
    $$ LANGUAGE plpgsql;   
    """
    )

    op.execute(
        """
    CREATE TRIGGER trigger_update_user_bookmarks_count
        AFTER INSERT OR UPDATE OR DELETE
        ON user_titles
        FOR EACH ROW
        EXECUTE FUNCTION update_user_bookmarks_count();
    """
    )


def downgrade() -> None:
    """Remove triggers and functions."""
    # Drop triggers first
    op.execute("DROP TRIGGER IF EXISTS title_search_vector_update ON titles")
    op.execute("DROP TRIGGER IF EXISTS rating_update_trigger ON user_titles")
    op.execute(
        "DROP TRIGGER IF EXISTS trigger_update_user_bookmarks_count ON user_titles"
    )

    # Then drop functions
    op.execute("DROP FUNCTION IF EXISTS update_title_search_vector()")
    op.execute("DROP FUNCTION IF EXISTS update_ratings_trigger()")
    op.execute("DROP FUNCTION IF EXISTS update_user_bookmarks_count()")
