"""Base SQLAlchemy models and mixins."""
import uuid
from datetime import datetime
from typing import Annotated, Any

from sqlalchemy import BIGINT, Integer
from sqlalchemy.dialects.postgresql import UUID as PUUID
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql.functions import func

# Type annotations
int_pk = Annotated[int, mapped_column(Integer, primary_key=True, autoincrement=True)]
bigint_pk = Annotated[int, mapped_column(BIGINT, primary_key=True)]


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy models."""

    repr_cols_num = 6
    repr_cols: tuple[str, ...] = ()

    def __repr__(self) -> str:
        """String representation of model."""
        cols = []
        for idx, col in enumerate(self.__table__.columns.keys()):
            if col in self.repr_cols or idx < self.repr_cols_num:
                cols.append(f"{col}={getattr(self, col)}")

        return f"<{self.__class__.__name__} {', '.join(cols)}>"

    def to_dict(self) -> dict[str, Any]:
        """Convert model to dictionary."""
        return {col.name: getattr(self, col.name) for col in self.__table__.columns}


class TableNameMixin:
    """Mixin to auto-generate table name from class name."""

    @declared_attr.directive
    def __tablename__(cls) -> str:  # noqa
        """Generate table name as plural lowercase class name."""
        return cls.__name__.lower() + "s"


class UUIDMixin:
    """Mixin for UUID primary key."""

    id: Mapped[uuid.UUID] = mapped_column(
        PUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True
    )


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""

    created_at: Mapped[datetime] = mapped_column(
        server_default=func.now(), nullable=False, index=True
    )
    updated_at: Mapped[datetime | None] = mapped_column(
        onupdate=func.now(), nullable=True
    )
