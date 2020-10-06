import sys, os, uuid, string, time, json, random, asyncio
import http.client as httplib

import logging

# opencensus base + azure extensions
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler, AzureEventHandler
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer
from opencensus.trace import config_integration

import config

# make sure traces have proper trace and span id set
config_integration.trace_integrations(['logging', 'httplib'])

tracer = Tracer( exporter=AzureExporter(connection_string=config.AI_CONNECTION_STR), sampler=AlwaysOnSampler())

logger = logging.getLogger(__name__)
# AI: this will send the events to trace
logger.addHandler(AzureLogHandler(connection_string=config.AI_CONNECTION_STR))
# AI: this will send the events to customEvents
logger.addHandler(AzureEventHandler(connection_string=config.AI_CONNECTION_STR))

logging.root.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

with tracer.span(name='HTTP Call'):
    logger.info('Before the call')

    conn = httplib.HTTPConnection("www.python.org")
    conn.request("GET", "http://www.python.org", "", {})
    response = conn.getresponse()
    conn.close()

    logger.info('After the call')
