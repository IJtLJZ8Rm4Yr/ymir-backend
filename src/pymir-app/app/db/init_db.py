import json

from sqlalchemy.orm import Session

from app import crud, schemas
from app.config import settings
from app.constants.role import Roles
from app.db import base  # noqa: F401

# make sure all SQL Alchemy models are imported (app.db.base) before initializing DB
# otherwise, SQL Alchemy might fail to initialize relationships properly
# for more details: https://github.com/tiangolo/full-stack-fastapi-postgresql/issues/28


def init_db(db: Session) -> None:
    # Tables should be created with Alembic migrations
    # But if you don't want to use migrations, create
    # the tables un-commenting the next line
    # Base.metadata.create_all(bind=engine)
    roles = crud.role.get_multi(db)
    if not roles:
        for role in [Roles.NORMAL, Roles.ADMIN, Roles.SUPER_ADMIN]:
            role_in = schemas.RoleCreate(name=role.name, description=role.description)
            crud.role.create(db, obj_in=role_in)

    user = crud.user.get_by_email(db, email=settings.FIRST_ADMIN)
    if not user:
        user_in = schemas.UserCreate(
            email=settings.FIRST_ADMIN,
            password=settings.FIRST_ADMIN_PASSWORD,
            is_admin=True,
        )
        user = crud.user.create(db, obj_in=user_in)  # noqa: F841
        admin_role = crud.role.get_by_name(db, name=Roles.ADMIN.name)
        assert admin_role, "missing role records"
        user_role_in = schemas.UserRoleCreate(user_id=user.id, role_id=admin_role.id)
        user_role = crud.user_role.create(db, obj_in=user_role_in)

    runtime = crud.runtime.get_multi_runtimes(db)
    if not runtime and settings.RUNTIMES:
        runtime_configs = json.loads(settings.RUNTIMES)
        for config in runtime_configs:
            runtime_in = schemas.RuntimeCreate(**config)
            crud.runtime.create(db, obj_in=runtime_in)  # noqa: F841
