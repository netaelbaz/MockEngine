"""Pydantic schemas for request/response validation."""

from pydantic import BaseModel, Field, validator
from typing import Optional, Dict, Any, List
from datetime import datetime
import enum


# ==================== User / Auth Schemas ====================

class UserCreate(BaseModel):
    email: str = Field(..., min_length=3, max_length=254)
    password: str = Field(..., min_length=6, max_length=128)
    first_name: str = Field(..., min_length=1, max_length=100)
    last_name: str = Field(..., min_length=1, max_length=100)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    first_name: str = ""
    last_name: str = ""
    email: str = ""


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
    method: str = Field("GET", description="HTTP method: GET, POST, PUT, DELETE, PATCH, or ANY")
    status_code: Optional[int] = Field(None, ge=100, le=599, description="HTTP response code (None = pass through real response code)")
    delay_s: int = Field(0, ge=0, description="Response delay in seconds")
    mock_data: Dict[str, Any] = Field(..., description="Mock response data as JSON object")
    use_mock_backend: bool = Field(True, description="When false, SDK hits real server and uses rule only for status/body overrides")
    ai_prompt: Optional[str] = Field(None, description="AI prompt used to generate mock_data")

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
    method: Optional[str] = None
    status_code: Optional[int] = Field(None, ge=100, le=599)
    delay_s: Optional[int] = Field(None, ge=0, le=60)
    mock_data: Optional[Dict[str, Any]] = None
    use_mock_backend: Optional[bool] = None
    is_enabled: Optional[bool] = None
    ai_prompt: Optional[str] = None

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
    method: str = "GET"
    status_code: Optional[int] = None
    delay_s: int
    mock_data: Dict[str, Any]
    use_mock_backend: bool = True
    ai_prompt: Optional[str] = None
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
    method: str = "GET"
    status_code: Optional[int] = None
    delay_s: int
    mock_data: Dict[str, Any]
    use_mock_backend: bool = True
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
    interceptedByRuleId: Optional[int] = Field(None, description="Rule ID that intercepted the call")
    responseTimeMs: Optional[int] = Field(None, ge=0, description="Response time in milliseconds")
    statusCode: Optional[int] = Field(None, description="HTTP response status code")


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
    ruleId: int = Field(..., description="Rule ID that was applied")
    endpoint: str = Field(..., min_length=1, description="Intercepted endpoint URL")
    method: str = Field(..., min_length=1, description="HTTP method: GET, POST, etc.")
    requestData: Optional[Dict[str, Any]] = Field(None, description="Request details as JSON object")
    responseMockData: Dict[str, Any] = Field(..., description="Mock response data as JSON object")


class InterceptionLogResponse(BaseModel):
    """Schema for interception log response."""
    id: int
    device_id: int
    rule_id: int
    endpoint: str
    method: Optional[str]
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
    timestamp: str
    device_id: str


class ErrorDistributionItem(BaseModel):
    """Schema for a single status code error count."""
    status_code: int
    count: int


class LatencyByHourItem(BaseModel):
    """Schema for average latency in a given hour."""
    hour: str
    avg_ms: float


class TrafficOverTimeItem(BaseModel):
    """Schema for total and intercepted requests in a time bucket."""
    bucket: str
    total: int
    intercepted: int


class DeviceHealth(BaseModel):
    """Schema for device health metrics."""
    connected: int
    last_heartbeat: Optional[str] = None
    offline_today: int
    avg_session_minutes: Optional[float] = None


class AnalyticsOverviewResponse(BaseModel):
    """Schema for analytics overview response."""
    time_range: TimeRange
    devices: DeviceStats
    calls: CallStats
    endpoints: List[EndpointAnalytics]
    recent_interceptions: List[RecentInterception]
    app_versions: List[AppVersionStat]
    error_distribution: List[ErrorDistributionItem]
    latency_by_hour: List[LatencyByHourItem]
    traffic_over_time: List[TrafficOverTimeItem]
    device_health: DeviceHealth


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
    timestamp: str
    device_id: str
    response_mock_data: Dict[str, Any]


class RuleUsage(BaseModel):
    """Schema for rule usage statistics."""
    rule_id: int
    rule_name: str
    usage_count: int


class RuleEffectiveness(BaseModel):
    """Schema for rule effectiveness analytics."""
    rule_id: int
    rule_name: str
    endpoint: str
    hits: int
    last_used: Optional[str] = None


class EndpointInterceptionRate(BaseModel):
    """Schema for endpoint interception rate analytics."""
    endpoint: str
    method: str
    total_calls: int
    intercepted: int
    rate: float


class InterceptionAnalyticsResponse(BaseModel):
    """Schema for interception analytics response."""
    time_range: TimeRange
    total_interceptions: int
    most_intercepted_endpoints: List[MostInterceptedEndpoint]
    recent_interceptions: List[RecentInterceptionDetail]
    rule_usage: List[RuleUsage]
    rule_effectiveness: List[RuleEffectiveness]
    endpoint_interception_rate: List[EndpointInterceptionRate]


class DeviceAnalytics(BaseModel):
    """Schema for device analytics."""
    total_devices: int
    active_today: int
    devices_by_version: List[AppVersionStat]
    devices_by_android_version: List[AndroidVersionStat]
    recent_devices: List[DeviceResponse]  # Use existing DeviceResponse


# ==================== AI Schemas ====================

class AIGenerateRequest(BaseModel):
    """Schema for AI mock data generation request."""
    prompt: str = Field(..., min_length=1, description="Plain-English description of the data to generate")
    url_pattern: Optional[str] = Field(None, description="Optional URL pattern context hint")
    method: Optional[str] = Field(None, description="Optional HTTP method context hint")


class AIGenerateResponse(BaseModel):
    """Schema for AI mock data generation response."""
    mock_data: Dict[str, Any]
