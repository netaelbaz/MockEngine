"""Analytics router for aggregated statistics and monitoring."""

from fastapi import APIRouter, Query, Depends
from sqlalchemy.orm import Session
from typing import Dict, Any

from src.database import get_db
from src import crud, schemas

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics"])


@router.get("/overview", response_model=schemas.AnalyticsOverviewResponse)
def get_analytics_overview(
    time_range: schemas.TimeRange = Query(
        schemas.TimeRange.today,
        description="Time range for analytics: today, week, or month"
    ),
    db: Session = Depends(get_db)
):
    """
    Get aggregated overview statistics.

    Returns comprehensive analytics including device stats,
    call statistics, endpoint analytics, and recent interceptions.

    Query parameters:
    - time_range: 'today' (last 24h), 'week' (last 7 days), 'month' (last 30 days)
    """
    analytics_data = crud.get_analytics_overview(db, time_range.value)

    return schemas.AnalyticsOverviewResponse(**analytics_data)


@router.get("/interceptions", response_model=schemas.InterceptionAnalyticsResponse)
def get_interception_analytics(
    time_range: schemas.TimeRange = Query(
        schemas.TimeRange.today,
        description="Time range for analytics: today, week, or month"
    ),
    db: Session = Depends(get_db)
):
    """
    Get interception-specific analytics.

    Returns statistics about intercepted endpoints,
    recent interception events, and rule usage patterns.

    Query parameters:
    - time_range: 'today' (last 24h), 'week' (last 7 days), 'month' (last 30 days)
    """
    analytics_data = crud.get_interception_analytics(db, time_range.value)

    return schemas.InterceptionAnalyticsResponse(**analytics_data)


@router.get("/devices", response_model=schemas.DeviceAnalytics)
def get_device_analytics(
    time_range: schemas.TimeRange = Query(
        schemas.TimeRange.today,
        description="Time range for analytics: today, week, or month"
    ),
    db: Session = Depends(get_db)
):
    """
    Get device analytics.

    Returns statistics about connected devices,
    version distribution, and recent device activity.

    Query parameters:
    - time_range: 'today' (last 24h), 'week' (last 7 days), 'month' (last 30 days)
    """
    analytics_data = crud.get_device_analytics(db, time_range.value)

    return schemas.DeviceAnalytics(**analytics_data)
