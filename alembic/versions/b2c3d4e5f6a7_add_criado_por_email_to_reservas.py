"""add criado_por_email to reservas

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2025-01-20 13:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add criado_por_email column if it doesn't exist
    # Using PostgreSQL DO block to make migration idempotent
    op.execute("""
        DO $$ 
        BEGIN
            IF NOT EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'reservas' 
                AND column_name = 'criado_por_email'
            ) THEN
                ALTER TABLE reservas 
                ADD COLUMN criado_por_email VARCHAR(255);
            END IF;
        END $$;
    """)


def downgrade() -> None:
    # Remove criado_por_email column if it exists
    op.execute("""
        DO $$ 
        BEGIN
            IF EXISTS (
                SELECT 1 
                FROM information_schema.columns 
                WHERE table_name = 'reservas' 
                AND column_name = 'criado_por_email'
            ) THEN
                ALTER TABLE reservas 
                DROP COLUMN criado_por_email;
            END IF;
        END $$;
    """)

