import uuid

from sqlalchemy import CheckConstraint, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, CreatedAtMixin


class Follow(CreatedAtMixin, Base):
    """`follower` sigue a `followee`. Dos alumnos que se siguen entre sí son amigos."""

    __tablename__ = "follows"
    __table_args__ = (CheckConstraint("follower_id <> followee_id", name="not_self"),)

    follower_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True
    )
    followee_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"), primary_key=True, index=True
    )
