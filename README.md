# Application Insights scenarios for Python

## Note
Make sure to update config.py with settings for 
* Application Insights Connection string
* Storage Account connection string and queue name (only required for 04_e2e_tracing.py)

## Scenarios
* 01_basic_logging - some basic OpenSensus instrumentation without Application Insights 
* 02_basic_logging_ai - same as the previous one with Application Insights configured
* 03_dependency_tracing - example for httplib dependency tracing on simple calls
* 04_e2e_tracing - tracing for storage queue messages being sent and received