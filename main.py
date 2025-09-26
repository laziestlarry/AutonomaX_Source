"""
Entry point to run the AutonomaX workflow scheduler.

This script initialises the database, scrapes new tasks from
configured sources, processes unprocessed tasks using the agent
summarisation pipeline and prints a summary of actions taken.  It
provides a simple loop for demonstration.  For production use,
consider using APScheduler or another scheduler to run these steps
periodically.
"""

import logging
from time import sleep

from models import init_db, WorkflowTask
from scraper import scrape_all_sources
from agent import process_task

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("main")


def main() -> None:
    logger.info("Starting AutonomaX scheduler...")
    SessionFactory = init_db()
    session = SessionFactory()
    # Step 1: scrape new tasks
    new_tasks = scrape_all_sources()
    added = 0
    for task in new_tasks:
        # avoid duplicates by link
        if not session.query(WorkflowTask).filter_by(link=task.link).first():
            session.add(task)
            added += 1
    session.commit()
    logger.info("Added %d new tasks", added)
    # Step 2: process unprocessed tasks
    unprocessed = session.query(WorkflowTask).filter_by(processed=False).all()
    for task in unprocessed:
        process_task(task, session)
        logger.info("Processed task %s", task.title)
    session.close()
    logger.info("Scheduler run complete")


if __name__ == "__main__":
    while True:
        main()
        # sleep between cycles (e.g. run hourly)
        sleep(3600)