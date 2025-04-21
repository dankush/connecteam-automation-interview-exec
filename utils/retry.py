"""Retry mechanism for handling flaky interactions."""
import time
import logging
from typing import TypeVar, Callable, Any, Optional, Type, List, Union
from functools import wraps
import random

T = TypeVar('T')


def retry(
    exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
    tries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    jitter: float = 0.1,
    logger: Optional[logging.Logger] = None
) -> Callable[[Callable[..., T]], Callable[..., T]]:
    """
    Retry decorator with exponential backoff for handling flaky interactions.
    
    Args:
        exceptions: Exception or list of exceptions to catch and retry on
        tries: Maximum number of attempts
        delay: Initial delay between retries in seconds
        backoff: Backoff multiplier (e.g. value of 2 will double the delay each retry)
        jitter: Jitter factor to randomize delay (0 to 1.0)
        logger: Logger to use, if None, logging.getLogger() is used
    
    Returns:
        Decorated function with retry logic
    """
    if logger is None:
        logger = logging.getLogger()
    
    # Convert single exception to list
    if not isinstance(exceptions, list):
        exceptions = [exceptions]
    
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> T:
            mtries, mdelay = tries, delay
            last_exception = None
            
            # Try the function up to 'tries' times
            for attempt in range(1, mtries + 1):
                try:
                    return func(*args, **kwargs)
                except tuple(exceptions) as e:
                    last_exception = e
                    
                    # If this was the last attempt, re-raise the exception
                    if attempt == mtries:
                        logger.error(f"Function {func.__name__} failed after {mtries} attempts. Last error: {str(e)}")
                        raise
                    
                    # Calculate jittered delay
                    jitter_amount = random.uniform(-jitter, jitter) * mdelay
                    sleep_time = mdelay + jitter_amount
                    
                    # Log the retry
                    logger.warning(
                        f"Attempt {attempt}/{mtries} for {func.__name__} failed: {str(e)}. "
                        f"Retrying in {sleep_time:.2f} seconds..."
                    )
                    
                    # Sleep before next attempt
                    time.sleep(sleep_time)
                    
                    # Increase delay for next attempt
                    mdelay *= backoff
            
            # This should never happen, but just in case
            if last_exception:
                raise last_exception
            raise Exception(f"Retry decorator failed for unknown reasons in {func.__name__}")
        
        return wrapper
    
    return decorator


class RetryOnException:
    """Context manager for retrying a block of code on exception."""
    
    def __init__(
        self,
        exceptions: Union[Type[Exception], List[Type[Exception]]] = Exception,
        tries: int = 3,
        delay: float = 1.0,
        backoff: float = 2.0,
        jitter: float = 0.1,
        logger: Optional[logging.Logger] = None
    ):
        """Initialize with retry parameters."""
        self.exceptions = exceptions if isinstance(exceptions, list) else [exceptions]
        self.tries = tries
        self.delay = delay
        self.backoff = backoff
        self.jitter = jitter
        self.logger = logger or logging.getLogger()
    
    def __enter__(self) -> None:
        """Enter the context manager."""
        pass
    
    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any) -> bool:
        """
        Exit the context manager, handling exceptions as needed.
        
        Returns:
            True if exception was handled, False otherwise
        """
        if exc_type is None:
            return False
        
        # Check if the exception is one we should retry on
        if not any(issubclass(exc_type, exc_class) for exc_class in self.exceptions):
            return False
        
        # If we've used up all our retries, don't suppress the exception
        if self.tries <= 1:
            return False
        
        # Log the retry
        self.logger.warning(
            f"Operation failed with {exc_type.__name__}: {str(exc_val)}. "
            f"Will retry {self.tries - 1} more times."
        )
        
        # Calculate jittered delay
        jitter_amount = random.uniform(-self.jitter, self.jitter) * self.delay
        sleep_time = self.delay + jitter_amount
        
        # Sleep before returning
        time.sleep(sleep_time)
        
        # Update for next retry
        self.delay *= self.backoff
        self.tries -= 1
        
        # Suppress the exception to retry
        return True
