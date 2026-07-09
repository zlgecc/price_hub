from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.price_sync import ensure_price_data
from app.schemas.price import CategoryOut, DashboardOut, ItemDetailOut, ItemOut
from app.services.price_service import get_dashboard, get_item_detail, list_categories, list_items

router = APIRouter(prefix="/api", tags=["prices"])


@router.get("/categories", response_model=list[CategoryOut])
async def get_categories(db: Session = Depends(get_db)):
    await ensure_price_data()
    return list_categories(db)


@router.get("/items", response_model=list[ItemOut])
async def get_items(
    category: str | None = Query(None),
    region: str | None = Query(None),
    search: str | None = Query(None),
    db: Session = Depends(get_db),
):
    await ensure_price_data()
    return list_items(db, category=category, region=region, search=search)


@router.get("/items/{code}/history", response_model=ItemDetailOut)
def get_item_history(
    code: str,
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    detail = get_item_detail(db, code, days=days)
    if not detail:
        raise HTTPException(status_code=404, detail="Item not found")
    return detail


@router.get("/dashboard", response_model=DashboardOut)
async def dashboard(db: Session = Depends(get_db)):
    await ensure_price_data()
    return get_dashboard(db)
