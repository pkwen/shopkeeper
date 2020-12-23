"""remove uuid from productcomponents and add onto products

Revision ID: a24f9b3315e6
Revises: d57417eb04f3
Create Date: 2020-12-22 15:47:07.586565

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'a24f9b3315e6'
down_revision = 'd57417eb04f3'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products', sa.Column('uuid', postgresql.UUID(as_uuid=True), nullable=False))
    op.create_unique_constraint(None, 'products', ['uuid'])
    op.drop_constraint('products_components_uuid_key', 'products_components', type_='unique')
    op.drop_column('products_components', 'uuid')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('products_components', sa.Column('uuid', postgresql.UUID(), autoincrement=False, nullable=False))
    op.create_unique_constraint('products_components_uuid_key', 'products_components', ['uuid'])
    op.drop_constraint(None, 'products', type_='unique')
    op.drop_column('products', 'uuid')
    # ### end Alembic commands ###