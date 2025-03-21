"""Added new signup fields

Revision ID: a40f77ec72d7
Revises: 67fc0c83ba3d
Create Date: 2025-03-21 21:01:25.044071

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'a40f77ec72d7'
down_revision: Union[str, None] = '67fc0c83ba3d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ✅ Drop foreign key constraint before dropping the table
    op.drop_constraint("observations_audit_id_fkey", "observations", type_="foreignkey")
    
    # ✅ Now drop the tables safely
    op.drop_table("observations")
    op.drop_table("audits")


def downgrade() -> None:
    """Downgrade schema."""
    op.create_table('audits',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('vendor_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('site_name', sa.VARCHAR(length=255), autoincrement=False, nullable=False),
        sa.Column('audit_month', sa.DATE(), autoincrement=False, nullable=False),
        sa.Column('status', sa.VARCHAR(length=50), server_default=sa.text("'Pending'::character varying"), autoincrement=False, nullable=True),
        sa.Column('uploaded_documents', postgresql.ARRAY(sa.TEXT()), autoincrement=False, nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
        sa.PrimaryKeyConstraint('id', name='audits_pkey')
    )

    op.create_table('observations',
        sa.Column('id', sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column('audit_id', sa.INTEGER(), autoincrement=False, nullable=True),
        sa.Column('comment', sa.TEXT(), autoincrement=False, nullable=False),
        sa.Column('created_at', postgresql.TIMESTAMP(), server_default=sa.text('CURRENT_TIMESTAMP'), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(['audit_id'], ['audits.id'], name='observations_audit_id_fkey', ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id', name='observations_pkey')
    )
