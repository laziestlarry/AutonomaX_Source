
import os
from google.analytics.data_v1beta import BetaAnalyticsDataClient
from google.analytics.data_v1beta.types import DateRange, Metric, Dimension, RunReportRequest
def get_ga4_kpis():
    prop=os.getenv("GA4_PROPERTY_ID"); 
    if not prop: return {"error":"GA4_PROPERTY_ID not set"}
    try:
        client=BetaAnalyticsDataClient()
        req=RunReportRequest(property=f"properties/{prop}", dimensions=[Dimension(name="date")], metrics=[Metric(name="sessions"),Metric(name="totalUsers"),Metric(name="eventCount")], date_ranges=[DateRange(start_date="7daysAgo", end_date="today")])
        resp=client.run_report(req)
        rows=[{"date":r.dimension_values[0].value,"sessions":int(r.metric_values[0].value),"users":int(r.metric_values[1].value),"events":int(r.metric_values[2].value)} for r in resp.rows]
        return {"rows": rows}
    except Exception as e:
        return {"error": str(e)}
