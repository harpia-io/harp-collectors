from logger.logging import service_logger
from harp_collectors.collectors import ReceiveEvent
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import harp_collectors.settings as settings
from typing import Optional

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class MSBody(BaseModel):
    subject: str
    severity: str
    description: str
    investigationUrl: str
    startTime: str
    startTimeEpoch: str
    anomalyId: str
    mergedAnomalies: str
    timeScale: str
    type: str
    alerts: list


@router.post('/monitoring-system/anodot')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle API alerts
    """

    data = row_data.dict()

    try:
        data['environment_id'] = environment_id
        data['scenario_id'] = scenario_id
        data['integration_key'] = integration_key

        event = ReceiveEvent(content=data, ms='anodot')
        result = event.processor()

        return {'result': result}, 200
    except Exception as err:
        log.error(msg=f"Can`t process event from Anodot.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
