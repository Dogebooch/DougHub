"""Custom logging utilities for DougHub.

Provides structured, contextual logging with extra fields and custom formatting.
"""

import logging
from typing import Any


class ContextualFormatter(logging.Formatter):
    """Custom formatter that includes extra contextual information.

    Extends the standard formatter to display extra context fields
    passed via the 'extra' parameter in logging calls.
    """

    def format(self, record: logging.LogRecord) -> str:
        """Format log record with contextual information.

        Args:
            record: The log record to format.

        Returns:
            Formatted log message string.
        """
        # Store original format
        original_format = self._style._fmt

        # Add extra context fields if present
        extra_parts = []
        for key, value in record.__dict__.items():
            # Skip built-in fields
            if key not in [
                "name", "msg", "args", "created", "filename", "funcName",
                "levelname", "levelno", "lineno", "module", "msecs",
                "message", "pathname", "process", "processName", "relativeCreated",
                "thread", "threadName", "exc_info", "exc_text", "stack_info",
                "taskName"
            ]:
                extra_parts.append(f"{key}={value}")

        # Add context to message if present
        if extra_parts:
            context_str = " | ".join(extra_parts)
            # Temporarily modify format to include context
            self._style._fmt = f"{original_format} [{context_str}]"

        result = super().format(record)

        # Restore original format
        self._style._fmt = original_format

        return result


class QtTextEditHandler(logging.Handler):
    """Logging handler that directs logs to a Qt TextEdit widget.

    Emits signals to update a TextEdit widget in a thread-safe manner.
    """

    def __init__(self) -> None:
        """Initialize the handler."""
        super().__init__()
        self.widget = None
        self.buffer: list[str] = []  # Buffer for logs before widget is set

    def set_widget(self, widget: Any) -> None:
        """Set the TextEdit widget to receive log messages.

        Args:
            widget: QTextEdit widget to display logs.
        """
        self.widget = widget
        # Flush buffer to widget
        if self.buffer:
            for msg in self.buffer:
                self._append_to_widget(msg)
            self.buffer.clear()

    def emit(self, record: logging.LogRecord) -> None:
        """Emit a log record to the widget.

        Args:
            record: The log record to emit.
        """
        try:
            msg = self.format(record)
            if self.widget:
                self._append_to_widget(msg)
            else:
                # Buffer until widget is available
                self.buffer.append(msg)
        except Exception:
            self.handleError(record)

    def _append_to_widget(self, msg: str) -> None:
        """Append message to widget in a thread-safe manner.

        Args:
            msg: The formatted message to append.
        """
        if self.widget:
            # Append directly - QTextEdit.append is thread-safe in Qt6
            self.widget.append(msg)


def setup_logging(level: int = logging.INFO) -> QtTextEditHandler:
    """Configure application-wide logging.

    Sets up structured logging with contextual formatting and
    returns a handler for the diagnostics view.

    Args:
        level: The logging level to use (default: INFO).

    Returns:
        QtTextEditHandler instance for the diagnostics view.
    """
    # Create formatter
    formatter = ContextualFormatter(
        fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # Configure root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(level)

    # Clear any existing handlers
    root_logger.handlers.clear()

    # Add console handler with contextual formatting
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)

    # Create and add Qt handler for diagnostics view
    qt_handler = QtTextEditHandler()
    qt_handler.setFormatter(formatter)
    root_logger.addHandler(qt_handler)

    # Configure third-party loggers to be less verbose
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)

    return qt_handler
