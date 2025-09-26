"""Local file discovery and analysis utilities.

This module provides functions to scan directories on the local filesystem for
data files (currently `.txt` and `.csv`) and preprocess their contents into
cleaned tokens.  The results are stored in the database via the ORM models
defined in `models.py`.  Preprocessing is intentionally lightweight so that
analysis can run without external NLP dependencies.

Usage:
    from models import init_db
    Session = init_db()
    scan_local_files(Session())
    process_local_files(Session())

The functions are designed to be called by scheduled jobs in `main.py`.
"""

import logging
import os
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

import config
from models import LocalFile, DocumentContent
import spr

logger = logging.getLogger(__name__)


def _iter_files(directories: Iterable[str]) -> Iterable[Path]:
    """Yield Path objects for .txt and .csv files in the given directories."""
    for directory in directories:
        root = Path(directory).expanduser()
        if not root.exists() or not root.is_dir():
            logger.warning("Directory does not exist or is not a directory: %s", directory)
            continue
        for dirpath, _, filenames in os.walk(root):
            for name in filenames:
                if name.lower().endswith((".txt", ".csv")):
                    yield Path(dirpath) / name


def scan_local_files(session: Session) -> None:
    """Discover new files in configured directories and insert them into the DB.

    Creates a `LocalFile` entry for each unique file path that doesn't yet
    exist in the database.  Only basic metadata (path and size) is stored at
    this stage.  Errors reading file metadata are logged.
    """
    count_new = 0
    for file_path in _iter_files(config.LOCAL_DIRECTORIES):
        path_str = str(file_path)
        exists = session.query(LocalFile).filter_by(path=path_str).first()
        if exists:
            continue
        try:
            size = file_path.stat().st_size
        except Exception as e:
            logger.error("Failed to stat file %s: %s", path_str, e)
            continue
        local_file = LocalFile(path=path_str, size=size)
        session.add(local_file)
        count_new += 1
    session.commit()
    logger.info("Discovered %d new local files", count_new)


def _preprocess_text(text: str) -> str:
    """Basic text preprocessing: lowercase, remove punctuation, remove stopwords."""
    # Lowercase
    text = text.lower()
    # Replace punctuation with spaces
    for ch in ",.?!;:\"'()[]{}<>-_/\\":
        text = text.replace(ch, " ")
    # Split into tokens and remove stopwords
    tokens = [tok for tok in text.split() if tok not in config.STOPWORDS]
    return " ".join(tokens)


def process_local_files(session: Session) -> None:
    """Read and preprocess unprocessed local files.

    For each file recorded in `local_files` where `processed` is False, read
    the file contents (for `.txt` or `.csv`), store both raw and processed
    versions in `DocumentContent`, and mark the file as processed.  Skips
    files that cannot be read.
    """
    unprocessed = session.query(LocalFile).filter_by(processed=False).all()
    if not unprocessed:
        logger.info("No unprocessed local files")
        return
    logger.info("Processing %d local files", len(unprocessed))
    for local_file in unprocessed:
        path = Path(local_file.path)
        try:
            with path.open("r", encoding="utf-8", errors="ignore") as f:
                raw_text = f.read()
        except Exception as e:
            logger.error("Failed to read file %s: %s", local_file.path, e)
            # Mark as processed to avoid repeatedly failing
            local_file.processed = True
            continue
        processed_text = _preprocess_text(raw_text)
        # Generate a sparse priming representation from the raw text.  Use a
        # modest number of sentences to avoid blowing out the context
        # window.  This representation will be stored alongside the raw and
        # processed text for later retrieval.  Should the SPR generator
        # fail, fall back to an empty string.
        try:
            spr_text = spr.generate_spr(raw_text, max_sentences=5)
        except Exception as e:
            logger.error("Failed to generate SPR for file %s: %s", local_file.path, e)
            spr_text = ""
        doc = DocumentContent(
            file_id=local_file.id,
            raw_text=raw_text,
            processed_text=processed_text,
            spr_text=spr_text,
        )
        session.add(doc)
        local_file.processed = True
    session.commit()