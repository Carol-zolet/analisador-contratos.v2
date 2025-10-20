"""add analises_cache table

Revision ID: 20251020_add_analise_cache
Revises: 01961428e8db
Create Date: 2025-10-20
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20251020_add_analise_cache'
down_revision = '01961428e8db'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'analises_cache',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('hash_arquivo', sa.String(), nullable=False, index=True),
        sa.Column('nome_arquivo', sa.String(), nullable=False),
        sa.Column('resumo_texto', sa.String()),
        sa.Column('resultado_regras', sa.JSON()),
        sa.Column('analise_ia', sa.String()),
        sa.Column('data_analise', sa.DateTime(), nullable=True),
    )
    op.create_unique_constraint('uq_hash_arquivo', 'analises_cache', ['hash_arquivo'])


def downgrade() -> None:
    op.drop_constraint('uq_hash_arquivo', 'analises_cache', type_='unique')
    op.drop_table('analises_cache')
