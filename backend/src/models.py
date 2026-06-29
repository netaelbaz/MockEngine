"""SQLAlchemy ORM models for MockEngine database."""

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.database import Base


class User(Base):
    """Users table for portal authentication."""

    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String, unique=True, nullable=False, index=True)
    first_name = Column(String, nullable=False, default="")
    last_name = Column(String, nullable=False, default="")
    hashed_password = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    api_keys = relationship("ApiKey", back_populates="user")


class ApiKey(Base):
    """API Keys table for SDK authentication."""

    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, doc="User-friendly name for the API key")
    api_key = Column(String, unique=True, nullable=False, index=True, doc="Hashed API key secret")
    is_active = Column(Boolean, default=True, nullable=False, doc="Whether the key is active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="Creation timestamp")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)

    # Relationships
    user = relationship("User", back_populates="api_keys")
    rules = relationship("Rule", back_populates="created_by", foreign_keys="Rule.created_by_key_id")
    devices = relationship("Device", back_populates="api_key")

    def __repr__(self):
        return f"<ApiKey(id={self.id}, name={self.name})>"


class Rule(Base):
    """Interception rules table for defining mock responses."""

    __tablename__ = "rules"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String, nullable=False, unique=True, doc="User-friendly rule name")
    url_pattern = Column(String, nullable=False, doc="URL regex or path pattern to match")
    method = Column(String, nullable=True, default="GET", doc="HTTP method: GET, POST, PUT, DELETE, PATCH or ANY")
    status_code = Column(Integer, nullable=True, doc="HTTP response code to return, or None to pass through")
    delay_s = Column(Integer, default=0, nullable=False, doc="Response delay in seconds")
    mode = Column(String, nullable=True, doc="Rule mode (deprecated - no longer used)")
    mock_data = Column(Text, nullable=False, doc="JSON string of mock response data")
    use_mock_backend = Column(Boolean, nullable=False, default=True, doc="When false, SDK hits real server and uses rule only for status/body overrides")
    ai_prompt = Column(Text, nullable=True, doc="AI prompt used to generate mock_data")
    is_enabled = Column(Boolean, default=True, nullable=False, doc="Whether the rule is active")
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="Creation timestamp")
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, doc="Last update timestamp")
    created_by_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=True, doc="API key that created this rule")

    # Relationships
    created_by = relationship("ApiKey", back_populates="rules", foreign_keys=[created_by_key_id])
    call_logs = relationship("CallLog", back_populates="intercepted_by_rule")
    interception_logs = relationship("InterceptionLog", back_populates="rule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Rule(id={self.id}, name={self.name}, url_pattern={self.url_pattern})>"


class Device(Base):
    """Devices table for tracking registered mobile devices."""

    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(String, nullable=False, index=True, doc="Unique device identifier")
    api_key_id = Column(Integer, ForeignKey("api_keys.id"), nullable=False, doc="Associated API key")
    app_version = Column(String, nullable=False, doc="Application version")
    android_version = Column(String, nullable=True, doc="Android version")
    internet_mode = Column(String, nullable=False, doc="Internet mode: 'wifi', 'cellular', or 'none'")
    first_seen = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="First registration timestamp")
    last_seen = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False, doc="Last activity timestamp")

    # Relationships
    api_key = relationship("ApiKey", back_populates="devices")
    call_logs = relationship("CallLog", back_populates="device")
    interception_logs = relationship("InterceptionLog", back_populates="device")

    def __repr__(self):
        return f"<Device(id={self.id}, device_id={self.device_id})>"


class CallLog(Base):
    """Call logs table for analytics and API call tracking."""

    __tablename__ = "call_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, doc="Device that made the call")
    endpoint = Column(String, nullable=False, doc="URL endpoint that was called")
    method = Column(String, nullable=False, doc="HTTP method: GET, POST, etc.")
    was_intercepted = Column(Boolean, default=False, nullable=False, doc="Whether the call was intercepted")
    intercepted_by_rule_id = Column(Integer, ForeignKey("rules.id"), nullable=True, doc="Rule that intercepted the call")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="Call timestamp")
    response_time_ms = Column(Integer, nullable=True, doc="Actual response time in milliseconds")
    status_code = Column(Integer, nullable=True, doc="HTTP response status code")

    # Relationships
    device = relationship("Device", back_populates="call_logs")
    intercepted_by_rule = relationship("Rule", back_populates="call_logs")

    def __repr__(self):
        return f"<CallLog(id={self.id}, endpoint={self.endpoint}, was_intercepted={self.was_intercepted})>"


class InterceptionLog(Base):
    """Interception logs table for detailed interception event tracking."""

    __tablename__ = "interception_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    device_id = Column(Integer, ForeignKey("devices.id"), nullable=False, index=True, doc="Device that triggered interception")
    rule_id = Column(Integer, ForeignKey("rules.id"), nullable=False, doc="Rule that was applied")
    endpoint = Column(String, nullable=False, doc="Intercepted endpoint URL")
    method = Column(String, nullable=True, doc="HTTP method: GET, POST, etc.")
    request_data = Column(Text, nullable=True, doc="JSON string of request details")
    response_mock_data = Column(Text, nullable=False, doc="JSON string of mock response returned")
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), nullable=False, doc="Interception timestamp")

    # Relationships
    device = relationship("Device", back_populates="interception_logs")
    rule = relationship("Rule", back_populates="interception_logs")

    def __repr__(self):
        return f"<InterceptionLog(id={self.id}, endpoint={self.endpoint}, rule_id={self.rule_id})>"
