# FastAPI
from fastapi import APIRouter, Depends, HTTPException, status

# SQLAlchemy
from sqlalchemy.orm import Session

# UUID
from uuid import UUID

# Application
from dependencies.database import get_db  # Get DB
from dependencies.token import get_current_user  # Get current user
from schemas.widget import WidgetCreate, WidgetRead, WidgetUpdate  # Schemas
from models import Host, Page, User, Widget  # Models

# Router
router = APIRouter(
    prefix="/widgets",
    tags=["Widget"],
)


@router.get("/page/{page_id}", response_model=list[WidgetRead])
async def list_widgets_for_page(
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

    return db_page.widgets


@router.post("", response_model=WidgetRead, status_code=status.HTTP_201_CREATED)
async def create_widget(
    page_id: UUID,
    widget_data: WidgetCreate,
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
            detail="Page not found or access denied",
        )

    db_host = (
        db.query(Host)
        .where(
            Host.id == widget_data.host_id,
            Host.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_host:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Specified host not found",
        )

    db_widget = Widget(
        **widget_data.model_dump(),
        page_id=page_id,
    )

    db.add(db_widget)
    db.commit()
    db.refresh(db_widget)

    return db_widget


@router.get("/{widget_id}", response_model=WidgetRead)
async def get_widget(
    widget_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_widget = (
        db.query(Widget)
        .join(Page)
        .where(
            Widget.id == widget_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
            Widget.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    return db_widget


@router.patch("/{widget_id}", response_model=WidgetRead)
async def update_widget(
    widget_id: UUID,
    widget_data: WidgetUpdate,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_widget = (
        db.query(Widget)
        .join(Page)
        .where(
            Widget.id == widget_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
            Widget.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    update_dict = widget_data.model_dump(exclude_unset=True)
    if "host_id" in update_dict:
        db_host = (
            db.query(Host)
            .where(
                Host.id == update_dict["host_id"],
                Host.deleted_at == None,
            )
            .one_or_none()
        )
        if not db_host:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Target host not found",
            )

    for key, value in update_dict.items():
        setattr(db_widget, key, value)

    db.commit()
    db.refresh(db_widget)

    return db_widget


@router.delete("/{widget_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_widget(
    widget_id: UUID,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    db_widget = (
        db.query(Widget)
        .join(Page)
        .where(
            Widget.id == widget_id,
            Page.user_id == user.id,
            Page.deleted_at == None,
            Widget.deleted_at == None,
        )
        .one_or_none()
    )

    if not db_widget:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Widget not found",
        )

    db.delete(db_widget)
    db.commit()

    return None
