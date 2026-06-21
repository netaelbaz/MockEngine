"""CRUD operations for MockEngine database models."""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta

from src import models, schemas
# Import both encryption utilities
from src.utils.encryption import encrypt, decrypt


# ==================== API Key Operations ====================

def create_api_key(db: Session, key_name: str, api_key: str) -> schemas.ApiKeyResponse:
    """Create a new API key and return a decoupled schema with plaintext key."""
    encrypted_key = encrypt(api_key)
    db_key = models.ApiKey(
        name=key_name,
        api_key=encrypted_key,
        is_active=True
    )
    db.add(db_key)
    db.commit()
    db.refresh(db_key)

    # Map to schema and explicitly pass the original plaintext key
    response_data = schemas.ApiKeyResponse.from_orm(db_key)
    response_data.api_key = api_key
    return response_data


def get_api_key_by_id(db: Session, key_id: str) -> Optional[schemas.ApiKeyResponse]:
    """Get an API key by ID and return it as a decrypted schema."""
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if not db_key:
        return None

    response_data = schemas.ApiKeyResponse.from_orm(db_key)
    if response_data.api_key:
        try:
            response_data.api_key = decrypt(response_data.api_key)
        except Exception:
            pass
    return response_data


def get_all_api_keys(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.ApiKeyResponse]:
    """Get all API keys with pagination, safely converting them to decrypted schemas."""
    db_keys = db.query(models.ApiKey).offset(skip).limit(limit).all()
    decrypted_keys = []

    for db_key in db_keys:
        # Convert to Pydantic schema first (disconnects from SQLAlchemy track-changes)
        key_schema = schemas.ApiKeyResponse.from_orm(db_key)

        if key_schema.api_key:
            try:
                key_schema.api_key = decrypt(key_schema.api_key)
            except Exception:
                pass  # Leaves it as-is if decryption fails

        decrypted_keys.append(key_schema)

    return decrypted_keys


def get_api_key_by_key(db: Session, api_key: str) -> Optional[models.ApiKey]:
    """
    Get an API key by the plaintext key string.

    Since Fernet uses non-deterministic encryption, we fetch active keys
    and decrypt them to find a match.
    """
    active_keys = db.query(models.ApiKey).filter(models.ApiKey.is_active == True).all()
    for db_key in active_keys:
        try:
            decrypted_val = decrypt(db_key.api_key)
            if decrypted_val == api_key:
                db_key.api_key = decrypted_val  # Set to plaintext for user response
                return db_key
        except Exception:
            continue  # Skip keys that fail decryption or don't match
    return None


def validate_api_key(db: Session, api_key: str) -> Optional[models.ApiKey]:
    """
    Validate an incoming plaintext API key and return the key object if valid.
    """
    return get_api_key_by_key(db, api_key)


def update_api_key_active(db: Session, key_id: str, is_active: bool) -> Optional[models.ApiKey]:
    """Update the active status of an API key."""
    db_key = get_api_key_by_id(db, key_id)  # Already handles decryption internally
    if db_key:
        db_key.is_active = is_active
        db.commit()
        db.refresh(db_key)
        # Re-decrypt after refreshing from the database
        try:
            db_key.api_key = decrypt(db_key.api_key)
        except Exception:
            pass
    return db_key


def delete_api_key(db: Session, key_id: str) -> bool:
    """Delete an API key."""
    db_key = db.query(models.ApiKey).filter(models.ApiKey.id == key_id).first()
    if db_key:
        db.delete(db_key)
        db.commit()
        return True
    return False

# ==================== Rule Operations ====================

def create_rule(db: Session, rule: schemas.RuleCreate, created_by_key_id: Optional[str] = None) -> models.Rule:
    """Create a new rule."""
    db_rule = models.Rule(
        name=rule.name,
        url_pattern=rule.url_pattern,
        status_code=rule.status_code,
        delay_ms=rule.delay_ms,
        mock_data=json.dumps(rule.mock_data),
        is_enabled=True,
        created_by_key_id=created_by_key_id
    )
    db.add(db_rule)
    db.commit()
    db.refresh(db_rule)
    return db_rule


