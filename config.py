"""
Configuration settings for the AutonomaX workflow system.

This file contains basic constants used throughout the application,
including scraping sources, preferred keywords for ranking and
directories to scan for local files.  Feel free to modify these
values to suit your particular business requirements.  New settings
for Shopify automation, market research and other verticals can be
added here as needed.
"""

import os

# Data directories for local file scanning (e.g. research notes,
# transcripts, product descriptions).  A list of paths on your
# server’s filesystem that the ``FileAnalyzerAgent`` will scan for
# new files.
LOCAL_DIRECTORIES = [
    os.path.join(os.getcwd(), "data"),
]

# Keywords that indicate a high‑value job posting.  When scraping
# external sites, tasks containing these words will be prioritised.
PREFERRED_KEYWORDS = ["remote", "no interview", "entry level", "flexible"]

# Stopwords for NLP preprocessing.  These are removed from
# documents before analysis to reduce noise.  You can add or remove
# terms to improve the quality of your summaries.
STOPWORDS = {
    "the",
    "a",
    "and",
    "to",
    "of",
    "in",
    "for",
}

# Shopify settings
SHOPIFY_STORE_DOMAIN = os.getenv("SHOPIFY_STORE_DOMAIN", "your-store.myshopify.com")
SHOPIFY_API_KEY = os.getenv("SHOPIFY_API_KEY")
SHOPIFY_API_PASSWORD = os.getenv("SHOPIFY_API_PASSWORD")

# OpenAI and local LLM settings.  The application will attempt to
# use OpenAI first and fall back to a local model (e.g. via the
# ``ollama`` API) if the OpenAI call fails or if no API key is
# configured.
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OLLAMA_MODEL_NAME = os.getenv("OLLAMA_MODEL_NAME", "llama3")