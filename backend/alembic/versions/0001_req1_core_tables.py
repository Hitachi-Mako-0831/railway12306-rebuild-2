from alembic import op
import sqlalchemy as sa


revision = "0001_req1_core_tables"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'train_type') THEN
                CREATE TYPE train_type AS ENUM ('G', 'D', 'Z');
            END IF;
        END$$;
        """
    )
    op.execute(
        """
        DO $$
        BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'seat_type') THEN
                CREATE TYPE seat_type AS ENUM ('first_class', 'second_class', 'soft_sleeper', 'hard_sleeper');
            END IF;
        END$$;
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS stations (
            id SERIAL PRIMARY KEY,
            name VARCHAR(100) NOT NULL UNIQUE,
            city VARCHAR(50) NOT NULL,
            pinyin VARCHAR(100),
            code VARCHAR(20) UNIQUE,
            is_hot BOOLEAN NOT NULL DEFAULT false
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS trains (
            id SERIAL PRIMARY KEY,
            train_number VARCHAR(50) NOT NULL UNIQUE,
            train_type train_type NOT NULL,
            from_station_id INTEGER NOT NULL REFERENCES stations(id),
            to_station_id INTEGER NOT NULL REFERENCES stations(id),
            departure_time TIME NOT NULL,
            arrival_time TIME NOT NULL,
            duration_minutes INTEGER NOT NULL,
            arrival_day_offset INTEGER NOT NULL DEFAULT 0
        )
        """
    )

    op.execute(
        """
        CREATE TABLE IF NOT EXISTS seats (
            id SERIAL PRIMARY KEY,
            train_id INTEGER NOT NULL REFERENCES trains(id),
            travel_date DATE NOT NULL,
            seat_type seat_type NOT NULL,
            total INTEGER NOT NULL,
            available INTEGER NOT NULL,
            CONSTRAINT uq_seat_train_date_type UNIQUE (train_id, travel_date, seat_type)
        )
        """
    )


def downgrade() -> None:
    op.execute("DROP TABLE IF EXISTS seats")
    op.execute("DROP TABLE IF EXISTS trains")
    op.execute("DROP TABLE IF EXISTS stations")
