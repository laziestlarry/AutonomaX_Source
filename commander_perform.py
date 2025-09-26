"""
Run a single cycle of the Commander agent.

This script initialises the database, creates the Commander and
subagents, runs them once and exits.  It is useful for testing the
agent orchestration without starting the periodic scheduler.
"""

import logging

from models import init_db
from agents import Commander, ScraperAgent, ProcessorAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("commander_perform")


def main() -> None:
    SessionFactory = init_db()
    session = SessionFactory()
    commander = Commander(
        "Commander",
        subagents=[ScraperAgent("Scraper"), ProcessorAgent("Processor")],
    )
    commander.perform(session)
    session.close()


if __name__ == "__main__":
    main()