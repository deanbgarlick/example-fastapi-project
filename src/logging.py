from typing import Any, Callable, TypeVar, ParamSpec
import functools
import logging
import asyncio

P = ParamSpec('P')
T = TypeVar('T')

def configure_logging(
    level: int = logging.INFO,
    format: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    date_format: str = "%Y-%m-%d %H:%M:%S",
) -> None:
    """
    Configure basic logging with reasonable defaults.
    
    Args:
        level: The logging level (default: logging.INFO)
        format: The log message format
        date_format: The date/time format for log messages
    """
    logging.basicConfig(
        level=level,
        format=format,
        datefmt=date_format,
    )

def with_logging(logger: logging.Logger) -> Callable[[Callable[P, T]], Callable[P, T]]:
    def decorator(func: Callable[P, T]) -> Callable[P, T]:
        if asyncio.iscoroutinefunction(func):
            @functools.wraps(func)
            async def async_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                logger.info(f"Calling {func.__name__}")
                value = await func(*args, **kwargs)  # type: ignore
                logger.info(f"Finished calling {func.__name__}")
                return value
            return async_wrapper  # type: ignore
        else:
            @functools.wraps(func)
            def sync_wrapper(*args: P.args, **kwargs: P.kwargs) -> T:
                logger.info(f"Calling {func.__name__}")
                value = func(*args, **kwargs)
                logger.info(f"Finished calling {func.__name__}")
                return value
            return sync_wrapper
    return decorator

# Create a default logger for the application
default_logger = logging.getLogger(__name__)

# Create a decorator using the default logger
with_default_logging = with_logging(default_logger)
