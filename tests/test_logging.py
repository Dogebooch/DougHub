"""Tests for persistent logging functionality."""

import logging

from sqlalchemy import select
from sqlalchemy.orm import Session

from doughub.models import Log
from doughub.persistence.logging_handler import DatabaseLogHandler


def test_database_log_handler_persists_logs(test_db_session: Session) -> None:
    """Test that log messages are persisted to the database."""
    # Create logger with database handler
    logger = logging.getLogger("test_logger")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = DatabaseLogHandler(test_db_session, level=logging.INFO)
    logger.addHandler(handler)

    # Emit log messages
    logger.info("Test info message")
    logger.warning("Test warning message")
    logger.error("Test error message")

    # Query the database
    stmt = select(Log).order_by(Log.log_id)
    logs = list(test_db_session.execute(stmt).scalars().all())

    assert len(logs) == 3

    assert logs[0].level == "INFO"
    assert logs[0].logger_name == "test_logger"
    assert "Test info message" in logs[0].message

    assert logs[1].level == "WARNING"
    assert "Test warning message" in logs[1].message

    assert logs[2].level == "ERROR"
    assert "Test error message" in logs[2].message


def test_database_log_handler_respects_level_threshold(test_db_session: Session) -> None:
    """Test that log messages below threshold are not persisted."""
    logger = logging.getLogger("test_logger_threshold")
    logger.setLevel(logging.DEBUG)
    logger.handlers.clear()

    # Set handler to only log WARNING and above
    handler = DatabaseLogHandler(test_db_session, level=logging.WARNING)
    logger.addHandler(handler)

    # Emit messages at different levels
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")

    # Query the database
    stmt = select(Log).where(Log.logger_name == "test_logger_threshold")
    logs = list(test_db_session.execute(stmt).scalars().all())

    # Only WARNING and ERROR should be persisted
    assert len(logs) == 2
    assert logs[0].level == "WARNING"
    assert logs[1].level == "ERROR"


def test_log_model_attributes(test_db_session: Session) -> None:
    """Test that Log model stores all required attributes."""
    logger = logging.getLogger("test_logger_attrs")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = DatabaseLogHandler(test_db_session)
    logger.addHandler(handler)

    logger.info("Test message")

    stmt = select(Log).where(Log.logger_name == "test_logger_attrs")
    log = test_db_session.execute(stmt).scalar_one()

    assert log.log_id is not None
    assert log.level == "INFO"
    assert log.logger_name == "test_logger_attrs"
    assert log.message == "Test message"
    assert log.timestamp is not None


def test_database_log_handler_with_formatter(test_db_session: Session) -> None:
    """Test that custom formatters work with the handler."""
    logger = logging.getLogger("test_logger_format")
    logger.setLevel(logging.INFO)
    logger.handlers.clear()

    handler = DatabaseLogHandler(test_db_session)
    formatter = logging.Formatter("%(levelname)s - %(name)s - %(message)s")
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    logger.info("Formatted message")

    stmt = select(Log).where(Log.logger_name == "test_logger_format")
    log = test_db_session.execute(stmt).scalar_one()

    assert "INFO - test_logger_format - Formatted message" == log.message
