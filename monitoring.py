import logging
import sentry_sdk
from sentry_sdk.integrations.logging import LoggingIntegration

# Initialize Sentry SDK for monitoring
sentry_sdk.init(
    dsn="YOUR_SENTRY_DSN",  # Replace with your Sentry DSN
    integrations=[LoggingIntegration(
        level=logging.ERROR,  # Capture error and above
        event_level=logging.ERROR  # Send errors as events
    )]
)

# Configure logging for monitoring
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.FileHandler("app.log"),
                        logging.StreamHandler()
                    ])

def log_critical_error(message):
    """Log a critical error and send it to Sentry."""
    logging.critical(message)
    sentry_sdk.capture_message(message)

def log_warning(message):
    """Log a warning message."""
    logging.warning(message)

def log_info(message):
    """Log an informational message."""
    logging.info(message)

def log_exception(exc):
    """Log an exception and send it to Sentry."""
    logging.error("An error occurred", exc_info=exc)
    sentry_sdk.capture_exception(exc)

# Example of usage
if __name__ == "__main__":
    try:
        # Simulate an operation that could fail
        raise ValueError("Simulated error for demonstration.")
    except Exception as e:
        log_exception(e)
