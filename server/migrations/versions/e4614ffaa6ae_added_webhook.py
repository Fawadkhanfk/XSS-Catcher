"""Added webhook

Revision ID: e4614ffaa6ae
Revises: f38564e35d62
Create Date: 2021-03-30 21:31:36.233752

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e4614ffaa6ae"
down_revision = "f38564e35d62"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("client", schema=None) as batch_op:
        batch_op.add_column(sa.Column("webhook_url", sa.Text(), nullable=True))

    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.add_column(sa.Column("webhook_url", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("mail_to", sa.Text(), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("settings", schema=None) as batch_op:
        batch_op.drop_column("webhook_url")
        batch_op.drop_column("mail_to")

    with op.batch_alter_table("client", schema=None) as batch_op:
        batch_op.drop_column("webhook_url")

    # ### end Alembic commands ###
