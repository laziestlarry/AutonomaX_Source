"""
Flask dashboard for monitoring workflow tasks and results.

This simple web application provides a basic overview of the system’s
state.  It displays the total number of tasks, the number of
processed tasks and the number of results.  If the ``TaskResult``
model has an ``approved`` attribute, the dashboard will also show
counts of approved and pending results.  Otherwise all results are
treated as pending.

The dashboard is intentionally minimal.  You can extend it to
include additional metrics (e.g. Shopify product counts, market
research insights, lead generation status) or allow administrative
actions (e.g. approving recommendations, triggering scrapes).
"""

from flask import Flask, render_template_string
from sqlalchemy import func
from sqlalchemy.exc import InvalidRequestError
from sqlalchemy.orm import sessionmaker

from models import init_db, WorkflowTask, TaskResult

app = Flask(__name__)
SessionFactory: sessionmaker | None = None


TEMPLATE = """
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <title>AutonomaX Dashboard</title>
  <style>
    body { font-family: Arial, sans-serif; margin: 2em; }
    h1 { color: #333; }
    .metrics { display: flex; gap: 2em; }
    .metric { border: 1px solid #eee; padding: 1em; border-radius: 4px; }
    .metric h2 { margin-top: 0; }
  </style>
</head>
<body>
  <h1>AutonomaX System Dashboard</h1>
  <div class="metrics">
    <div class="metric">
      <h2>Total Tasks</h2>
      <p>{{ total_tasks }}</p>
    </div>
    <div class="metric">
      <h2>Processed Tasks</h2>
      <p>{{ processed_tasks }}</p>
    </div>
    <div class="metric">
      <h2>Results</h2>
      <p>{{ total_results }}</p>
    </div>
    {% if show_approved %}
    <div class="metric">
      <h2>Approved Results</h2>
      <p>{{ approved_results }}</p>
    </div>
    <div class="metric">
      <h2>Pending Results</h2>
      <p>{{ pending_results }}</p>
    </div>
    {% endif %}
  </div>
</body>
</html>
"""


@app.route("/")
def dashboard():
    """Render a basic dashboard view of the system state."""
    global SessionFactory
    if SessionFactory is None:
        SessionFactory = init_db()
    session = SessionFactory()
    total_tasks = session.query(WorkflowTask).count()
    processed_tasks = session.query(WorkflowTask).filter_by(processed=True).count()
    total_results = session.query(TaskResult).count()
    show_approved = False
    approved_results = 0
    pending_results = total_results
    # Check for approved attribute on TaskResult
    if hasattr(TaskResult, "approved"):
        show_approved = True
        try:
            approved_results = session.query(TaskResult).filter_by(approved=True).count()
            pending_results = session.query(TaskResult).filter_by(approved=False).count()
        except InvalidRequestError:
            # Catch cases where the column is missing from the DB
            approved_results = 0
            pending_results = total_results
    session.close()
    return render_template_string(
        TEMPLATE,
        total_tasks=total_tasks,
        processed_tasks=processed_tasks,
        total_results=total_results,
        show_approved=show_approved,
        approved_results=approved_results,
        pending_results=pending_results,
    )


# New comprehensive BI dashboard with charts and analytics
@app.route("/dashboard")
def full_dashboard():
    """Render a comprehensive dashboard with charts and analytics."""
    global SessionFactory
    if SessionFactory is None:
        SessionFactory = init_db()
    session = SessionFactory()
    # Metrics
    total_tasks = session.query(WorkflowTask).count()
    processed_tasks = session.query(WorkflowTask).filter_by(processed=True).count()
    total_results = session.query(TaskResult).count()
    # Tasks by company
    tasks_by_company = (
        session.query(WorkflowTask.company, func.count())
        .group_by(WorkflowTask.company)
        .all()
    )
    company_labels = [c for c, _ in tasks_by_company]
    company_counts = [count for _, count in tasks_by_company]
    # Tasks over time
    tasks_by_date = (
        session.query(func.date(WorkflowTask.created_at), func.count())
        .group_by(func.date(WorkflowTask.created_at))
        .all()
    )
    date_labels = [str(date) for date, _ in tasks_by_date]
    date_counts = [count for _, count in tasks_by_date]
    # Pending tasks
    unprocessed_count = total_tasks - processed_tasks
    session.close()
    # Chart.js in template
    dashboard_html = """
    <!doctype html>
    <html lang="en">
    <head>
        <meta charset="utf-8">
        <title>BI Dashboard</title>
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            body { font-family: Arial, sans-serif; margin: 2em; }
            h1 { color: #333; }
            .chart-container { width: 600px; height: 300px; margin-bottom: 2em; }
        </style>
    </head>
    <body>
        <h1>AutonomaX BI Dashboard</h1>
        <p>Total Tasks: {{ total_tasks }} | Processed Tasks: {{ processed_tasks }} | Pending: {{ pending }}</p>
        <div class="chart-container">
            <canvas id="companyChart"></canvas>
        </div>
        <div class="chart-container">
            <canvas id="dateChart"></canvas>
        </div>
        <script>
            const companyLabels = {{ company_labels|tojson }};
            const companyCounts = {{ company_counts|tojson }};
            const dateLabels = {{ date_labels|tojson }};
            const dateCounts = {{ date_counts|tojson }};
            const companyCtx = document.getElementById('companyChart').getContext('2d');
            const dateCtx = document.getElementById('dateChart').getContext('2d');
            new Chart(companyCtx, {
                type: 'bar',
                data: {
                    labels: companyLabels,
                    datasets: [{
                        label: 'Tasks by Company',
                        data: companyCounts,
                        backgroundColor: 'rgba(54, 162, 235, 0.5)',
                        borderColor: 'rgba(54, 162, 235, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
            new Chart(dateCtx, {
                type: 'line',
                data: {
                    labels: dateLabels,
                    datasets: [{
                        label: 'Tasks Over Time',
                        data: dateCounts,
                        backgroundColor: 'rgba(255, 99, 132, 0.5)',
                        borderColor: 'rgba(255, 99, 132, 1)',
                        borderWidth: 1
                    }]
                },
                options: {
                    scales: {
                        y: { beginAtZero: true }
                    }
                }
            });
        </script>
    </body>
    </html>
    """
    return render_template_string(
        dashboard_html,
        total_tasks=total_tasks,
        processed_tasks=processed_tasks,
        pending=unprocessed_count,
        company_labels=company_labels,
        company_counts=company_counts,
        date_labels=date_labels,
        date_counts=date_counts
    )


if __name__ == "__main__":
    app.run(debug=True)