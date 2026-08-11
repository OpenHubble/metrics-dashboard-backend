# FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy
from sqlalchemy.orm import Session, joinedload

# Datetime
from datetime import datetime, timezone

# UUID
from uuid import UUID

# Application
from dependencies.database import get_db  # Get DB
from dependencies.token import get_current_user  # Get current user
from schemas.page import PageCreate, PageUpdate, PageRead  # Schemas
from models import User, Page  # Models

# Router
router = APIRouter(
    prefix="/pages",
    tags=["Page"],
)


@router.get("", response_model=list[PageRead])
async def list_pages(
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_pages = (
        db.query(Page)
        .options(joinedload(Page.widgets))
        .where(
            Page.user_id == user.id,
            Page.deleted_at == None,
        )
        .all()
    )

    return db_pages


@router.get("/{page_id}", response_model=PageRead)
async def get_page(
    page_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_page = (
        db.query(Page)
        .options(joinedload(Page.widgets))
        .where(
            Page.id == page_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    return db_page


@router.post("", response_model=PageRead, status_code=status.HTTP_201_CREATED)
async def create_page(
    page_data: PageCreate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_page = Page(**page_data.model_dump(), user_id=user.id)

    db.add(db_page)
    db.commit()
    db.refresh(db_page)

    return db_page


@router.patch("/{page_id}", response_model=PageRead)
async def update_page(
    page_id: UUID,
    page_data: PageUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_page = (
        db.query(Page)
        .options(joinedload(Page.widgets))
        .where(
            Page.id == page_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    for key, value in page_data.model_dump(exclude_unset=True).items():
        setattr(db_page, key, value)

    db.commit()
    db.refresh(db_page)

    return db_page


@router.delete("/{page_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_page(
    page_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_page = (
        db.query(Page)
        .where(
            Page.id == page_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_page:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Page not found",
        )

    db_page.deleted_at = datetime.now(timezone.utc)

    db.commit()
    db.refresh(db_page)

    return None
