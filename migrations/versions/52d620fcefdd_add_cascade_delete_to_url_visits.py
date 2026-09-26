from alembic import op


# revision identifiers, used by Alembic.
revision = '52d620fcefdd'
down_revision = '87c21bb91315'
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        'url_visit_short_url_id_fkey',
        'url_visit',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'url_visit_short_url_id_fkey',
        'url_visit',
        'short_urls',
        ['short_url_id'],
        ['id'],
        ondelete='CASCADE'
    )


def downgrade():
    op.drop_constraint(
        'url_visit_short_url_id_fkey',
        'url_visit',
        type_='foreignkey'
    )

    op.create_foreign_key(
        'url_visit_short_url_id_fkey',
        'url_visit',
        'short_urls',
        ['short_url_id'],
        ['id']
    )