def get_rule(db: Session, rule_id: str) -> Optional[models.Rule]:
    """Get a rule by ID."""
    return db.query(models.Rule).filter(models.Rule.id == rule_id).first()


def get_all_rules(db: Session, skip: int = 0, limit: int = 100) -> List[models.Rule]:
    """Get all rules with pagination."""
    return db.query(models.Rule).offset(skip).limit(limit).all()


def get_active_rules(db: Session) -> List[models.Rule]:
    """Get all enabled rules for SDK."""
    return db.query(models.Rule).filter(models.Rule.is_enabled == True).all()


def update_rule(db: Session, rule_id: str, rule_update: schemas.RuleUpdate) -> Optional[models.Rule]:
    """Update a rule."""
    db_rule = get_rule(db, rule_id)
    if not db_rule:
        return None

    # Update fields if provided
    update_data = rule_update.dict(exclude_unset=True)
    if "mock_data" in update_data and update_data["mock_data"] is not None:
        update_data["mock_data"] = json.dumps(update_data["mock_data"])

    for field, value in update_data.items():
        setattr(db_rule, field, value)

    db.commit()
    db.refresh(db_rule)
    return db_rule


def delete_rule(db: Session, rule_id: str) -> bool:
    """Delete a rule."""
    db_rule = get_rule(db, rule_id)
    if db_rule:
        db.delete(db_rule)
        db.commit()
        return True
    return False


# ==================== Device Operations ====================

def get_or_create_device(db: Session, device_id: str, api_key_id: str) -> models.Device:
    """Get existing device or create a new one."""
    # Try to find existing device
    device = db.query(models.Device).filter(
        and_(
            models.Device.device_id == device_id,
            models.Device.api_key_id == api_key_id
        )
    ).first()

    if device:
        # Update last_seen
        device.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(device)
        return device

    # Create new device
    return device


def register_device(
    db: Session,
    device_id: str,
    api_key_id: str,
    app_version: str,
    android_version: Optional[str],
    internet_mode: str
) -> models.Device:
    """Register a new device."""
    db_device = models.Device(
        device_id=device_id,
        api_key_id=api_key_id,
        app_version=app_version,
        android_version=android_version,
        internet_mode=internet_mode
    )
    db.add(db_device)
    db.commit()
    db.refresh(db_device)
    return db_device


def update_device_last_seen(db: Session, device_id: str) -> Optional[models.Device]:
    """Update the last_seen timestamp for a device."""
    device = db.query(models.Device).filter(models.Device.device_id == device_id).first()
    if device:
        device.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(device)
    return device


def get_device_by_id(db: Session, device_internal_id: str) -> Optional[models.Device]:
    """Get device by internal ID."""
    return db.query(models.Device).filter(models.Device.id == device_internal_id).first()


def get_device_by_device_id(db: Session, device_id: str) -> Optional[models.Device]:
    """Get device by external device ID."""
    return db.query(models.Device).filter(models.Device.device_id == device_id).first()


def get_all_devices(db: Session, skip: int = 0, limit: int = 100) -> List[models.Device]:
    """Get all devices with pagination."""
    return db.query(models.Device).offset(skip).limit(limit).all()


# ==================== Call Log Operations ====================

