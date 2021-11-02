from typing import Optional

from sqlalchemy.orm import Session

from app.crud.base import CRUDBase
from app.models.user_role import UserRole
from app.schemas.user_role import UserRoleCreate, UserRoleUpdate


class CRUDUserRole(CRUDBase[UserRole, UserRoleCreate, UserRoleUpdate]):
    def get_by_user_id(self, db: Session, *, user_id: int) -> Optional[UserRole]:
        return db.query(self.model).filter(UserRole.user_id == user_id).first()


user_role = CRUDUserRole(UserRole)
