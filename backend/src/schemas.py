"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import enum


# ==================== API Key Schemas ====================

class ApiKeyCreate(BaseModel):
    """Schema for creating a new API key."""
    key_name: str = Field(..., min_length=1, max_length=100, description="User-friendly name for the API key")


class ApiKeyResponse(BaseModel):
    """Schema for API key response."""
    id: int
    name: str
    api_key: str
    is_active: bool
    created_at: datetime

    class Config:
        from_attributes = True


class ApiKeyValidate(BaseModel):
    """Schema for API key validation request."""
    api_key: str = Field(..., description="API key to validate")


# ==================== Rule Schemas ====================

class RuleCreate(BaseModel):
    """Schema for creating a new rule."""
    name: str = Field(..., min_length=1, max_length=200, description="User-friendly rule name")
    url_pattern: str = Field(..., min_length=1, description="URL regex or path pattern to match")
    status_code: int = Field(..., ge=100, le=599, description="HTTP response code")
    delay_ms: int = Field(0, ge=0, le=60000, description="Response delay in milliseconds")
    mock_data: Dict[str, Any] = Field(..., description="Mock response data as JSON object")

    @validator("mock_data")
    def validate_mock_data_is_dict(cls, v):
        """Ensure mock_data is a dictionary."""
        if not isinstance(v, dict):
            raise ValueError("mock_data must be a JSON object/dictionary")
        return v


class RuleUpdate(BaseModel):
    """Schema for updating an existing rule."""
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    url_pattern: Optional[str] = Field(None, min_length=1)
    status_code: Optional[int] = Field(None, ge=100, le=599)
    delay_ms: Optional[int] = Field(None, ge=0, le=60000)
    mock_data: Optional[Dict[str, Any]] = None
    is_enabled: Optional[bool] = None

    @validator("mock_data")
    def validate_mock_data_is_dict(cls, v):
        """Ensure mock_data is a dictionary if provided."""
        if v is not None and not isinstance(v, dict):
            raise ValueError("mock_data must be a JSON object/dictionary")
        return v


class RuleResponse(BaseModel):
    """Schema for rule response."""
    id: int
    name: str
    url_pattern: str
    status_code: int
    delay_ms: int
    mock_data: Dict[str, Any]
    is_enabled: bool
    created_at: datetime
    updated_at: datetime
    created_by_key_id: Optional[str] = None

    class Config:
        from_attributes = True


class RuleSDKResponse(BaseModel):
    """Schema for rule response in SDK config (minimal fields)."""
    id: int
    url_pattern: str
    status_code: int
    delay_ms: int
    mock_data: Dict[str, Any]
    is_enabled: bool

    class Config:
        from_attributes = True


# ==================== Device Schemas ====================

class InternetMode(str, enum.Enum):
    """Enumeration of internet modes."""
    wifi = "wifi"
    cellular = "cellular"
    none = "none"


class DeviceRegister(BaseModel):
    """Schema for device registration."""
    deviceId: str = Field(..., min_length=1, description="Unique device identifier")
    appVersion: str = Field(..., min_length=1, description="Application version")
    androidVersion: Optional[str] = Field(None, description="Android version")
    internetMode: InternetMode = Field(..., description="Internet mode: wifi, cellular, or none")


class DeviceResponse(BaseModel):
    """Schema for device response."""
    id: int
    device_id: str
    api_key_id: int
    app_version: str
    android_version: Optional[str]
    internet_mode: str
    first_seen: datetime
    last_seen: datetime

    class Config:
        from_attributes = True


# ==================== Log Schemas ====================

class CallLogCreate(BaseModel):
    """Schema for creating a call log."""
    deviceId: str = Field(..., description="Device identifier")
    endpoint: str = Field(..., min_length=1, description="URL endpoint that was called")
    method: str = Field(..., min_length=1, description="HTTP method")
    wasIntercepted: bool = Field(default=False, description="Whether the call was intercepted")
    interceptedByRuleId: Optional[str] = Field(None, description="Rule ID that intercepted the call")
    responseTimeMs: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")


