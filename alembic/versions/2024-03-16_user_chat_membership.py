"""user-chat-membership

Revision ID: 79a270a02fd1
Revises: d881b503c0ae
Create Date: 2024-03-16 11:09:22.515742

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '79a270a02fd1'
down_revision = 'd881b503c0ae'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('user_tg_chat_membership',
    sa.Column('user_tg_id', sa.BigInteger(), nullable=False),
    sa.Column('chat_id', sa.BigInteger(), nullable=False),
    sa.Column('last_seen_at', sa.DateTime(), server_default=sa.text('now()'), nullable=False),
    sa.ForeignKeyConstraint(['user_tg_id'], ['user_tg.id'], name=op.f('user_tg_chat_membership_user_tg_id_fkey'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('user_tg_id', 'chat_id', name=op.f('user_tg_chat_membership_pkey'))
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('user_tg_chat_membership')
    # ### end Alembic commands ###
