"""Added tags

Revision ID: f38564e35d62
Revises: 7dd0f5e2bfb9
Create Date: 2021-03-07 18:57:26.297863

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.orm import Session
from app.models import XSS
import json


# revision identifiers, used by Alembic.
revision = "f38564e35d62"
down_revision = "7dd0f5e2bfb9"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("XSS", schema=None) as batch_op:
        batch_op.add_column(sa.Column("tags", sa.Text(), server_default="[]", nullable=False))

    conn = op.get_bind()
    session = Session(bind=conn)

    for xss in session.query(XSS).all():
        xss_data = json.loads(xss.data)
        for element_name, element_value in xss_data.items():
            if element_name in ["local_storage", "session_storage", "cookies"]:
                if isinstance(element_value, list):
                    new_data = {}
                    for single_element in element_value:
                        new_data.update(single_element)
                    xss_data[element_name] = new_data
        xss.data = json.dumps(xss_data)

        xss_headers = json.loads(xss.headers)
        if isinstance(xss_headers, list):
            new_headers = {}
            for header in xss_headers:
                new_headers.update(header)
            xss.headers = json.dumps(new_headers)

    session.commit()

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("XSS", schema=None) as batch_op:
        batch_op.drop_column("tags")

    # ### end Alembic commands ###