from fastapi import APIRouter, Depends
from app.api.auth import get_current_user
from app.models import User
from app.utils.history_utils import get_history

router = APIRouter(prefix="/history", tags=["History"])

@router.get("")
def get_analysis_history(current_user: User = Depends(get_current_user)):
    return get_history(user_id=current_user.id)