def log_call(
    db: Session,
    device_id: str,
    endpoint: str,
    method: str,
    was_intercepted: bool = False,
    intercepted_by_rule_id: Optional[str] = None,
    response_time_ms: Optional[int] = None
) -> models.CallLog:
    """Log an API call for analytics."""
    db_log = models.CallLog(
        device_id=device_id,
        endpoint=endpoint,
        method=method,
        was_intercepted=was_intercepted,
        intercepted_by_rule_id=intercepted_by_rule_id,
        response_time_ms=response_time_ms
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_call_logs(db: Session, device_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.CallLog]:
    """Get call logs with optional device filter and pagination."""
    query = db.query(models.CallLog)
    if device_id:
        query = query.filter(models.CallLog.device_id == device_id)
    return query.offset(skip).limit(limit).all()


# ==================== Interception Log Operations ====================

def log_interception(
    db: Session,
    device_id: str,
    rule_id: str,
    endpoint: str,
    request_data: Optional[Dict[str, Any]],
    response_mock_data: Dict[str, Any]
) -> models.InterceptionLog:
    """Log an interception event."""
    db_log = models.InterceptionLog(
        device_id=device_id,
        rule_id=rule_id,
        endpoint=endpoint,
        request_data=json.dumps(request_data) if request_data else None,
        response_mock_data=json.dumps(response_mock_data)
    )
    db.add(db_log)
    db.commit()
    db.refresh(db_log)
    return db_log


def get_interception_logs(db: Session, device_id: Optional[str] = None, skip: int = 0, limit: int = 100) -> List[models.InterceptionLog]:
    """Get interception logs with optional device filter and pagination."""
    query = db.query(models.InterceptionLog)
    if device_id:
        query = query.filter(models.InterceptionLog.device_id == device_id)
    return query.offset(skip).limit(limit).all()


# ==================== Analytics Operations ====================

from datetime import datetime, timedelta
from sqlalchemy import func, desc, case


def _get_time_range_filter(time_range: str) -> datetime:
    """Get the cutoff datetime for a given time range."""
    now = datetime.utcnow()
    if time_range == "today":
        return now - timedelta(hours=24)
    elif time_range == "week":
        return now - timedelta(days=7)
    elif time_range == "month":
        return now - timedelta(days=30)
    else:
        return now - timedelta(hours=24)  # Default to today


def get_analytics_overview(db: Session, time_range: str = "today") -> Dict[str, Any]:
    """Get aggregated overview statistics for analytics."""
    cutoff_time = _get_time_range_filter(time_range)

    # Device stats
    total_devices = db.query(func.count(models.Device.id)).scalar()

    active_devices_query = db.query(func.count(models.Device.id)).filter(
        models.Device.last_seen >= cutoff_time
    )
    active_today = active_devices_query.scalar()

    # Android versions
    android_versions_query = db.query(
        models.Device.android_version,
        func.count(models.Device.id).label('count')
    ).filter(
        models.Device.last_seen >= cutoff_time,
        models.Device.android_version.isnot(None)
    ).group_by(models.Device.android_version).all()

    android_versions = [
        {"version": av[0] if av[0] else "Unknown", "count": av[1]}
        for av in android_versions_query
    ]

    # Internet modes
    internet_modes_query = db.query(
        models.Device.internet_mode,
        func.count(models.Device.id).label('count')
    ).filter(
        models.Device.last_seen >= cutoff_time
    ).group_by(models.Device.internet_mode).all()

    internet_modes = {im[0]: im[1] for im in internet_modes_query}

    # Call stats
    total_calls = db.query(func.count(models.CallLog.id)).filter(
        models.CallLog.timestamp >= cutoff_time
    ).scalar()

    unique_endpoints = db.query(
        models.CallLog.endpoint
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).distinct().count()

    intercepted_count = db.query(func.count(models.CallLog.id)).filter(
        models.CallLog.timestamp >= cutoff_time,
        models.CallLog.was_intercepted == True
    ).scalar()

    interception_rate = intercepted_count / total_calls if total_calls > 0 else 0.0

    # Endpoint analytics
    endpoint_stats = db.query(
        models.CallLog.endpoint,
        models.CallLog.method,
        func.count(models.CallLog.id).label('call_count'),
        func.avg(models.CallLog.response_time_ms).label('avg_response_time'),
        func.sum(case((models.CallLog.was_intercepted == True, 1), else_=0)).label('intercepted_count')
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).group_by(
        models.CallLog.endpoint,
        models.CallLog.method
    ).all()

    # Get wifi/cellular breakdown per endpoint
    endpoints = []
    for ep in endpoint_stats:
        endpoint, method, call_count, avg_response, intercepted_count = ep

        # Query wifi/cellular for this endpoint
        wifi_query = db.query(func.count(models.CallLog.id)).join(
            models.Device, models.Device.id == models.CallLog.device_id
        ).filter(
            models.CallLog.endpoint == endpoint,
            models.CallLog.method == method,
            models.CallLog.timestamp >= cutoff_time,
            models.Device.internet_mode == "wifi"
        ).scalar() or 0

        cellular_query = db.query(func.count(models.CallLog.id)).join(
            models.Device, models.Device.id == models.CallLog.device_id
        ).filter(
            models.CallLog.endpoint == endpoint,
            models.CallLog.method == method,
            models.CallLog.timestamp >= cutoff_time,
            models.Device.internet_mode == "cellular"
        ).scalar() or 0

        endpoints.append({
            "endpoint": endpoint,
            "method": method,
            "call_count": call_count,
            "avg_response_time_ms": int(avg_response) if avg_response else None,
            "was_intercepted_count": intercepted_count or 0,
            "wifi_calls": wifi_query,
            "cellular_calls": cellular_query
        })

    # Recent interceptions (join with rules to get rule name)
    recent_interceptions_query = db.query(
        models.InterceptionLog.id,
        models.InterceptionLog.endpoint,
        models.Rule.name.label('rule_name'),
        models.InterceptionLog.timestamp,
        models.Device.device_id
    ).join(
        models.Rule, models.Rule.id == models.InterceptionLog.rule_id
    ).join(
        models.Device, models.Device.id == models.InterceptionLog.device_id
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).order_by(desc(models.InterceptionLog.timestamp)).limit(10).all()

    recent_interceptions = [
        {
            "id": ri[0],
            "endpoint": ri[1],
            "rule_name": ri[2],
            "timestamp": ri[3],
            "device_id": ri[4]
        }
        for ri in recent_interceptions_query
    ]

    # App versions
    app_versions_query = db.query(
        models.Device.app_version,
        func.count(models.Device.id).label('count')
    ).filter(
        models.Device.last_seen >= cutoff_time
    ).group_by(models.Device.app_version).order_by(desc('count')).all()

    # Get latest version
    latest_version = app_versions_query[0][0] if app_versions_query else None
    total_active = sum(av[1] for av in app_versions_query)

    app_versions = []
    for av in app_versions_query:
        version, count = av
        app_versions.append({
            "version": version,
            "count": count,
            "percentage": round(count / total_active * 100, 1) if total_active > 0 else 0,
            "is_latest": version == latest_version
        })

    return {
        "time_range": time_range,
        "devices": {
            "total_connected": total_devices,
            "active_today": active_today,
            "android_versions": android_versions,
            "internet_modes": internet_modes
        },
        "calls": {
            "total_calls": total_calls,
            "unique_endpoints": unique_endpoints,
            "intercepted_count": intercepted_count,
            "interception_rate": round(interception_rate, 3)
        },
        "endpoints": endpoints,
        "recent_interceptions": recent_interceptions,
        "app_versions": app_versions
    }


def get_interception_analytics(db: Session, time_range: str = "today") -> Dict[str, Any]:
    """Get interception-specific analytics."""
    cutoff_time = _get_time_range_filter(time_range)

    # Total interceptions
    total_interceptions = db.query(func.count(models.InterceptionLog.id)).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).scalar()

    # Most intercepted endpoints
    most_intercepted_query = db.query(
        models.InterceptionLog.endpoint,
        func.count(models.InterceptionLog.id).label('count'),
        models.Rule.name.label('rule_name')
    ).join(
        models.Rule, models.Rule.id == models.InterceptionLog.rule_id
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).group_by(
        models.InterceptionLog.endpoint,
        models.Rule.name
    ).order_by(desc('count')).limit(10).all()

    most_intercepted_endpoints = [
        {
            "endpoint": mie[0],
            "count": mie[1],
            "rule_name": mie[2]
        }
        for mie in most_intercepted_query
    ]

    # Recent interceptions with details
    recent_interceptions_query = db.query(
        models.InterceptionLog
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).order_by(desc(models.InterceptionLog.timestamp)).limit(20).all()

    recent_interceptions = []
    for il in recent_interceptions_query:
        # Get rule name
        rule = db.query(models.Rule).filter(models.Rule.id == il.rule_id).first()
        rule_name = rule.name if rule else "Unknown"

        # Get device_id
        device = db.query(models.Device).filter(models.Device.id == il.device_id).first()
        device_id = device.device_id if device else "Unknown"

        recent_interceptions.append({
            "id": il.id,
            "endpoint": il.endpoint,
            "rule_name": rule_name,
            "timestamp": il.timestamp,
            "device_id": device_id,
            "response_mock_data": json.loads(il.response_mock_data) if il.response_mock_data else {}
        })

    # Rule usage
    rule_usage_query = db.query(
        models.InterceptionLog.rule_id,
        func.count(models.InterceptionLog.id).label('usage_count')
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).group_by(
        models.InterceptionLog.rule_id
    ).order_by(desc('usage_count')).all()

    rule_usage = []
    for ru in rule_usage_query:
        rule_id, usage_count = ru
        rule = db.query(models.Rule).filter(models.Rule.id == rule_id).first()
        if rule:
            rule_usage.append({
                "rule_id": rule_id,
                "rule_name": rule.name,
                "usage_count": usage_count
            })

    return {
        "time_range": time_range,
        "total_interceptions": total_interceptions,
        "most_intercepted_endpoints": most_intercepted_endpoints,
        "recent_interceptions": recent_interceptions,
        "rule_usage": rule_usage
    }


