"""
Hierarchical agent orchestrator for the AutonomaX system.

This module defines a simple Commander agent that delegates work
to specialised subagents.  The architecture is inspired by the
Hierarchical Autonomous Agent Swarm (HAAS) paradigm.  Each
subagent has a ``perform`` method that executes its duties using
shared database sessions.

You can extend this framework by adding more agents, such as a
``ShopifyAgent`` for updating listings, a ``MarketResearchAgent``
for running analyses or a ``LeadGenAgent`` for marketing tasks.
"""

import logging
from sqlalchemy.orm import Session

from models import WorkflowTask
from scraper import scrape_all_sources
from agent import process_task

logger = logging.getLogger(__name__)


class BaseAgent:
    """Base class for all agents."""

    def __init__(self, name: str) -> None:
        self.name = name

    def perform(self, session: Session) -> None:
        raise NotImplementedError


class ScraperAgent(BaseAgent):
    """Agent responsible for scraping new tasks."""

    def perform(self, session: Session) -> None:
        logger.info("%s: scraping sources", self.name)
        tasks = scrape_all_sources()
        added = 0
        for task in tasks:
            if not session.query(WorkflowTask).filter_by(link=task.link).first():
                session.add(task)
                added += 1
        session.commit()
        logger.info("%s: added %d new tasks", self.name, added)


class ProcessorAgent(BaseAgent):
    """Agent responsible for processing unprocessed tasks."""

    def perform(self, session: Session) -> None:
        logger.info("%s: processing unprocessed tasks", self.name)
        tasks = session.query(WorkflowTask).filter_by(processed=False).all()
        for task in tasks:
            process_task(task, session)
        logger.info("%s: processed %d tasks", self.name, len(tasks))


class Commander(BaseAgent):
    """Top‑level agent that orchestrates subagents."""

    def __init__(self, name: str, subagents: list[BaseAgent]) -> None:
        super().__init__(name)
        self.subagents = subagents

    def perform(self, session: Session) -> None:
        logger.info("%s starting operations", self.name)
        for agent in self.subagents:
            agent.perform(session)
        logger.info("%s completed a cycle", self.name)