class CallLogResponse(BaseModel):
    """Schema for call log response."""
    id: int
    device_id: int
    endpoint: str
    method: str
    was_intercepted: bool
    intercepted_by_rule_id: Optional[int]
    timestamp: datetime
    response_time_ms: Optional[int]

    class Config:
        from_attributes = True


class InterceptionLogCreate(BaseModel):
    """Schema for creating an interception log."""
    deviceId: str = Field(..., description="Device identifier")
    ruleId: str = Field(..., description="Rule ID that was applied")
    endpoint: str = Field(..., min_length=1, description="Intercepted endpoint URL")
    requestData: Optional[Dict[str, Any]] = Field(None, description="Request details as JSON object")
    responseMockData: Dict[str, Any] = Field(..., description="Mock response data as JSON object")


class InterceptionLogResponse(BaseModel):
    """Schema for interception log response."""
    id: int
    device_id: int
    rule_id: int
    endpoint: str
    request_data: Optional[str]
    response_mock_data: str
    timestamp: datetime

    class Config:
        from_attributes = True


# ==================== Common Schemas ====================

class SuccessResponse(BaseModel):
    """Schema for success response."""
    status: str = "success"
    message: str


class MessageResponse(BaseModel):
    """Schema for generic message response."""
    message: str


# ==================== Analytics Schemas ====================


class TimeRange(str, enum.Enum):
    """Enumeration of time ranges for analytics."""
    today = "today"
    week = "week"
    month = "month"


class AndroidVersionStat(BaseModel):
    """Schema for Android version statistics."""
    version: str
    count: int


class InternetModeStat(BaseModel):
    """Schema for internet mode statistics."""
    wifi: int
    cellular: int


class DeviceStats(BaseModel):
    """Schema for device statistics."""
    total_connected: int
    active_today: int
    android_versions: List[AndroidVersionStat]
    internet_modes: Dict[str, int]


class CallStats(BaseModel):
    """Schema for call statistics."""
    total_calls: int
    unique_endpoints: int
    intercepted_count: int
    interception_rate: float


class EndpointAnalytics(BaseModel):
    """Schema for endpoint analytics."""
    endpoint: str
    method: str
    call_count: int
    avg_response_time_ms: Optional[int] = None
    was_intercepted_count: int
    wifi_calls: int
    cellular_calls: int


class AppVersionStat(BaseModel):
    """Schema for app version statistics."""
    version: str
    count: int
    percentage: float
    is_latest: bool


class RecentInterception(BaseModel):
    """Schema for recent interception item."""
    id: int
    endpoint: str
    rule_name: str
    timestamp: datetime
    device_id: str


class AnalyticsOverviewResponse(BaseModel):
    """Schema for analytics overview response."""
    time_range: TimeRange
    devices: DeviceStats
    calls: CallStats
    endpoints: List[EndpointAnalytics]
    recent_interceptions: List[RecentInterception]
    app_versions: List[AppVersionStat]


class MostInterceptedEndpoint(BaseModel):
    """Schema for most intercepted endpoint."""
    endpoint: str
    count: int
    rule_name: str


class RecentInterceptionDetail(BaseModel):
    """Schema for recent interception with details."""
    id: int
    endpoint: str
    rule_name: str
    timestamp: datetime
    device_id: str
    response_mock_data: Dict[str, Any]


class RuleUsage(BaseModel):
    """Schema for rule usage statistics."""
    rule_id: int
    rule_name: str
    usage_count: int


class InterceptionAnalyticsResponse(BaseModel):
    """Schema for interception analytics response."""
    time_range: TimeRange
    total_interceptions: int
    most_intercepted_endpoints: List[MostInterceptedEndpoint]
    recent_interceptions: List[RecentInterceptionDetail]
    rule_usage: List[RuleUsage]


class DeviceAnalytics(BaseModel):
    """Schema for device analytics."""
    total_devices: int
    active_today: int
    devices_by_version: List[AppVersionStat]
    devices_by_android_version: List[AndroidVersionStat]
    recent_devices: List[DeviceResponse]  # Use existing DeviceResponse
