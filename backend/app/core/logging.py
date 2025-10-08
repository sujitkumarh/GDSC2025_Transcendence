"""
Logging configuration for Transcendence.
Provides structured logging with loguru.
"""
import sys
from pathlib import Path
from loguru import logger
from .config import settings


def setup_logging():
    """Configure loguru logging for the application"""
    
    # Remove default handler
    logger.remove()
    
    # Console logging with colors
    logger.add(
        sys.stdout,
        level=settings.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        colorize=True,
        backtrace=settings.DEBUG,
        diagnose=settings.DEBUG
    )
    
    # File logging (if not in mock mode)
    if not settings.MOCK_MODE or settings.is_production():
        log_dir = Path("logs")
        log_dir.mkdir(exist_ok=True)
        
        # Application logs
        logger.add(
            log_dir / "transcendence.log",
            level="INFO",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="10 MB",
            retention="30 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
        
        # Error logs
        logger.add(
            log_dir / "errors.log",
            level="ERROR",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
            rotation="5 MB",
            retention="60 days",
            compression="zip",
            backtrace=True,
            diagnose=True
        )
    
    # Configure specific loggers
    logger.configure(
        handlers=[
            {
                "sink": sys.stdout,
                "level": settings.LOG_LEVEL,
                "format": "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
                         "<level>{level: <8}</level> | "
                         "<cyan>{extra[module]}</cyan> | "
                         "<level>{message}</level>"
            }
        ]
    )


def get_logger(name: str):
    """Get a logger instance for a specific module"""
    return logger.bind(module=name)


# Pre-configured loggers
agent_logger = get_logger("agent")
api_logger = get_logger("api")
service_logger = get_logger("service")
analytics_logger = get_logger("analytics")