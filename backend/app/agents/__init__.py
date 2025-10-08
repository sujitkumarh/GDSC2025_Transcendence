"""
Agent registry and imports for Transcendence multi-agent system.
Individual agents are now organized in separate files for better maintainability.
"""
from typing import Dict

# Import all agent classes from their individual files
from .base_agent import BaseAgent
from .router_agent import RouterAgent
from .career_agent import CareerAgent
from .learning_agent import LearningAgent
from .guidance_agent import GuidanceAgent
from .safety_agent import SafetyAgent


# Agent registry for easy access and dynamic loading
AGENT_REGISTRY = {
    "router_agent": RouterAgent,
    "career_agent": CareerAgent,
    "learning_agent": LearningAgent,
    "guidance_agent": GuidanceAgent,
    "safety_agent": SafetyAgent
}

def get_agent(agent_name: str) -> BaseAgent:
    """Get agent instance by name"""
    if agent_name not in AGENT_REGISTRY:
        raise ValueError(f"Unknown agent: {agent_name}. Available agents: {list(AGENT_REGISTRY.keys())}")
    
    return AGENT_REGISTRY[agent_name]()

def list_available_agents() -> Dict[str, str]:
    """List all available agents with their descriptions"""
    agents_info = {}
    for name, agent_class in AGENT_REGISTRY.items():
        # Create temporary instance to get description
        temp_instance = agent_class()
        agents_info[name] = temp_instance.description
    return agents_info

# Export main classes and functions for easy importing
__all__ = [
    "BaseAgent",
    "RouterAgent", 
    "CareerAgent",
    "LearningAgent",
    "GuidanceAgent", 
    "SafetyAgent",
    "AGENT_REGISTRY",
    "get_agent",
    "list_available_agents"
]