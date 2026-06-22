"""SDK router for mobile SDK endpoints with authentication."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import and_
from typing import List, Optional
from datetime import datetime
import json

from src.database import get_db
from src import schemas, crud, models
from src.auth import get_api_key

router = APIRouter(prefix="/api/sdk", tags=["SDK"])


@router.get("/config", response_model=List[schemas.RuleSDKResponse])
def get_sdk_config(
    db_api_key: models.ApiKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Get active rules for SDK.

    Returns all enabled rules that the SDK should use for matching
    and intercepting HTTP requests. Only includes fields needed for
    SDK matching logic.

    Requires X-API-KEY header for authentication.
    """
    rules = crud.get_active_rules(db)

    result = []
    for db_rule in rules:
        mock_data = json.loads(db_rule.mock_data) if db_rule.mock_data else {}
        result.append(schemas.RuleSDKResponse(
            id=db_rule.id,
            url_pattern=db_rule.url_pattern,
            method=db_rule.method or "GET",
            status_code=db_rule.status_code,
            delay_ms=db_rule.delay_ms,
            mock_data=mock_data,
            is_enabled=db_rule.is_enabled
        ))

    return result


@router.post("/register", response_model=schemas.DeviceResponse)
def register_device(
    device: schemas.DeviceRegister,
    db_api_key: models.ApiKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Register a device with the backend.

    Called by the SDK when it first initializes or periodically
    to update device information. Returns or creates the device record.

    Requires X-API-KEY header for authentication.
    """
    existing_device = db.query(models.Device).filter(
        and_(
            models.Device.device_id == device.deviceId,
            models.Device.api_key_id == db_api_key.id
        )
    ).first()

    if existing_device:
        existing_device.app_version = device.appVersion
        existing_device.android_version = device.androidVersion
        existing_device.internet_mode = device.internetMode
        existing_device.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(existing_device)
        return existing_device

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
    db_api_key: models.ApiKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Log an interception event.

    Called by the SDK when it successfully intercepts and mocks
    an HTTP request. Stores detailed information about the interception.

    Requires X-API-KEY header for authentication.
    """
    device = crud.get_device_by_device_id(db, log_data.deviceId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found. Please register the device first."
        )

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
    db_api_key: models.ApiKey = Depends(get_api_key),
    db: Session = Depends(get_db)
):
    """
    Log any API call for analytics.

    Called by the SDK for every HTTP request, whether intercepted or not.
    Used for analytics and tracking SDK usage.

    Requires X-API-KEY header for authentication.
    """
    device = crud.get_device_by_device_id(db, log_data.deviceId)
    if not device:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Device not found. Please register the device first."
        )

    crud.log_call(
        db,
        device_id=device.id,
        endpoint=log_data.endpoint,
        method=log_data.method,
        was_intercepted=log_data.wasIntercepted,
        intercepted_by_rule_id=log_data.interceptedByRuleId,
        response_time_ms=log_data.responseTimeMs,
        status_code=log_data.statusCode
    )

    return schemas.SuccessResponse(
        status="success",
        message="Call logged successfully"
    )


@router.get("/devices", response_model=List[schemas.DeviceResponse])
def list_devices(
    db_api_key: models.ApiKey = Depends(get_api_key),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db)
):
    """
    List all devices for the authenticated API key.

    Returns a paginated list of devices registered with this API key.

    Requires X-API-KEY header for authentication.
    """
    devices = db.query(models.Device).filter(
        models.Device.api_key_id == db_api_key.id
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
