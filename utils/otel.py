
import os
from opentelemetry import trace, metrics
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter

# Note: Avoid importing instrumentation at module import time to prevent
# optional dependencies from breaking app startup when OTEL is disabled.

SERVICE_NAME = os.getenv("OTEL_SERVICE_NAME", "autonoma-x-ai")

def setup_otel(app=None):
    """Initialize OpenTelemetry exporters and optional framework instrumentation.

    Imports FastAPI and Requests instrumentors lazily so that missing optional
    packages do not crash the service on startup when OTEL is disabled.
    """
    resource = Resource.create({"service.name": SERVICE_NAME})
    tracer_provider = TracerProvider(resource=resource)
    processor = BatchSpanProcessor(
        OTLPSpanExporter(
            endpoint=os.getenv(
                "OTEL_EXPORTER_OTLP_ENDPOINT", "http://localhost:4318/v1/traces"
            )
        )
    )
    tracer_provider.add_span_processor(processor)
    trace.set_tracer_provider(tracer_provider)

    meter_provider = MeterProvider(resource=resource)
    metrics.set_meter_provider(meter_provider)

    # Best-effort instrumentation; ignore if optional deps missing
    if app:
        try:
            from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor

            FastAPIInstrumentor.instrument_app(app)
        except Exception:
            pass

    try:
        from opentelemetry.instrumentation.requests import RequestsInstrumentor

        RequestsInstrumentor().instrument()
    except Exception:
        pass
