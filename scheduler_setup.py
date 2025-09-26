"""Scheduler configuration for the workflow system.

This module provides a helper to initialise an APScheduler instance with
persistent storage backed by SQLAlchemy.  Scheduled jobs defined using this
scheduler will survive application restarts, allowing for reliable long‑running
automation.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.jobstores.sqlalchemy import SQLAlchemyJobStore


def init_scheduler(db_url: str = "sqlite:///jobs.sqlite") -> BackgroundScheduler:
    """Create and start a background scheduler with a persistent job store.

    Args:
        db_url: SQLAlchemy database URL used for persisting job metadata.

    Returns:
        An initialised and started `BackgroundScheduler` instance.
    """
    jobstores = {
        'default': SQLAlchemyJobStore(url=db_url),
    }
    scheduler = BackgroundScheduler(jobstores=jobstores)
    scheduler.start()
    return scheduler