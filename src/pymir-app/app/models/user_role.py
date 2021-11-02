from sqlalchemy import Column, Integer, UniqueConstraint

from app.db.base_class import Base


class UserRole(Base):
    __tablename__ = "role"
    user_id = Column(Integer, index=True, nullable=False)
    role_id = Column(Integer, index=True, nullable=False)

    __table_args__ = UniqueConstraint("user_id", "role_id", name="unique_user_role")
