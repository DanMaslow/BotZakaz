from alembic import op
import sqlalchemy as sa

revision = 'ae1027a6acf3'         # или любой ID, который у тебя в названии файла
down_revision = 'c5ad1516dc10'    # ← вот это ключевое
branch_labels = None
depends_on = None

def upgrade():
    op.add_column('clients',
        sa.Column('admin', sa.Boolean(), nullable=False, server_default=sa.text('false'))
    )

def downgrade():
    op.drop_column('clients', 'admin')