from alembic import op


revision = "a2"
down_revision = "0001_req1_core_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (
                SELECT 1
                FROM information_schema.table_constraints
                WHERE table_name = 'users'
                  AND constraint_type = 'UNIQUE'
                  AND constraint_name = 'uq_users_id_number'
            ) THEN
                ALTER TABLE users
                ADD CONSTRAINT uq_users_id_number UNIQUE (id_number);
            END IF;
        END$$;
        """
    )


def downgrade() -> None:
    op.execute(
        """
        ALTER TABLE users
        DROP CONSTRAINT IF EXISTS uq_users_id_number
        """
    )
