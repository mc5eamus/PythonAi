import sys, os, uuid, string, time, json, random, asyncio

import logging

from azure.storage.queue import ( QueueClient, BinaryBase64EncodePolicy, BinaryBase64DecodePolicy)

# opencensus base + azure extensions
from opencensus.ext.azure.trace_exporter import AzureExporter
from opencensus.ext.azure.log_exporter import AzureLogHandler, AzureEventHandler
from opencensus.trace.samplers import AlwaysOnSampler
from opencensus.trace.tracer import Tracer
from opencensus.trace import config_integration

import config

# make sure traces have proper trace and span id set
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

queue_client = QueueClient.from_connection_string(config.STORAGE_CONNECTION_STR, config.QUEUE_NAME)

async def run():
   with tracer.span("send outer"):
      # inject one message in the queue
      message = u"Initial message"

      # our message will carry a json payload
      val = {"message": message, "properties": { "count": 1 }}

      # creating a span for sending
      with tracer.span("send init"):
         queue_client.send_message(json.dumps(val))
         logger.info("Init msg")
      
      while True:
         messages = queue_client.receive_messages()
         for msg in messages:
            print("Batch dequeue message: " + msg.content)
            queue_client.delete_message(msg)
            
            m = json.loads(msg.content)
            # increment the message sequence num
            msgId = m['properties']['count'] + 1
            m["message"] = "next in queue: {}".format(msgId)
            m["properties"]["count"] = msgId
            # a new span for sending subsequent message
            if True:
               with tracer.span("send subsequent") :
                  time.sleep(2)
                  logger.info("subsequent message: {}".format(m["message"]))
                  queue_client.send_message(json.dumps(m))

def main():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())

if __name__ == "__main__":
    main()
