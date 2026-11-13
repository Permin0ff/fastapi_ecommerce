"""Add reviews and product rating.

Revision ID: b49a102dc317
Revises: 10773efc166d
"""
from alembic import op
import sqlalchemy as sa

revision = "b49a102dc317"
down_revision = "10773efc166d"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("products", sa.Column("rating", sa.Float(), server_default=sa.text("0"), nullable=False))
    op.create_table(
        "reviews",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False),
        sa.Column("product_id", sa.Integer(), sa.ForeignKey("products.id"), nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("comment_date", sa.DateTime(), server_default=sa.func.now(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
        sa.CheckConstraint("grade >= 1 AND grade <= 5", name="ck_reviews_grade"),
    )
    op.create_index("ix_reviews_product_id_is_active", "reviews", ["product_id", "is_active"])


def downgrade() -> None:
    op.drop_index("ix_reviews_product_id_is_active", table_name="reviews")
    op.drop_table("reviews")
    op.drop_column("products", "rating")
