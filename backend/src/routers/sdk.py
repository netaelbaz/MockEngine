"""SDK router for mobile SDK endpoints with authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json

from src.database import get_db
from src import schemas, crud
from src.auth import get_api_key

router = APIRouter(prefix="/api/sdk", tags=["SDK"])


@router.get("/config", response_model=List[schemas.RuleSDKResponse])
def get_sdk_config(
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get active rules for SDK.

    Returns all enabled rules that the SDK should use for matching
    and intercepting HTTP requests. Only includes fields needed for
    SDK matching logic.

    Requires X-API-KEY header for authentication.
    """
    # Get all active rules
    rules = crud.get_active_rules(db)

    # Convert to SDK response format (minimal fields)
    result = []
    for db_rule in rules:
        mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}
        result.append(schemas.RuleSDKResponse(
            id=db_rule.id,
            url_pattern=db_rule.url_pattern,
            status_code=db_rule.status_code,
            delay_ms=db_rule.delay_ms,
            mock_data=mock_data,
            is_enabled=db_rule.is_enabled
        ))

    return result


@router.post("/register", response_model=schemas.DeviceResponse)
def register_device(
    device: schemas.DeviceRegister,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Register a device with the backend.

    Called by the SDK when it first initializes or periodically
    to update device information. Returns or creates the device record.

    Requires X-API-KEY header for authentication.
    """
    # Get API key to retrieve its ID
    db_api_key = crud.get_api_key_by_key(db, api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    # Check if device already exists
    existing_device = crud.get_or_create_device(
        db,
        device_id=device.deviceId,
        api_key_id=db_api_key.id
    )

    if existing_device:
        # Update existing device info
        existing_device.app_version = device.appVersion
        existing_device.android_version = device.androidVersion
        existing_device.internet_mode = device.internetMode
        db.commit()
        db.refresh(existing_device)
        return existing_device

    # Create new device
    db_device = crud.register_device(
        db,
        device_id=device.deviceId,
        api_key_id=db_api_key.id,
        app_version=device.appVersion,
        android_version=device.androidVersion,
        internet_mode=device.internetMode
    )

    return schemas.DeviceResponse(
        id=db_device.id,
        device_id=db_device.device_id,
        api_key_id=db_device.api_key_id,
        app_version=db_device.app_version,
        android_version=db_device.android_version,
        internet_mode=db_device.internet_mode,
        first_seen=db_device.first_seen,
        last_seen=db_device.last_seen
    )


@router.post("/log-intercept", response_model=schemas.SuccessResponse)
def log_intercept(
    log_data: schemas.InterceptionLogCreate,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Log an interception event.

    Called by the SDK when it successfully intercepts and mocks
    an HTTP request. Stores detailed information about the interception.

    Requires X-API-KEY header for authentication.
    """
    # Get API key to find the device
    db_api_key = crud.get_api_key_by_key(db, api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    # Find the device by device_id
    device = crud.get_device_by_device_id(db, log_data.deviceId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found. Please register the device first."
        )

    # Create interception log
    crud.log_interception(
        db,
        device_id=device.id,
        rule_id=log_data.ruleId,
        endpoint=log_data.endpoint,
        request_data=log_data.requestData,
        response_mock_data=log_data.responseMockData
    )

    return schemas.SuccessResponse(
        status="success",
        message="Interception logged successfully"
    )


@router.post("/log-call", response_model=schemas.SuccessResponse)
def log_call(
    log_data: schemas.CallLogCreate,
    api_key: str = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Log any API call for analytics.

    Called by the SDK for every HTTP request, whether intercepted or not.
    Used for analytics and tracking SDK usage.

    Requires X-API-KEY header for authentication.
    """
    # Get API key to find the device
    db_api_key = crud.get_api_key_by_key(db, api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    # Find the device by device_id
    device = crud.get_device_by_device_id(db, log_data.deviceId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found. Please register the device first."
        )

    # Create call log
    crud.log_call(
        db,
        device_id=device.id,
        endpoint=log_data.endpoint,
        method=log_data.method,
        was_intercepted=log_data.wasIntercepted,
        intercepted_by_rule_id=log_data.interceptedByRuleId,
        response_time_ms=log_data.responseTimeMs
    )

    return schemas.SuccessResponse(
        status="success",
        message="Call logged successfully"
    )


@router.get("/devices", response_model=List[schemas.DeviceResponse])
def list_devices(
    api_key: str = Depends(get_api_key),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all devices for the authenticated API key.

    Returns a paginated list of devices registered with this API key.

    Requires X-API-KEY header for authentication.
    """
    # Get API key
    db_api_key = crud.get_api_key_by_key(db, api_key)
    if not db_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid API key"
        )

    # Get devices for this API key
    from sqlalchemy import and_
    devices = db.query(crud.models.Device).filter(
        and_(
            crud.models.Device.api_key_id == db_api_key.id
        )
    ).offset(skip).limit(limit).all()

    return [
        schemas.DeviceResponse(
            id=device.id,
            device_id=device.device_id,
            api_key_id=device.api_key_id,
            app_version=device.app_version,
            android_version=device.android_version,
            internet_mode=device.internet_mode,
            first_seen=device.first_seen,
            last_seen=device.last_seen
        )
        for device in devices
    ]
