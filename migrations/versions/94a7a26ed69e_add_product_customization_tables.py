"""Add product customization tables

Revision ID: 94a7a26ed69e
Revises: 16d082625264
Create Date: 2021-10-16 23:42:38.256337

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '94a7a26ed69e'
down_revision = '16d082625264'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('customizations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('price', sa.Float(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('products_customizations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('customization_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['customization_id'], ['customizations.id'], ),
    sa.ForeignKeyConstraint(['product_id'], ['products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('order_products_customizations',
    sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
    sa.Column('order_product_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('customization_id', postgresql.UUID(as_uuid=True), nullable=True),
    sa.Column('created_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.Column('updated_at', sa.DateTime(), server_default=sa.text('now()'), nullable=True),
    sa.ForeignKeyConstraint(['customization_id'], ['customizations.id'], ),
    sa.ForeignKeyConstraint(['order_product_id'], ['orders_products.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('order_products_customizations')
    op.drop_table('products_customizations')
    op.drop_table('customizations')
    # ### end Alembic commands ###
