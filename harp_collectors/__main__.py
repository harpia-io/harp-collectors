import harp_collectors.settings as settings
from fastapi import FastAPI, Request, status
from logger.logging import fastapi_logging
from logger.logging import service_logger
from harp_collectors.plugins.tracer import get_tracer
from prometheus_fastapi_instrumentator import Instrumentator
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from harp_collectors.api.api import router as api
from harp_collectors.api.health import router as health
from harp_collectors.api.anodot import router as anodot
from harp_collectors.api.appdynamics import router as appdynamics
from harp_collectors.api.atatus import router as atatus
from harp_collectors.api.cloudwatch import router as cloudwatch
from harp_collectors.api.crashlytics import router as crashlytics
from harp_collectors.api.dynatrace import router as dynatrace
from harp_collectors.api.email import router as email
from harp_collectors.api.gcp import router as gcp
from harp_collectors.api.grafana import router as grafana
from harp_collectors.api.icinga import router as icinga
from harp_collectors.api.nagios import router as nagios
from harp_collectors.api.newrelic import router as newrelic
from harp_collectors.api.pagerduty import router as pagerduty
from harp_collectors.api.pingdom import router as pingdom
from harp_collectors.api.prometheus import router as prometheus
from harp_collectors.api.prtg import router as prtg
from harp_collectors.api.zabbix import router as zabbix


log = service_logger()
fastapi_logging()
tracer = get_tracer()


app = FastAPI(
    openapi_url=f'{settings.URL_PREFIX}/openapi.json',
    docs_url=f'{settings.URL_PREFIX}/docs',
    redoc_url=f'{settings.URL_PREFIX}/redoc'
)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    log.error(
        msg=f"FastAPI: Failed to validate request\nURL: {request.method} - {request.url}\nBody: {exc.body}\nError: {exc.errors()}"
    )
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


FastAPIInstrumentor.instrument_app(app, tracer_provider=tracer)
Instrumentator().instrument(app).expose(app)
app.include_router(api)
app.include_router(health)
app.include_router(anodot)
app.include_router(appdynamics)
app.include_router(atatus)
app.include_router(cloudwatch)
app.include_router(crashlytics)
app.include_router(dynatrace)
app.include_router(email)
app.include_router(gcp)
app.include_router(grafana)
app.include_router(icinga)
app.include_router(nagios)
app.include_router(newrelic)
app.include_router(pagerduty)
app.include_router(pingdom)
app.include_router(prometheus)
app.include_router(prtg)
app.include_router(zabbix)
