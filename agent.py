"""
Core agent utilities and summarisation routines.

This module provides functions to process tasks and generate
summaries.  It attempts to call OpenAI’s API if configured.  If the
API call fails (e.g. due to quota or credentials), it falls back to
using a local model via the Ollama API.  In the event that both
external and local summarisation fails, a simple truncation summary
is returned.

This design makes it easy to plug in additional summarisation
engines in the future (e.g. other hosted LLMs or your own fine‑
tuned models).
"""

from typing import Optional
import logging
import requests

from sqlalchemy.orm import Session

from models import WorkflowTask, TaskResult
import config

logger = logging.getLogger(__name__)


def _openai_summary(prompt: str) -> Optional[str]:
    """Attempt to summarise a prompt using OpenAI.

    Returns the summary string on success, otherwise ``None`` if
    there is an error or the API key is not set.
    """
    if not config.OPENAI_API_KEY:
        return None
    try:
        import openai  # imported lazily to avoid mandatory dependency
        client = openai.OpenAI(api_key=config.OPENAI_API_KEY)
        response = client.completions.create(
            model="gpt-3.5-turbo-instruct",
            prompt=prompt,
            max_tokens=80,
        )
        return response.choices[0].text.strip()
    except Exception as e:  # broad catch for demonstration
        logger.error("OpenAI summary failed: %s", e)
        return None


def _ollama_summary(prompt: str) -> Optional[str]:
    """Attempt to summarise a prompt using a local Ollama model.

    This assumes that an Ollama service is running locally on
    ``http://localhost:11434`` and exposes the `/generate` endpoint as
    described in the Ollama documentation.  On failure, returns
    ``None``.
    """
    url = "http://localhost:11434/api/generate"
    try:
        res = requests.post(
            url,
            json={"model": config.OLLAMA_MODEL_NAME, "prompt": prompt, "options": {"n_predict": 80}},
            timeout=30,
        )
        res.raise_for_status()
        data = res.json()
        return data.get("response", "").strip()
    except Exception as e:
        logger.error("Ollama summary failed: %s", e)
        return None


def generate_summary(text: str) -> str:
    """Generate a short summary of the given text.

    The function tries OpenAI first, then falls back to Ollama.
    If both fail, it returns the first 50 words of the text.
    """
    prompt = f"Summarise the following text:\n\n{text}"
    summary = _openai_summary(prompt)
    if summary:
        return summary
    summary = _ollama_summary(prompt)
    if summary:
        return summary
    # naive fallback: truncate
    return " ".join(text.split()[:50]) + ("..." if len(text.split()) > 50 else "")


def process_task(task: WorkflowTask, session: Session) -> None:
    """Process a single workflow task.

    This function generates a summary and recommendation for the task
    using the configured language model and saves a ``TaskResult`` in
    the database.  It sets the task as processed to prevent duplicate
    processing.
    """
    # For demonstration, we'll summarise the title and company.
    combined = f"{task.title} at {task.company}"
    summary = generate_summary(combined)
    recommendation = f"Consider applying to '{task.title}' at {task.company} if it fits your skills."
    result = TaskResult(
        task_id=task.id,
        summary=summary,
        recommendation=recommendation,
    )
    session.add(result)
    task.processed = True
    session.commit()