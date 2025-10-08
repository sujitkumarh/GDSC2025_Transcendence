"""
Event logging and telemetry for Transcendence.
Tracks user interactions and system performance.
"""
import json
import os
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import uuid
from loguru import logger

from app.models import InteractionEvent
from app.core.config import settings


class EventLogger:
    """Event logging system for analytics and monitoring"""
    
    def __init__(self):
        self.data_dir = settings.DATA_DIR
        self.events_file = os.path.join(self.data_dir, "events.json")
        self.enabled = settings.TELEMETRY_ENABLED
        self._events_cache = []
        self._ensure_data_dir()
        self._load_events()
    
    def _ensure_data_dir(self):
        """Ensure data directory exists"""
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Create empty events file if it doesn't exist
        if not os.path.exists(self.events_file):
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def _load_events(self):
        """Load events from JSON file"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                events_data = json.load(f)
            
            self._events_cache = []
            for event_dict in events_data:
                # Convert timestamp string back to datetime
                if 'timestamp' in event_dict:
                    event_dict['timestamp'] = datetime.fromisoformat(event_dict['timestamp'])
                
                # Create InteractionEvent if it matches the schema
                if self._is_interaction_event(event_dict):
                    self._events_cache.append(InteractionEvent(**event_dict))
                else:
                    # Store as generic event dict for non-interaction events
                    self._events_cache.append(event_dict)
            
            logger.info(f"📊 Loaded {len(self._events_cache)} events from storage")
            
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.warning(f"⚠️ Could not load events: {e}, starting with empty cache")
            self._events_cache = []
    
    def _is_interaction_event(self, event_dict: Dict[str, Any]) -> bool:
        """Check if event dict matches InteractionEvent schema"""
        required_fields = ['id', 'timestamp', 'persona_id', 'event_type', 'task_type', 'agent_used', 'language', 'success', 'duration_ms']
        return all(field in event_dict for field in required_fields)
    
    def _save_events(self):
        """Save events cache to JSON file"""
        if not self.enabled:
            return
            
        try:
            # Convert events to serializable format
            events_data = []
            for event in self._events_cache:
                if isinstance(event, InteractionEvent):
                    event_dict = event.dict()
                    event_dict['timestamp'] = event_dict['timestamp'].isoformat()
                    events_data.append(event_dict)
                else:
                    # Handle generic event dicts
                    event_copy = event.copy()
                    if 'timestamp' in event_copy and isinstance(event_copy['timestamp'], datetime):
                        event_copy['timestamp'] = event_copy['timestamp'].isoformat()
                    events_data.append(event_copy)
            
            # Keep only recent events to prevent file from growing too large
            retention_days = settings.ANALYTICS_RETENTION_DAYS
            cutoff_date = datetime.utcnow() - timedelta(days=retention_days)
            
            filtered_events = []
            for event_dict in events_data:
                event_timestamp = datetime.fromisoformat(event_dict['timestamp'])
                if event_timestamp > cutoff_date:
                    filtered_events.append(event_dict)
            
            # Write to file
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(filtered_events, f, ensure_ascii=False, indent=2)
            
            logger.debug(f"💾 Saved {len(filtered_events)} events to storage")
            
        except Exception as e:
            logger.error(f"❌ Failed to save events: {e}")
    
    async def initialize(self):
        """Initialize the event logger"""
        if self.enabled:
            await self.log_event("event_logger_initialized", {
                "retention_days": settings.ANALYTICS_RETENTION_DAYS,
                "events_loaded": len(self._events_cache)
            })
            logger.info("📊 Event logger initialized")
    
    async def log_event(self, event_type: str, metadata: Dict[str, Any]):
        """Log a general event"""
        if not self.enabled:
            return
        
        event = {
            "id": str(uuid.uuid4()),
            "timestamp": datetime.utcnow(),
            "event_type": event_type,
            "metadata": metadata
        }
        
        self._events_cache.append(event)
        
        # Periodically save to disk (every 10 events)
        if len(self._events_cache) % 10 == 0:
            self._save_events()
        
        logger.debug(f"📝 Logged event: {event_type}")
    
    async def log_interaction(
        self,
        persona_id: str,
        event_type: str,
        task_type: str,
        agent_used: str,
        language: str,
        success: bool,
        duration_ms: int,
        user_feedback: Optional[int] = None,
        metadata: Dict[str, Any] = None
    ):
        """Log an interaction event"""
        if not self.enabled:
            return
        
        interaction_event = InteractionEvent(
            id=str(uuid.uuid4()),
            timestamp=datetime.utcnow(),
            persona_id=persona_id,
            event_type=event_type,
            task_type=task_type,
            agent_used=agent_used,
            language=language,
            success=success,
            duration_ms=duration_ms,
            user_feedback=user_feedback,
            metadata=metadata or {}
        )
        
        self._events_cache.append(interaction_event)
        
        # Save to disk every 5 interactions
        if len([e for e in self._events_cache if isinstance(e, InteractionEvent)]) % 5 == 0:
            self._save_events()
        
        logger.debug(f"🎯 Logged interaction: {event_type} for {persona_id}")
    
    async def get_persona_interactions(self, persona_id: str) -> List[Dict[str, Any]]:
        """Get all interactions for a specific persona"""
        interactions = []
        for event in self._events_cache:
            if isinstance(event, InteractionEvent) and event.persona_id == persona_id:
                interactions.append(event.dict())
            elif isinstance(event, dict) and event.get('metadata', {}).get('persona_id') == persona_id:
                interactions.append(event)
        
        # Sort by timestamp (newest first)
        interactions.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        return interactions
    
    async def get_analytics_summary(self, days: int = 7) -> Dict[str, Any]:
        """Get analytics summary for the last N days"""
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        
        # Filter recent events
        recent_events = []
        for event in self._events_cache:
            if isinstance(event, InteractionEvent):
                if event.timestamp > cutoff_date:
                    recent_events.append(event)
            elif isinstance(event, dict):
                event_timestamp = event.get('timestamp')
                if isinstance(event_timestamp, str):
                    event_timestamp = datetime.fromisoformat(event_timestamp)
                if isinstance(event_timestamp, datetime) and event_timestamp > cutoff_date:
                    recent_events.append(event)
        
        # Calculate metrics
        total_interactions = len([e for e in recent_events if isinstance(e, InteractionEvent)])
        unique_personas = len(set(e.persona_id for e in recent_events if isinstance(e, InteractionEvent)))
        successful_interactions = len([e for e in recent_events if isinstance(e, InteractionEvent) and e.success])
        
        success_rate = successful_interactions / total_interactions if total_interactions > 0 else 0
        
        # Task type distribution
        task_distribution = {}
        for event in recent_events:
            if isinstance(event, InteractionEvent):
                task_type = event.task_type
                task_distribution[task_type] = task_distribution.get(task_type, 0) + 1
        
        # Language distribution
        language_distribution = {}
        for event in recent_events:
            if isinstance(event, InteractionEvent):
                language = event.language
                language_distribution[language] = language_distribution.get(language, 0) + 1
        
        return {
            "period_days": days,
            "total_interactions": total_interactions,
            "unique_personas": unique_personas,
            "success_rate": success_rate,
            "avg_interactions_per_persona": total_interactions / unique_personas if unique_personas > 0 else 0,
            "task_distribution": task_distribution,
            "language_distribution": language_distribution,
            "total_events": len(recent_events)
        }
    
    async def get_events(
        self, 
        limit: int = 100, 
        offset: int = 0, 
        event_type: Optional[str] = None,
        persona_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Get events with optional filtering"""
        events = []
        
        for event in self._events_cache:
            # Convert to dict format
            if isinstance(event, InteractionEvent):
                event_dict = event.dict()
            else:
                event_dict = event.copy()
            
            # Apply filters
            if event_type and event_dict.get('event_type') != event_type:
                continue
            if persona_id and event_dict.get('persona_id') != persona_id:
                continue
            
            events.append(event_dict)
        
        # Sort by timestamp (newest first)
        events.sort(key=lambda x: x.get('timestamp', ''), reverse=True)
        
        # Apply pagination
        return events[offset:offset + limit]
    
    async def close(self):
        """Close the event logger and save any pending events"""
        if self.enabled:
            self._save_events()
            await self.log_event("event_logger_closed", {
                "total_events": len(self._events_cache)
            })
            logger.info("📊 Event logger closed")


# Global event logger instance
event_logger = EventLogger()