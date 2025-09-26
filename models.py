"""
Database models for the AutonomaX workflow system.

This module defines SQLAlchemy ORM classes for representing
workflow tasks and results.  The ``TaskResult`` model no longer
contains an ``approved`` column to ensure compatibility with legacy
SQLite databases that pre‐date the addition of an approval flag.

You can extend these models as you add new features (for example,
adding pricing fields or metadata for Shopify listings).  To avoid
breaking existing databases, consider writing migration scripts or
using a dedicated migration tool such as Alembic when adding new
columns.
"""

from datetime import datetime
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

Base = declarative_base()


class WorkflowTask(Base):
    """Represents a unit of work discovered by the scraper."""

    __tablename__ = "workflow_tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String)
    company = Column(String)
    link = Column(String)
    processed = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    requires_interview = Column(Boolean, default=False)


class TaskResult(Base):
    """Stores the result of processing a task."""

    __tablename__ = "task_results"

    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer)
    summary = Column(Text)
    recommendation = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)


def init_db(db_url: str = "sqlite:///tasks.db") -> sessionmaker:
    """Initialise the database and return a session factory.

    If the database file does not exist it will be created on the
    first run.  New tables will be created automatically if they
    don’t already exist.

    Args:
        db_url: SQLAlchemy database URL.  Defaults to an SQLite file
            named ``tasks.db`` in the current working directory.

    Returns:
        A SQLAlchemy ``sessionmaker`` bound to the engine.
    """
    engine = create_engine(db_url, echo=False)
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)