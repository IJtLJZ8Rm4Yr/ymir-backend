from typing import Any

from fastapi import APIRouter, Body, Depends, Security
from fastapi.logger import logger
from pydantic.networks import EmailStr
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.api import deps
from app.api.errors.errors import (
    DuplicateUserNameError,
    FailedtoCreateWorkspace,
    UserNotFound,
)
from app.constants.role import Roles
from app.utils.ymir_controller import (
    ControllerClient,
    ControllerRequest,
    ExtraRequestType,
)

router = APIRouter()


@router.post(
    "/",
    response_model=schemas.UserOut,
    responses={400: {"description": "Username Already Exists"}},
)
def create_user(
    *,
    db: Session = Depends(deps.get_db),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    password: str = Body(...),
    email: EmailStr = Body(...),
    phone: str = Body(None),
    username: str = Body(None),
) -> Any:
    """
    Register user
    """
    user = crud.user.get_by_email(db, email=email)
    if user:
        raise DuplicateUserNameError()

    user_in = schemas.UserCreate(
        password=password, email=email, phone=phone, username=username
    )
    user = crud.user.create(db, obj_in=user_in)

    workspace_id = f"{user.id:0>6}"
    crud.workspace.create(
        db,
        obj_in=schemas.WorkspaceCreate(
            hash=workspace_id, name=workspace_id, user_id=user.id
        ),
    )
    req = ControllerRequest(ExtraRequestType.create_workspace, user.id, workspace_id)
    try:
        resp = controller_client.send(req)
        logger.info("controller response: %s", resp)
    except ValueError:
        # todo parse error message
        raise FailedtoCreateWorkspace()

    return {"result": user}


@router.get("/me", response_model=schemas.UserOut)
def get_current_user(
    current_user: models.User = Depends(deps.get_current_active_user),
) -> Any:
    """
    Get verbose information about current user
    """
    return {"result": current_user}


@router.get(
    "/{user_id}",
    response_model=schemas.UserOut,
    responses={404: {"description": "User Not Found"}},
)
def get_user(
    user_id: int,
    db: Session = Depends(deps.get_db),
    current_user: models.User = Security(
        deps.get_current_active_user,
        scopes=[Roles.ADMIN.name, Roles.SUPER_ADMIN.name],
    ),
) -> Any:
    """
    Query user information,
    Admin permission is required
    """
    user = crud.user.get(db, id=user_id)
    if not user:
        raise UserNotFound()

    return {"result": user}
