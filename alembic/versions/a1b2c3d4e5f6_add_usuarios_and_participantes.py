"""add usuarios and participantes tables

Revision ID: a1b2c3d4e5f6
Revises: 17cfabd1a957
Create Date: 2025-01-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = '17cfabd1a957'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create usuarios table
    op.create_table(
        'usuarios',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('google_id', sa.String(length=255), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('nome', sa.String(length=255), nullable=False),
        sa.Column('foto_url', sa.String(length=500), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('last_login_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False)
    op.create_index('ix_usuarios_google_id', 'usuarios', ['google_id'], unique=True)
    op.create_index('ix_usuarios_email', 'usuarios', ['email'], unique=True)

    # Create participantes table
    op.create_table(
        'participantes',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('reserva_id', sa.Integer(), nullable=False),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('nome_manual', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['reserva_id'], ['reservas.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_participantes_id'), 'participantes', ['id'], unique=False)
    op.create_index('idx_participante_reserva', 'participantes', ['reserva_id'], unique=False)
    op.create_index('idx_participante_usuario', 'participantes', ['usuario_id'], unique=False)

    # Create trigger to update updated_at in usuarios
    op.execute("""
        CREATE TRIGGER update_usuarios_updated_at BEFORE UPDATE ON usuarios
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove trigger
    op.execute("DROP TRIGGER IF EXISTS update_usuarios_updated_at ON usuarios;")
    
    # Remove indices and tables
    op.drop_index('idx_participante_usuario', table_name='participantes')
    op.drop_index('idx_participante_reserva', table_name='participantes')
    op.drop_index(op.f('ix_participantes_id'), table_name='participantes')
    op.drop_table('participantes')
    
    op.drop_index('ix_usuarios_email', table_name='usuarios')
    op.drop_index('ix_usuarios_google_id', table_name='usuarios')
    op.drop_index(op.f('ix_usuarios_id'), table_name='usuarios')
    op.drop_table('usuarios')

