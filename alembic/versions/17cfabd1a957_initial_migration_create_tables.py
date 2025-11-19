"""Initial migration - create tables

Revision ID: 17cfabd1a957
Revises: 
Create Date: 2025-11-19 01:49:37.456799

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '17cfabd1a957'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create locais table
    op.create_table(
        'locais',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_locais_id'), 'locais', ['id'], unique=False)
    op.create_index('ix_locais_nome', 'locais', ['nome'], unique=True)

    # Create salas table
    op.create_table(
        'salas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('local_id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(length=100), nullable=False),
        sa.Column('capacidade', sa.Integer(), nullable=True),
        sa.Column('recursos', sa.Text(), nullable=True),
        sa.Column('ativo', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['local_id'], ['locais.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_salas_id'), 'salas', ['id'], unique=False)
    op.create_index('idx_sala_local_nome', 'salas', ['local_id', 'nome'], unique=False)

    # Create reservas table
    op.create_table(
        'reservas',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('local_id', sa.Integer(), nullable=False),
        sa.Column('sala_id', sa.Integer(), nullable=False),
        sa.Column('local', sa.String(length=100), nullable=False),
        sa.Column('sala', sa.String(length=100), nullable=False),
        sa.Column('data_inicio', sa.DateTime(timezone=True), nullable=False),
        sa.Column('data_fim', sa.DateTime(timezone=True), nullable=False),
        sa.Column('responsavel', sa.String(length=150), nullable=False),
        sa.Column('cafe', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('quantidade_cafe', sa.Integer(), nullable=True),
        sa.Column('descricao', sa.Text(), nullable=True),
        sa.Column('criado_por_email', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['local_id'], ['locais.id'], ),
        sa.ForeignKeyConstraint(['sala_id'], ['salas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_reservas_id'), 'reservas', ['id'], unique=False)
    op.create_index('idx_reserva_sala_datas', 'reservas', ['sala', 'data_inicio', 'data_fim'], unique=False)

    # Create function to automatically update updated_at
    op.execute("""
        CREATE OR REPLACE FUNCTION update_updated_at_column()
        RETURNS TRIGGER AS $$
        BEGIN
            NEW.updated_at = now();
            RETURN NEW;
        END;
        $$ language 'plpgsql';
    """)

    # Create triggers to update updated_at
    op.execute("""
        CREATE TRIGGER update_locais_updated_at BEFORE UPDATE ON locais
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_salas_updated_at BEFORE UPDATE ON salas
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)
    op.execute("""
        CREATE TRIGGER update_reservas_updated_at BEFORE UPDATE ON reservas
        FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
    """)


def downgrade() -> None:
    # Remove triggers
    op.execute("DROP TRIGGER IF EXISTS update_reservas_updated_at ON reservas;")
    op.execute("DROP TRIGGER IF EXISTS update_salas_updated_at ON salas;")
    op.execute("DROP TRIGGER IF EXISTS update_locais_updated_at ON locais;")
    
    # Remove function
    op.execute("DROP FUNCTION IF EXISTS update_updated_at_column();")
    
    # Remove indices and tables
    op.drop_index('idx_reserva_sala_datas', table_name='reservas')
    op.drop_index(op.f('ix_reservas_id'), table_name='reservas')
    op.drop_table('reservas')
    
    op.drop_index('idx_sala_local_nome', table_name='salas')
    op.drop_index(op.f('ix_salas_id'), table_name='salas')
    op.drop_table('salas')
    
    op.drop_index('ix_locais_nome', table_name='locais')
    op.drop_index(op.f('ix_locais_id'), table_name='locais')
    op.drop_table('locais')
