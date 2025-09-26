# AI‑Driven Workflow System

This project implements an example **AI‑driven workflow system** that scrapes online sources for remote job listings, stores them in a database, schedules recurring tasks and optionally processes them with a language‑model agent.  The system uses Python, SQLAlchemy for persistence, APScheduler for scheduling, and LangChain for AI integration.

## Prerequisites

* Python 3.9 or newer.
* Internet access to fetch remote job listings.
* Optional: an OpenAI API key if you wish to enable the AI agent features.

## Setup

1. Create a virtual environment and install dependencies:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```

2. If you plan to use the AI agent to summarise tasks, set the `OPENAI_API_KEY` environment variable or create a `.env` file in the project root with the following content:

   ```ini
   OPENAI_API_KEY=your_openai_api_key_here
   ```

## Running the system

Execute the following command from the root of the repository to start the scheduler and begin scraping and processing tasks:

```bash
python main.py
```

The default configuration will:

* Scrape the **Work at Home Woman** article on no‑interview jobs once every 24 hours.
* Scrape the **Self‑Made Success** article on no‑interview jobs once every 24 hours.
* Process any unprocessed tasks hourly.  When an OpenAI key is configured, the processor will summarise each task using a language model; otherwise, it will produce a simple uppercase summary.
* Scan configured local directories for `.txt` and `.csv` files once every 24 hours.  Newly discovered files are stored in the database.
* Preprocess and index unprocessed local files daily.  The raw and cleaned text are stored in the database for future analysis.

### Starting the administrative dashboard

In addition to the background scheduler, the project includes a simple yet stylish web dashboard for monitoring process flows and approving AI‑generated strategies.  To launch the dashboard, run:

```bash
python web.py
```

Then open <http://localhost:5000> in your browser.  The dashboard displays key metrics (tasks, local files, results), lists the highest priority unprocessed tasks and shows recent summaries and recommendations.  You can approve or revoke recommendations directly from the interface.  Approved results may inform future ranking and automation decisions.

## Folder structure

```
codebase/
├── config.py          # User preferences and job ranking logic
├── agent.py           # Optional AI agent integration
├── main.py            # Entry point; sets up scheduler and jobs
├── models.py          # SQLAlchemy ORM models
├── requirements.txt   # Python dependencies
├── scraper.py         # Functions for scraping job data
├── scheduler_setup.py # Scheduler and job store configuration
└── README.md          # This file
```

## Customisation

* To modify scraping sources, edit the `scrape_jobs` function in **scraper.py** and update the `SCRAPE_URLS` list.  Each entry should be a function that returns a list of dictionaries describing jobs.
* To change the scheduling intervals, edit the job definitions in **main.py**.  APScheduler supports interval, date and cron triggers.
* To extend the AI agent, implement additional tools or use other models within **agent.py**.
* To prioritise certain job categories, modify the `PREFERRED_KEYWORDS` list in **config.py**.  Jobs containing these keywords in their title or company name receive a higher score.  The top three tasks are logged after each scrape and the agent adjusts its recommendation based on the score.

* To analyse local files, populate the `LOCAL_DIRECTORIES` list in **config.py** with paths to folders containing `.txt` or `.csv` files.  When enabled, the system will discover new files in these directories, preprocess their contents (lowercasing, punctuation removal and stop‑word filtering) and store both raw and processed text in the database.

## Database migrations

The `WorkflowTask` model now includes a `score` column used for ranking.  If you previously ran an earlier version of this project, delete the existing `tasks.db` file or run a migration tool before using the updated code.

## Disclaimer

This project is provided for educational purposes.  Always respect website terms of service when scraping and ensure that automated job applications comply with platform rules and relevant laws.