def get_device_analytics(db: Session, time_range: str = "today") -> Dict[str, Any]:
    """Get device analytics."""
    cutoff_time = _get_time_range_filter(time_range)

    # Total devices
    total_devices = db.query(func.count(models.Device.id)).scalar()

    # Active today
    active_today = db.query(func.count(models.Device.id)).filter(
        models.Device.last_seen >= cutoff_time
    ).scalar()

    # Devices by version
    devices_by_version_query = db.query(
        models.Device.app_version,
        func.count(models.Device.id).label('count')
    ).filter(
        models.Device.last_seen >= cutoff_time
    ).group_by(models.Device.app_version).order_by(desc('count')).all()

    # Get latest version
    latest_version = devices_by_version_query[0][0] if devices_by_version_query else None
    total_active = sum(dv[1] for dv in devices_by_version_query)

    devices_by_version = []
    for dv in devices_by_version_query:
        version, count = dv
        devices_by_version.append({
            "version": version,
            "count": count,
            "percentage": round(count / total_active * 100, 1) if total_active > 0 else 0,
            "is_latest": version == latest_version
        })

    # Devices by Android version
    devices_by_android_query = db.query(
        models.Device.android_version,
        func.count(models.Device.id).label('count')
    ).filter(
        models.Device.last_seen >= cutoff_time,
        models.Device.android_version.isnot(None)
    ).group_by(models.Device.android_version).order_by(desc('count')).all()

    devices_by_android_version = [
        {"version": dav[0] if dav[0] else "Unknown", "count": dav[1]}
        for dav in devices_by_android_query
    ]

    # Recent devices
    recent_devices_query = db.query(models.Device).filter(
        models.Device.last_seen >= cutoff_time
    ).order_by(desc(models.Device.last_seen)).limit(10).all()

    recent_devices = [
        schemas.DeviceResponse(
            id=d.id,
            device_id=d.device_id,
            api_key_id=d.api_key_id,
            app_version=d.app_version,
            android_version=d.android_version,
            internet_mode=d.internet_mode,
            first_seen=d.first_seen,
            last_seen=d.last_seen
        )
        for d in recent_devices_query
    ]

    return {
        "total_devices": total_devices,
        "active_today": active_today,
        "devices_by_version": devices_by_version,
        "devices_by_android_version": devices_by_android_version,
        "recent_devices": recent_devices
    }
