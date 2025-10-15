"""
Tag management routes for the SlayFlashcards API.
"""

from typing import List

from fastapi import APIRouter, Depends, HTTPException, status  # pylint: disable=import-error
from sqlalchemy.exc import IntegrityError  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import Tag, TagCreate, TagResponse, TagsResponse, TagUpdate
from api.dependencies.auth import get_current_user
from core.db.database import get_db
from core.db.models import Tag as TagModel

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsResponse)
async def get_tags(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all available tags.
    """
    tags = db.query(TagModel).order_by(TagModel.name).all()

    return TagsResponse(
        success=True,
        message="Tags retrieved successfully",
        data=[Tag.model_validate(tag) for tag in tags]
    )


@router.get("/{tag_id}", response_model=TagResponse)
async def get_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get a specific tag by ID.
    """
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    return TagResponse(
        success=True,
        message="Tag retrieved successfully",
        data=Tag.model_validate(tag)
    )


@router.post("/", response_model=TagResponse, status_code=status.HTTP_201_CREATED)
async def create_tag(
    tag_data: TagCreate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Create a new tag.
    """
    # Check if tag with this name already exists
    existing_tag = db.query(TagModel).filter(TagModel.name == tag_data.name).first()
    if existing_tag:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag_data.name}' already exists"
        )

    new_tag = TagModel(
        name=tag_data.name,
        color=tag_data.color
    )

    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)

        return TagResponse(
            success=True,
            message="Tag created successfully",
            data=Tag.model_validate(new_tag)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Tag with this name already exists"
        )


@router.put("/{tag_id}", response_model=TagResponse)
async def update_tag(
    tag_id: int,
    tag_data: TagUpdate,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Update an existing tag.
    """
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    # Check if new name conflicts with existing tag
    if tag_data.name and tag_data.name != tag.name:
        existing_tag = db.query(TagModel).filter(TagModel.name == tag_data.name).first()
        if existing_tag:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Tag with name '{tag_data.name}' already exists"
            )

    # Update fields
    if tag_data.name is not None:
        tag.name = tag_data.name
    if tag_data.color is not None:
        tag.color = tag_data.color

    try:
        db.commit()
        db.refresh(tag)

        return TagResponse(
            success=True,
            message="Tag updated successfully",
            data=Tag.model_validate(tag)
        )
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Error updating tag"
        )


@router.delete("/{tag_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(
    tag_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Delete a tag.
    Note: This will remove the tag from all quizzes that use it.
    """
    tag = db.query(TagModel).filter(TagModel.id == tag_id).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    db.delete(tag)
    db.commit()

    return None
