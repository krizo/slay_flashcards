"""
Tag management routes for the SlayFlashcards API.
"""

import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status  # pylint: disable=import-error
from sqlalchemy.exc import IntegrityError  # pylint: disable=import-error
from sqlalchemy.orm import Session  # pylint: disable=import-error

from api.api_schemas import Tag, TagCreate, TagResponse, TagsResponse, TagUpdate
from api.dependencies.auth import get_current_user
from core.db.database import get_db
from core.db.models import Tag as TagModel

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/tags", tags=["tags"])


@router.get("/", response_model=TagsResponse)
async def get_tags(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    """
    Get all tags for the current user.
    """
    tags = db.query(TagModel).filter(TagModel.user_id == current_user.id).order_by(TagModel.name).all()

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
    Get a specific tag by ID (only if it belongs to the current user).
    """
    tag = db.query(TagModel).filter(
        TagModel.id == tag_id,
        TagModel.user_id == current_user.id
    ).first()

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
    Create a new tag for the current user.
    """
    logger.info(f"Creating tag '{tag_data.name}' for user {current_user.id}")

    # Check if tag with this name already exists for this user
    existing_tag = db.query(TagModel).filter(
        TagModel.user_id == current_user.id,
        TagModel.name == tag_data.name
    ).first()

    if existing_tag:
        logger.warning(f"Tag '{tag_data.name}' already exists for user {current_user.id} (tag_id: {existing_tag.id})")
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Tag with name '{tag_data.name}' already exists"
        )

    logger.info(f"No existing tag found, creating new tag '{tag_data.name}'")

    new_tag = TagModel(
        user_id=current_user.id,
        name=tag_data.name,
        color=tag_data.color
    )

    try:
        db.add(new_tag)
        db.commit()
        db.refresh(new_tag)

        logger.info(f"Tag '{new_tag.name}' created successfully with ID {new_tag.id} for user {current_user.id}")

        return TagResponse(
            success=True,
            message="Tag created successfully",
            data=Tag.model_validate(new_tag)
        )
    except IntegrityError as e:
        db.rollback()
        logger.error(f"IntegrityError creating tag '{tag_data.name}' for user {current_user.id}: {str(e)}")
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
    Update an existing tag (only if it belongs to the current user).
    """
    tag = db.query(TagModel).filter(
        TagModel.id == tag_id,
        TagModel.user_id == current_user.id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    # Check if new name conflicts with existing tag for this user
    if tag_data.name and tag_data.name != tag.name:
        existing_tag = db.query(TagModel).filter(
            TagModel.user_id == current_user.id,
            TagModel.name == tag_data.name
        ).first()
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
    Delete a tag (only if it belongs to the current user).
    Note: This will remove the tag from all quizzes that use it.
    """
    tag = db.query(TagModel).filter(
        TagModel.id == tag_id,
        TagModel.user_id == current_user.id
    ).first()

    if not tag:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Tag with ID {tag_id} not found"
        )

    db.delete(tag)
    db.commit()

    return None
