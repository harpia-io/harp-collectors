from logger.logging import service_logger
from harp_collectors.collectors import ReceiveEvent
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import harp_collectors.settings as settings
from typing import Optional, Union

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class MSBody(BaseModel):
    incident: dict
    version: str


@router.post('/monitoring-system/gcp')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None):
    """
    Handle GCP alerts
    """

    data = row_data.dict()
    try:
        data['integration_key'] = integration_key

        event = ReceiveEvent(content=data, ms='gcp')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from GCP.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
