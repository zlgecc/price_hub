from fastapi import APIRouter, Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.schemas.price import FetchResult
from app.services.fetcher_manager import FetcherManager

router = APIRouter(prefix="/internal", tags=["internal"])


@router.post("/fetch", response_model=list[FetchResult])
async def trigger_fetch(
    authorization: str | None = Header(None),
    db: Session = Depends(get_db),
):
    expected = f"Bearer {settings.cron_secret}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")
    manager = FetcherManager()
    return await manager.run_all(db)
