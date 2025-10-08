"""
API routes for analytics and metrics.
Provides insights into persona interactions and system performance.
"""
from typing import List, Optional
from fastapi import APIRouter, Query, HTTPException
from datetime import datetime, timedelta
from loguru import logger

from app.models import AnalyticsSummary, InteractionEvent
from app.repositories.persona_repository import persona_repository
from app.telemetry.events import event_logger

router = APIRouter()


@router.get("/summary", response_model=AnalyticsSummary)
async def get_analytics_summary(
    days: int = Query(default=7, ge=1, le=90, description="Number of days to analyze")
):
    """Get analytics summary for the specified period"""
    try:
        logger.info(f"📊 Getting analytics summary for {days} days")
        
        # Get summary from event logger
        summary_data = await event_logger.get_analytics_summary(days)
        
        # Get additional persona metrics
        total_personas = await persona_repository.count_personas()
        
        # Calculate popular categories from personas
        all_personas = await persona_repository.list_personas(limit=1000)
        category_counts = {}
        readiness_counts = {}
        
        for persona in all_personas:
            # Count green interests
            for interest in persona.green_interests:
                category_counts[interest] = category_counts.get(interest, 0) + 1
            
            # Count readiness levels
            readiness_counts[persona.readiness_level] = readiness_counts.get(persona.readiness_level, 0) + 1
        
        # Format popular categories
        popular_categories = [
            {"category": cat, "count": count}
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Create analytics summary
        analytics = AnalyticsSummary(
            total_personas=total_personas,
            total_interactions=summary_data["total_interactions"],
            unique_active_personas=summary_data["unique_personas"],
            avg_interactions_per_persona=summary_data["avg_interactions_per_persona"],
            success_rate=summary_data["success_rate"],
            popular_categories=popular_categories,
            language_distribution=summary_data["language_distribution"],
            readiness_distribution=readiness_counts,
            top_recommendations=[]  # Will be populated when recommendation system is implemented
        )
        
        logger.info(f"✅ Generated analytics summary: {total_personas} personas, {summary_data['total_interactions']} interactions")
        return analytics
        
    except Exception as e:
        logger.error(f"❌ Failed to get analytics summary: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve analytics summary")


@router.get("/persona/{persona_id}")
async def get_persona_analytics(persona_id: str):
    """Get detailed analytics for a specific persona"""
    try:
        logger.info(f"👤 Getting analytics for persona {persona_id}")
        
        # Get persona details
        persona = await persona_repository.get_persona(persona_id)
        if not persona:
            raise HTTPException(status_code=404, detail="Persona not found")
        
        # Get persona interactions
        interactions = await event_logger.get_persona_interactions(persona_id)
        
        # Calculate persona-specific metrics
        total_interactions = len(interactions)
        successful_interactions = len([i for i in interactions if i.get('success', False)])
        success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0
        
        # Task type breakdown
        task_breakdown = {}
        agent_usage = {}
        
        for interaction in interactions:
            task_type = interaction.get('task_type', 'unknown')
            agent_used = interaction.get('agent_used', 'unknown')
            
            task_breakdown[task_type] = task_breakdown.get(task_type, 0) + 1
            agent_usage[agent_used] = agent_usage.get(agent_used, 0) + 1
        
        # Calculate average interaction duration
        durations = [i.get('duration_ms', 0) for i in interactions if i.get('duration_ms')]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        return {
            "persona_id": persona_id,
            "persona_name": persona.name,
            "total_interactions": total_interactions,
            "success_rate": success_rate,
            "avg_duration_ms": avg_duration,
            "task_breakdown": task_breakdown,
            "agent_usage": agent_usage,
            "recent_interactions": interactions[:10],  # Last 10 interactions
            "persona_profile": {
                "age": persona.age,
                "location": f"{persona.location_city}, {persona.location_state}",
                "readiness_level": persona.readiness_level,
                "green_interests": persona.green_interests,
                "preferred_language": persona.preferred_language
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get persona analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve persona analytics")


@router.get("/events")
async def get_events(
    limit: int = Query(default=100, le=500, description="Maximum number of events to return"),
    offset: int = Query(default=0, ge=0, description="Number of events to skip"),
    event_type: Optional[str] = Query(default=None, description="Filter by event type"),
    persona_id: Optional[str] = Query(default=None, description="Filter by persona ID"),
    days: int = Query(default=7, ge=1, le=90, description="Number of days to look back")
):
    """Get paginated list of events with optional filtering"""
    try:
        logger.info(f"📝 Getting events: limit={limit}, offset={offset}, type={event_type}")
        
        events = await event_logger.get_events(
            limit=limit,
            offset=offset,
            event_type=event_type,
            persona_id=persona_id
        )
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        filtered_events = []
        
        for event in events:
            event_timestamp = event.get('timestamp')
            if isinstance(event_timestamp, str):
                event_timestamp = datetime.fromisoformat(event_timestamp)
            
            if isinstance(event_timestamp, datetime) and event_timestamp > cutoff_date:
                filtered_events.append(event)
        
        return {
            "events": filtered_events,
            "total_returned": len(filtered_events),
            "limit": limit,
            "offset": offset,
            "filters": {
                "event_type": event_type,
                "persona_id": persona_id,
                "days": days
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get events: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve events")


@router.get("/trends")
async def get_trends(
    days: int = Query(default=30, ge=7, le=90, description="Number of days for trend analysis")
):
    """Get trend analysis over time"""
    try:
        logger.info(f"📈 Getting trends for {days} days")
        
        # Get all events for the period
        all_events = await event_logger.get_events(limit=10000)
        
        # Filter by date range
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        recent_events = []
        
        for event in all_events:
            event_timestamp = event.get('timestamp')
            if isinstance(event_timestamp, str):
                event_timestamp = datetime.fromisoformat(event_timestamp)
            
            if isinstance(event_timestamp, datetime) and event_timestamp > cutoff_date:
                recent_events.append(event)
        
        # Group events by day
        daily_stats = {}
        for event in recent_events:
            event_timestamp = event.get('timestamp')
            if isinstance(event_timestamp, str):
                event_timestamp = datetime.fromisoformat(event_timestamp)
            
            day_key = event_timestamp.date().isoformat()
            
            if day_key not in daily_stats:
                daily_stats[day_key] = {
                    "date": day_key,
                    "total_events": 0,
                    "interactions": 0,
                    "unique_personas": set(),
                    "success_rate": 0
                }
            
            daily_stats[day_key]["total_events"] += 1
            
            if event.get('event_type') in ['assistant_interaction', 'interaction']:
                daily_stats[day_key]["interactions"] += 1
                if event.get('persona_id'):
                    daily_stats[day_key]["unique_personas"].add(event['persona_id'])
        
        # Calculate success rates and format response
        trend_data = []
        for day_key in sorted(daily_stats.keys()):
            stats = daily_stats[day_key]
            stats["unique_personas"] = len(stats["unique_personas"])
            
            # Calculate success rate (mock for now)
            stats["success_rate"] = 0.85 if stats["interactions"] > 0 else 0
            
            trend_data.append(stats)
        
        return {
            "period_days": days,
            "daily_trends": trend_data,
            "summary": {
                "total_days": len(trend_data),
                "avg_daily_interactions": sum(d["interactions"] for d in trend_data) / len(trend_data) if trend_data else 0,
                "peak_day": max(trend_data, key=lambda x: x["interactions"]) if trend_data else None
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get trends: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve trends")


@router.get("/health")
async def analytics_health():
    """Health check for analytics service"""
    try:
        # Get basic metrics
        total_personas = await persona_repository.count_personas()
        summary = await event_logger.get_analytics_summary(1)  # Last 24 hours
        
        return {
            "status": "healthy",
            "total_personas": total_personas,
            "events_last_24h": summary["total_interactions"],
            "telemetry_enabled": event_logger.enabled,
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ Analytics health check failed: {e}")
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat()
        }