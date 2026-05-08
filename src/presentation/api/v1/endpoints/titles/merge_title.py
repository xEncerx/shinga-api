from fastapi import APIRouter, Depends
from typing import Annotated

from src.presentation.api.dependencies.use_cases import MergeTitlesUseCaseDep
from src.presentation.api.schemas.requests import MergeTitlesRequest
from src.presentation.api.dependencies.security import require_roles
from src.presentation.api.decorators import map_domain_errors
from src.presentation.api.schemas import errors as api_errors
from src.domain import errors as domain_errors
from src.domain.models import UserRole, UserData

router = APIRouter(tags=["Merge Titles"])


@router.post("/merge", status_code=204)
@map_domain_errors(
    {
        domain_errors.RecordNotFoundError: api_errors.TitleNotFound,
        domain_errors.ValidationError: api_errors.ValidationError,
    }
)
async def merge_titles_endpoint(
    input: MergeTitlesRequest,
    _: Annotated[
        UserData, Depends(require_roles([UserRole.ADMIN, UserRole.MODERATOR]))
    ],
    use_case: MergeTitlesUseCaseDep,
):
    await use_case.execute(
        target_id=input.major_id,
        source_id=input.minor_id,
    )
