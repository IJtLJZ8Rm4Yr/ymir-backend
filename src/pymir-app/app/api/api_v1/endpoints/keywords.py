import json
from typing import Dict, Any, List, Iterator, Optional, Callable
from functools import partial

from fastapi import APIRouter, Depends, Query
from fastapi.logger import logger

from app import models
from app.api import deps
from app.utils.ymir_controller import (
    ControllerClient,
    ControllerRequest,
    ExtraRequestType,
)
from app.utils.cache import CacheClient
from app.utils.class_ids import keywords_to_labels, labels_to_keywords
from app.schemas import (
    KeywordsCreate,
    KeywordsUpdateOut,
    KeywordsPaginationOut,
    KeywordOut,
    KeywordUpdate,
    Keyword,
)

router = APIRouter()


@router.get(
    "/", response_model=KeywordsPaginationOut,
)
def get_keywords(
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    labels: List = Depends(deps.get_personal_labels),
    q: Optional[str] = Query(None, description="query keywords"),
    offset: int = Query(0),
    limit: Optional[int] = Query(None),
) -> Dict:
    """
    Get keywords and aliases
    """
    filter_f = partial(filter_keyword, q) if q else None
    items = list(labels_to_keywords(labels, filter_f))

    res = {"total": len(items), "items": paginate(items, offset, limit)}
    return {"result": res}


@router.post(
    "/", response_model=KeywordsUpdateOut,
)
def create_keywords(
    *,
    keywords_input: KeywordsCreate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
) -> Any:
    """
    Batch create given keywords and aliases to keywords list
    """
    user_id = current_user.id
    labels = list(keywords_to_labels(keywords_input.keywords))
    req = ControllerRequest(
        ExtraRequestType.add_label,
        user_id,
        args={"labels": labels, "dry_run": keywords_input.dry_run},
    )
    resp = controller_client.send(req)
    logger.info("[controller] response for add label: %s", resp)

    # note that for failed keywords, the result looks like: 'dog,puppy'
    # there is not leading index
    failed_keywords = list(labels_to_keywords(list(resp["csv_labels"]), offset=0))

    if not keywords_input.dry_run:
        # clean cached key when changes happen
        cache.delete_personal_keywords()
    return {"result": {"failed": failed_keywords}}


@router.patch(
    "/{keyword}", response_model=KeywordOut,
)
def update_keyword_aliases(
    *,
    keyword: str,
    aliases_in: KeywordUpdate,
    current_user: models.User = Depends(deps.get_current_active_user),
    controller_client: ControllerClient = Depends(deps.get_controller_client),
    cache: CacheClient = Depends(deps.get_cache),
) -> Any:
    user_id = current_user.id
    updated_keyword = Keyword(name=keyword, aliases=aliases_in.aliases)
    labels = list(keywords_to_labels([updated_keyword]))
    req = ControllerRequest(
        ExtraRequestType.add_label, user_id, args={"labels": labels, "dry_run": False}
    )
    resp = controller_client.send(req)

    # clean cached key when changes happen
    cache.delete_personal_keywords()
    return {"result": updated_keyword}


def paginate(
    items: List[Any], offset: int = 0, limit: Optional[int] = None
) -> List[Any]:
    """
    Mimic the behavior of database query's offset-limit pagination
    """
    return items[offset : (limit + offset if limit is not None else None)]


def filter_keyword(query: str, keyword: Dict) -> bool:
    for matching_string in [keyword["name"], *keyword["aliases"]]:
        if query in matching_string:
            return True
    return False
