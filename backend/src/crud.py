"""CRUD operations for MockEngine database models."""

from sqlalchemy.orm import Session
from sqlalchemy import and_, func, desc, case
from typing import Optional, List, Dict, Any
import json
from datetime import datetime, timedelta

from passlib.context import CryptContext

from src import models, schemas
from src.utils.encryption import encrypt, decrypt

_pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ==================== User Operations ====================

def create_user(db: Session, email: str, password: str, first_name: str = "", last_name: str = "") -> models.User:
    hashed = _pwd_context.hash(password)
    user = models.User(email=email.lower().strip(), hashed_password=hashed, first_name=first_name.strip(), last_name=last_name.strip())
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


def get_user_by_email(db: Session, email: str) -> Optional[models.User]:
    return db.query(models.User).filter(models.User.email == email.lower().strip()).first()


def authenticate_user(db: Session, email: str, password: str) -> Optional[models.User]:
    user = get_user_by_email(db, email)
    if not user or not _pwd_context.verify(password, user.hashed_password):
        return None
    return user


# ==================== API Key Operations ====================

def create_api_key(db: Session, key_name: str, api_key: str, user_id: Optional[int] = None) -> schemas.ApiKeyResponse:
    """Create a new API key and return a decoupled schema with plaintext key."""
    encrypted_key = encrypt(api_key)
    db_key = models.ApiKey(
        name=key_name,
        api_key=encrypted_key,
        is_active=True,
        user_id=user_id,
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
                return db_key
        except Exception:
            continue
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

def get_api_keys_by_user(db: Session, user_id: int, skip: int = 0, limit: int = 100) -> List[schemas.ApiKeyResponse]:
    """List API keys belonging to a specific user, with decrypted values."""
    db_keys = db.query(models.ApiKey).filter(models.ApiKey.user_id == user_id).offset(skip).limit(limit).all()
    result = []
    for k in db_keys:
        schema = schemas.ApiKeyResponse.from_orm(k)
        try:
            schema.api_key = decrypt(schema.api_key)
        except Exception:
            pass
        result.append(schema)
    return result


def update_api_key_active_for_user(db: Session, key_id: str, user_id: int, is_active: bool) -> Optional[models.ApiKey]:
    """Update active status of an API key, scoped to the owning user."""
    db_key = db.query(models.ApiKey).filter(
        models.ApiKey.id == key_id,
        models.ApiKey.user_id == user_id,
    ).first()
    if not db_key:
        return None
    db_key.is_active = is_active
    db.commit()
    db.refresh(db_key)
    return db_key


def delete_api_key_for_user(db: Session, key_id: str, user_id: int) -> bool:
    """Delete an API key, scoped to the owning user."""
    db_key = db.query(models.ApiKey).filter(
        models.ApiKey.id == key_id,
        models.ApiKey.user_id == user_id,
    ).first()
    if not db_key:
        return False
    db.delete(db_key)
    db.commit()
    return True


# ==================== Rule Operations ====================

def create_rule(db: Session, rule: schemas.RuleCreate, created_by_key_id: Optional[str] = None) -> models.Rule:
    """Create a new rule."""
    db_rule = models.Rule(
        name=rule.name,
        url_pattern=rule.url_pattern,
        method=rule.method.upper(),
        status_code=rule.status_code,
        delay_s=rule.delay_s,
        mock_data=json.dumps(rule.mock_data),
        use_mock_backend=rule.use_mock_backend,
        ai_prompt=rule.ai_prompt,
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

def get_or_create_device(
    db: Session,
    device_id: str,
    api_key_id: str,
    app_version: str = "unknown",
    android_version: Optional[str] = None,
    internet_mode: str = "wifi"
) -> models.Device:
    """Get existing device or create a new one."""
    device = db.query(models.Device).filter(
        and_(
            models.Device.device_id == device_id,
            models.Device.api_key_id == api_key_id
        )
    ).first()

    if device:
        device.last_seen = datetime.utcnow()
        db.commit()
        db.refresh(device)
        return device

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
    intercepted_by_rule_id: Optional[int] = None,
    response_time_ms: Optional[int] = None,
    status_code: Optional[int] = None
) -> models.CallLog:
    """Log an API call for analytics."""
    db_log = models.CallLog(
        device_id=device_id,
        endpoint=endpoint,
        method=method,
        was_intercepted=was_intercepted,
        intercepted_by_rule_id=intercepted_by_rule_id,
        response_time_ms=response_time_ms,
        status_code=status_code
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
    method: str,
    request_data: Optional[Dict[str, Any]],
    response_mock_data: Dict[str, Any]
) -> models.InterceptionLog:
    """Log an interception event."""
    db_log = models.InterceptionLog(
        device_id=device_id,
        rule_id=rule_id,
        endpoint=endpoint,
        method=method,
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

    # Device health
    online_threshold = datetime.utcnow() - timedelta(minutes=30)

    connected = db.query(func.count(models.Device.id)).filter(
        models.Device.last_seen >= online_threshold
    ).scalar()

    last_heartbeat_row = db.query(func.max(models.Device.last_seen)).scalar()
    last_heartbeat = last_heartbeat_row.isoformat() + "Z" if last_heartbeat_row else None

    offline_today = db.query(func.count(models.Device.id)).filter(
        models.Device.last_seen >= cutoff_time,
        models.Device.last_seen < online_threshold
    ).scalar()

    avg_session_raw = db.query(
        func.avg(
            (func.julianday(models.Device.last_seen) - func.julianday(models.Device.first_seen)) * 24 * 60
        )
    ).filter(
        models.Device.last_seen >= cutoff_time
    ).scalar()
    avg_session_minutes = round(float(avg_session_raw), 1) if avg_session_raw else None

    # Call stats
    total_calls = db.query(func.count(models.CallLog.id)).filter(
        models.CallLog.timestamp >= cutoff_time
    ).scalar()

    unique_endpoints = db.query(
        models.CallLog.endpoint
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).distinct().count()

    # Use InterceptionLog as source of truth for intercepted counts
    intercepted_count = db.query(func.count(models.InterceptionLog.id)).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).scalar()

    interception_rate = intercepted_count / total_calls if total_calls > 0 else 0.0

    # Pre-compute per-endpoint interception counts from InterceptionLog, keyed by (endpoint, method)
    interception_per_endpoint = db.query(
        models.InterceptionLog.endpoint,
        models.InterceptionLog.method,
        func.count(models.InterceptionLog.id).label('count')
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).group_by(models.InterceptionLog.endpoint, models.InterceptionLog.method).all()
    interception_endpoint_map = {(row[0], row[1]): row[2] for row in interception_per_endpoint}

    # Endpoint analytics
    endpoint_stats = db.query(
        models.CallLog.endpoint,
        models.CallLog.method,
        func.count(models.CallLog.id).label('call_count'),
        func.avg(models.CallLog.response_time_ms).label('avg_response_time'),
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).group_by(
        models.CallLog.endpoint,
        models.CallLog.method
    ).all()

    # Get wifi/cellular breakdown per endpoint
    endpoints = []
    for ep in endpoint_stats:
        endpoint, method, call_count, avg_response = ep

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
            "was_intercepted_count": interception_endpoint_map.get((endpoint, method), 0),
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
            "timestamp": ri[3].isoformat() + "Z",
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

    # Error distribution (4xx / 5xx only)
    error_dist_query = db.query(
        models.CallLog.status_code,
        func.count(models.CallLog.id).label("count")
    ).filter(
        models.CallLog.timestamp >= cutoff_time,
        models.CallLog.status_code >= 400,
        models.CallLog.was_intercepted == False
    ).group_by(
        models.CallLog.status_code
    ).order_by(
        models.CallLog.status_code
    ).all()

    error_distribution = [
        {"status_code": row[0], "count": row[1]}
        for row in error_dist_query
        if row[0] is not None
    ]

    # Average latency by hour
    from sqlalchemy import text as sa_text
    latency_query = db.query(
        func.strftime("%H", models.CallLog.timestamp).label("hour"),
        func.avg(models.CallLog.response_time_ms).label("avg_ms")
    ).filter(
        models.CallLog.timestamp >= cutoff_time,
        models.CallLog.response_time_ms.isnot(None)
    ).group_by(
        func.strftime("%H", models.CallLog.timestamp)
    ).order_by("hour").all()

    latency_by_hour = [
        {"hour": row[0], "avg_ms": round(row[1], 1)}
        for row in latency_query
        if row[0] is not None and row[1] is not None
    ]

    # Traffic over time (total from CallLog, intercepted from InterceptionLog)
    traffic_format = "%H" if time_range == "today" else "%Y-%m-%d"
    traffic_query = db.query(
        func.strftime(traffic_format, models.CallLog.timestamp).label("bucket"),
        func.count(models.CallLog.id).label("total"),
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).group_by(
        func.strftime(traffic_format, models.CallLog.timestamp)
    ).order_by("bucket").all()

    interception_bucket_query = db.query(
        func.strftime(traffic_format, models.InterceptionLog.timestamp).label("bucket"),
        func.count(models.InterceptionLog.id).label("intercepted")
    ).filter(
        models.InterceptionLog.timestamp >= cutoff_time
    ).group_by(
        func.strftime(traffic_format, models.InterceptionLog.timestamp)
    ).all()
    intercepted_by_bucket = {row[0]: row[1] for row in interception_bucket_query}

    traffic_over_time = [
        {"bucket": row[0], "total": row[1], "intercepted": intercepted_by_bucket.get(row[0], 0)}
        for row in traffic_query
        if row[0] is not None
    ]

    return {
        "time_range": time_range,
        "device_health": {
            "connected": connected,
            "last_heartbeat": last_heartbeat,
            "offline_today": offline_today,
            "avg_session_minutes": avg_session_minutes,
        },
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
        "app_versions": app_versions,
        "error_distribution": error_distribution,
        "latency_by_hour": latency_by_hour,
        "traffic_over_time": traffic_over_time
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
            "timestamp": il.timestamp.isoformat() + "Z",
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

    # Rule effectiveness: enabled rules only with hit count and last used timestamp
    all_rules = db.query(models.Rule).filter(models.Rule.is_enabled == True).all()
    rule_effectiveness = []
    for rule in all_rules:
        hits = db.query(func.count(models.InterceptionLog.id)).filter(
            models.InterceptionLog.rule_id == rule.id,
            models.InterceptionLog.timestamp >= cutoff_time
        ).scalar() or 0

        last_used_ts = db.query(func.max(models.InterceptionLog.timestamp)).filter(
            models.InterceptionLog.rule_id == rule.id
        ).scalar()

        rule_effectiveness.append({
            "rule_id": rule.id,
            "rule_name": rule.name,
            "endpoint": rule.url_pattern,
            "hits": hits,
            "last_used": last_used_ts.isoformat() + "Z" if last_used_ts else None
        })

    rule_effectiveness.sort(key=lambda x: x["hits"], reverse=True)

    # Endpoint interception rate: total calls vs intercepted per endpoint+method
    endpoint_rate_query = db.query(
        models.CallLog.endpoint,
        models.CallLog.method,
        func.count(models.CallLog.id).label('total_calls'),
        func.sum(case((models.CallLog.was_intercepted == True, 1), else_=0)).label('intercepted')
    ).filter(
        models.CallLog.timestamp >= cutoff_time
    ).group_by(
        models.CallLog.endpoint,
        models.CallLog.method
    ).all()

    endpoint_interception_rate = []
    for row in endpoint_rate_query:
        endpoint, method, total_calls, intercepted = row
        intercepted = int(intercepted or 0)
        rate = round((intercepted / total_calls * 100), 1) if total_calls > 0 else 0.0
        endpoint_interception_rate.append({
            "endpoint": endpoint,
            "method": method,
            "total_calls": total_calls,
            "intercepted": intercepted,
            "rate": rate
        })

    endpoint_interception_rate.sort(key=lambda x: x["rate"], reverse=True)

    return {
        "time_range": time_range,
        "total_interceptions": total_interceptions,
        "most_intercepted_endpoints": most_intercepted_endpoints,
        "recent_interceptions": recent_interceptions,
        "rule_usage": rule_usage,
        "rule_effectiveness": rule_effectiveness,
        "endpoint_interception_rate": endpoint_interception_rate
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
