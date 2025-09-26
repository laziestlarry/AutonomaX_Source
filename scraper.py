"""
Web scraping utilities for the AutonomaX system.

This module contains functions to scrape job listings from various
sources and persist them as ``WorkflowTask`` objects.  It sets a
browser‑like User‑Agent header to reduce the likelihood of being
blocked.  The scraper is simplified for demonstration purposes.

If you extend the system to scrape product listings (e.g. Shopify
inventory) or other online content, you can add new functions here
and register them in the scheduler.
"""

import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

from models import WorkflowTask

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/117.0 Safari/537.36"
    )
}


def _scrape_work_at_home_woman() -> list[WorkflowTask]:
    """Scrape jobs from the Work at Home Woman site.

    Returns a list of ``WorkflowTask`` objects.  Any parsing
    exceptions are logged and the offending job is skipped.
    """
    url = "https://www.theworkathomewoman.com/work-at-home-jobs/"
    tasks: list[WorkflowTask] = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        # Assume each job is represented by an ``li`` tag with a link
        for li in soup.select("li a"):
            title = li.get_text(strip=True)
            link = urljoin(url, li["href"])
            tasks.append(
                WorkflowTask(
                    title=title,
                    company="Work at Home Woman",
                    link=link,
                    requires_interview=False,
                )
            )
    except Exception as e:
        logger.error("Failed to fetch Work at Home Woman jobs: %s", e)
    return tasks


def _scrape_self_made_success() -> list[WorkflowTask]:
    """Scrape jobs from the Self‑Made Success website.

    Due to occasional 403 errors, the function will attempt to
    gracefully handle forbidden responses and simply return an empty
    list.  Consider rotating proxies or using a headless browser
    library (e.g. Playwright) for more robust scraping.
    """
    url = (
        "https://selfmadesuccess.com/urgently-hiring-work-from-home-jobs-no-interview/"
    )
    tasks: list[WorkflowTask] = []
    try:
        res = requests.get(url, headers=HEADERS, timeout=30)
        if res.status_code == 403:
            logger.warning("Access forbidden when scraping Self‑Made Success; skipping.")
            return []
        res.raise_for_status()
        soup = BeautifulSoup(res.text, "html.parser")
        for li in soup.select("li a"):
            title = li.get_text(strip=True)
            link = urljoin(url, li["href"])
            tasks.append(
                WorkflowTask(
                    title=title,
                    company="Self‑Made Success",
                    link=link,
                    requires_interview=False,
                )
            )
    except Exception as e:
        logger.error("Failed to fetch Self‑Made Success jobs: %s", e)
    return tasks


def scrape_all_sources() -> list[WorkflowTask]:
    """Scrape all configured sources and return a combined list of tasks."""
    tasks = []
    tasks += _scrape_work_at_home_woman()
    tasks += _scrape_self_made_success()
    return tasks