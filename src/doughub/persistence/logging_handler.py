"""Database logging handler for persistent log storage."""

import logging
from datetime import datetime

from sqlalchemy.orm import Session

from doughub.models import Log


class DatabaseLogHandler(logging.Handler):
    """Logging handler that persists log records to the database.

    This handler writes log records to the Log table for persistent storage
    and analysis.
    """

    def __init__(self, session: Session, level: int = logging.NOTSET) -> None:
        """Initialize the database log handler.

        Args:
            session: SQLAlchemy session for database operations.
            level: Minimum logging level to persist.
        """
        super().__init__(level)
        self.session = session

    def emit(self, record: logging.LogRecord) -> None:
        """Persist a log record to the database.

        Args:
            record: The log record to persist.
        """
        try:
            log_entry = Log(
                level=record.levelname,
                logger_name=record.name,
                message=self.format(record),
                timestamp=datetime.fromtimestamp(record.created),
            )
            self.session.add(log_entry)
            self.session.commit()
        except Exception:
            # Avoid recursive errors when logging fails
            self.handleError(record)
