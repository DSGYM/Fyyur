"""empty message

Revision ID: 1bbd607d5386
Revises: 148fdad6b928
Create Date: 2020-06-03 19:40:28.171945

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "1bbd607d5386"
down_revision = "148fdad6b928"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "Artist", "seeking_talent", existing_type=sa.BOOLEAN(), nullable=True
    )
    # ### end Alembic commands ###

    op.execute("UPDATE Artist SET seeking_talent = False WHERE seeking_talent IS NULL")
    op.update_column("Artist", "seeking_talent", nullable=False)


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column(
        "Artist", "seeking_talent", existing_type=sa.BOOLEAN(), nullable=True
    )
    # ### end Alembic commands ###
