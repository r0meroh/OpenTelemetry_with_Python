import time
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import (
    BatchSpanProcessor,
    ConsoleSpanExporter,
)
from opentelemetry.sdk.resources import Resource
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# Resource setup to specify service information
myResourceConfig = Resource(attributes={
    "service.name": "addition_service",
    "originated_from": "hugos_machine",
    "Cluster_Name": "Test_Cluster",
    "Environment": "Development"
})


# OTEL Tracing setup
provider = TracerProvider(resource=myResourceConfig)

COLLECTOR_ENDPOINT = "127.0.0.1"
COLLECTOR_GPRC_PORT = 6004

processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=f"http://{COLLECTOR_ENDPOINT}:{COLLECTOR_GPRC_PORT}"))
provider.add_span_processor(processor)

# set the global tracer provider
trace.set_tracer_provider(provider)

# create a tracer from the global tracer provider
myTracer = trace.get_tracer("myTracer")

# simple python definition of a function that adds two numbers
@myTracer.start_as_current_span("add_numbers_span")
def add_numbers(first, second) -> None:
    # add span status
    current_span = trace.get_current_span()
    current_span.set_status(trace.StatusCode.OK)
    # add span attributes
    current_span.set_attributes(attributes={
        "first_number": first,
        "second_number": second
    })

    # add a sleep function to simulate a delay in a span
    # the code below affects the span duration and can be visible in start_time and end_time
    time.sleep(2)
    current_span.add_event(
        name="sleeping for 2 seconds",
        attributes={
            "duration": 2,
            "additional_message": "complete"
            },
        # timestamp in nanoseconds or else OTEL exporter fails (expects integer)
        timestamp=int(time.time() * 1e9))
    

    return first + second

if __name__ == "__main__":
    result = add_numbers(3, 5)
    print(f"The sum of 3 and 5 is: {result}")   