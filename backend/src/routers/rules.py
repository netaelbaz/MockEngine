"""Rules management router for interception rules."""

from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from src.database import get_db
from src import schemas, crud
from src.utils.validators import validate_url_pattern

router = APIRouter(prefix="/api/v1/rules", tags=["Rules"])


@router.post("", response_model=schemas.RuleResponse, status_code=status.HTTP_201_CREATED)
def create_rule(
    rule: schemas.RuleCreate,
    db: Session = Depends(get_db)
):
    """
    Create a new interception rule.

    Creates a rule that defines how to mock HTTP responses.
    The URL pattern will be matched against incoming requests.
    """
    # Validate URL pattern
    if not validate_url_pattern(rule.url_pattern):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL pattern. Must start with / and contain valid characters."
        )

    # Create rule in database
    db_rule = crud.create_rule(db, rule)

    # Parse mock_data from JSON string for response
    import json
    mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}

    return schemas.RuleResponse(
        id=db_rule.id,
        name=db_rule.name,
        url_pattern=db_rule.url_pattern,
        method=db_rule.method or "GET",
        status_code=db_rule.status_code,
        delay_ms=db_rule.delay_ms,
        mock_data=mock_data,
        is_enabled=db_rule.is_enabled,
        created_at=db_rule.created_at,
        updated_at=db_rule.updated_at,
        created_by_key_id=db_rule.created_by_key_id
    )


@router.get("", response_model=List[schemas.RuleResponse])
def list_rules(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    enabled_only: bool = Query(False, description="Only return enabled rules"),
    db: Session = Depends(get_db)
):
    """
    List all interception rules.

    Returns a paginated list of all rules in the system.
    Use enabled_only=true to get only active rules.
    """
    if enabled_only:
        rules = crud.get_active_rules(db)
    else:
        rules = crud.get_all_rules(db, skip=skip, limit=limit)

    # Parse mock_data from JSON string for each rule
    import json
    result = []
    for db_rule in rules:
        mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}
        result.append(schemas.RuleResponse(
            id=db_rule.id,
            name=db_rule.name,
            url_pattern=db_rule.url_pattern,
            method=db_rule.method or "GET",
            status_code=db_rule.status_code,
            delay_ms=db_rule.delay_ms,
            mock_data=mock_data,
            is_enabled=db_rule.is_enabled,
            created_at=db_rule.created_at,
            updated_at=db_rule.updated_at,
            created_by_key_id=db_rule.created_by_key_id
        ))

    return result


@router.get("/{rule_id}", response_model=schemas.RuleResponse)
def get_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """
    Get a specific rule by ID.

    Returns detailed information about a single rule.
    """
    db_rule = crud.get_rule(db, rule_id)

    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id {rule_id} not found"
        )

    # Parse mock_data from JSON string
    import json
    mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}

    return schemas.RuleResponse(
        id=db_rule.id,
        name=db_rule.name,
        url_pattern=db_rule.url_pattern,
        method=db_rule.method or "GET",
        status_code=db_rule.status_code,
        delay_ms=db_rule.delay_ms,
        mock_data=mock_data,
        is_enabled=db_rule.is_enabled,
        created_at=db_rule.created_at,
        updated_at=db_rule.updated_at,
        created_by_key_id=db_rule.created_by_key_id
    )


@router.put("/{rule_id}", response_model=schemas.RuleResponse)
def update_rule(
    rule_id: str,
    rule_update: schemas.RuleUpdate,
    db: Session = Depends(get_db)
):
    """
    Update an existing rule.

    Updates any field of an existing rule.
    Partial updates are supported - only provide fields you want to change.
    """
    # Validate URL pattern if provided
    if rule_update.url_pattern and not validate_url_pattern(rule_update.url_pattern):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid URL pattern. Must start with / and contain valid characters."
        )

    # Update rule in database
    db_rule = crud.update_rule(db, rule_id, rule_update)

    if not db_rule:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id {rule_id} not found"
        )

    # Parse mock_data from JSON string
    import json
    mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}

    return schemas.RuleResponse(
        id=db_rule.id,
        name=db_rule.name,
        url_pattern=db_rule.url_pattern,
        method=db_rule.method or "GET",
        status_code=db_rule.status_code,
        delay_ms=db_rule.delay_ms,
        mock_data=mock_data,
        is_enabled=db_rule.is_enabled,
        created_at=db_rule.created_at,
        updated_at=db_rule.updated_at,
        created_by_key_id=db_rule.created_by_key_id
    )


@router.delete("/{rule_id}", response_model=schemas.SuccessResponse)
def delete_rule(
    rule_id: str,
    db: Session = Depends(get_db)
):
    """
    Delete a rule.

    Permanently deletes a rule from the system.
    This action cannot be undone.
    """
    success = crud.delete_rule(db, rule_id)

    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Rule with id {rule_id} not found"
        )

    return schemas.SuccessResponse(status="success", message="Rule deleted successfully")
