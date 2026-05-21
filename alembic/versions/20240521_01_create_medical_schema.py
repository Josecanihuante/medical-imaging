"""create medical schema and knee_analyses table

Revision ID: 20240521_01
Revises: 
Create Date: 2024-05-21 09:40:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20240521_01'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create schema if not exists
    op.execute('CREATE SCHEMA IF NOT EXISTS medical')

    # Create table
    op.create_table(
        'knee_analyses',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('patient_id', sa.String(length=100), nullable=True),
        sa.Column('kl_grade', sa.SmallInt(), nullable=False),
        sa.Column('confidence', sa.Numeric(precision=5, scale=4), nullable=False),
        sa.Column('probabilities', postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column('model_version', sa.String(length=50), nullable=False, server_default='efficientnetv2_l_v1'),
        sa.Column('processing_time_ms', sa.Integer(), nullable=True),
        sa.Column('gradcam_stored', sa.Boolean(), nullable=False, server_default=sa.text('false')),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('created_at', postgresql.TIMESTAMP(timezone=True), nullable=False, server_default=sa.text('now()')),
        sa.Column('deleted_at', postgresql.TIMESTAMP(timezone=True), nullable=True),
        schema='medical'
    )
    # Create primary key constraint
    op.create_primary_key('pk_knee_analyses', 'knee_analyses', ['id'], schema='medical')
    # Create check constraint for kl_grade
    op.create_check_constraint(
        'ck_knee_analyses_kl_grade',
        'knee_analyses',
        sa.text('kl_grade BETWEEN 0 AND 4'),
        schema='medical'
    )


def downgrade() -> None:
    op.drop_table('knee_analyses', schema='medical')
    # Note: We are not dropping the schema in case there are other tables.
    # If you want to drop the schema, uncomment the following line:
    # op.execute('DROP SCHEMA IF EXISTS medical')