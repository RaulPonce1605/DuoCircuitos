"""intentos de repaso y evaluacion

Revision ID: b3c1d2e4f5a6
Revises: 7942016fd1e3
Create Date: 2026-11-26 14:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3c1d2e4f5a6'
down_revision: Union[str, Sequence[str], None] = '7942016fd1e3'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('lesson_attempts', sa.Column('node_id', sa.Integer(), nullable=True))
    # Los intentos que ya existen son todos de lección: su nodo es el de esa lección.
    op.execute(
        "UPDATE lesson_attempts AS a SET node_id = n.id FROM nodes AS n WHERE n.lesson_id = a.lesson_id"
    )
    op.alter_column('lesson_attempts', 'node_id', nullable=False)
    op.alter_column('lesson_attempts', 'lesson_id', existing_type=sa.INTEGER(), nullable=True)
    op.create_index(op.f('ix_lesson_attempts_node_id'), 'lesson_attempts', ['node_id'], unique=False)
    op.create_foreign_key(op.f('fk_lesson_attempts_node_id_nodes'), 'lesson_attempts', 'nodes', ['node_id'], ['id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DELETE FROM lesson_attempts WHERE lesson_id IS NULL")
    op.drop_constraint(op.f('fk_lesson_attempts_node_id_nodes'), 'lesson_attempts', type_='foreignkey')
    op.drop_index(op.f('ix_lesson_attempts_node_id'), table_name='lesson_attempts')
    op.alter_column('lesson_attempts', 'lesson_id', existing_type=sa.INTEGER(), nullable=False)
    op.drop_column('lesson_attempts', 'node_id')
