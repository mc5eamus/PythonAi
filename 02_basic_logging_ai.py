import logging
import random

from opencensus.trace import config_integration
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer

from opencensus.stats import aggregation as aggregation_module
from opencensus.stats import measure as measure_module
from opencensus.stats import stats as stats_module
from opencensus.stats import view as view_module
from opencensus.tags import tag_map as tag_map_module
from opencensus.tags import tag_value as tag_value_module

# Azure Applicatin Insights specific exporters
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler, AzureEventHandler
from opencensus.ext.azure import metrics_exporter

import config

# make sure traces have proper trace and span id set
config_integration.trace_integrations(['logging'])

# AI: tracer with AzureExporter configured
tracer = Tracer(exporter=AzureExporter(connection_string=config.AI_CONNECTION_STR),sampler=AlwaysOnSampler())

logging.root.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO)

logger = logging.getLogger(__name__)
# AI: this will send the events to trace
logger.addHandler(AzureLogHandler(connection_string=config.AI_CONNECTION_STR))
# AI: this will send the events to customEvents
logger.addHandler(AzureEventHandler(connection_string=config.AI_CONNECTION_STR))


stats = stats_module.stats
view_manager = stats.view_manager
stats_recorder = stats.stats_recorder

CARROTS_MEASURE = measure_module.MeasureInt("carrots",
                                            "number of carrots",
                                            "carrots")
CARROTS_VIEW = view_module.View("carrots_view",
                                "number of carrots",
                                [],
                                CARROTS_MEASURE,
                                aggregation_module.SumAggregation())

# AI: registing the metrics exporter with the view manager
view_manager.register_exporter(metrics_exporter.new_metrics_exporter(connection_string=config.AI_CONNECTION_STR))

view_manager.register_view(CARROTS_VIEW)

with tracer.span(name='hello world'):
    logger.warning('Before the inner span')
    with tracer.span(name='hello') as innerSpan:
        innerSpan.add_annotation("Some additional data here", textkey="textkey val", boolkey=False, intkex=31415926)
        logger.warning('In the inner span')
        logger.critical('error')
        try:
            result = 1 / 0  # generate a ZeroDivisionError
        except Exception:
            logger.exception('Captured an exception.', extra={'custom_dimensions': {'key_1': 'value_1', 'key_2': 'value_2'}})
    
    logger.warning('After the inner span')

    mmap = stats_recorder.new_measurement_map()
    tmap = tag_map_module.TagMap()
    tmap.insert("version", tag_value_module.TagValue("1.2.30"))
    mmap.measure_int_put(CARROTS_MEASURE, 10+random.randrange(10))
    mmap.record(tmap)