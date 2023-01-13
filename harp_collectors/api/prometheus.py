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
    receiver: str
    status: str
    alerts: list
    groupLabels: dict
    commonLabels: dict
    commonAnnotations: dict
    externalURL: str
    version: str
    groupKey: str


@router.post('/monitoring-system/prometheus')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Prometheus alerts
    """

    data = row_data.dict()
    try:
        # log.info(msg=f'Receive Prometheus data: {data}')

        data['integration_key'] = integration_key
        data['procedure_id'] = environment_id
        data['studio_id'] = scenario_id

        data['event_id'] = None

        event = ReceiveEvent(content=data, ms='prometheus')
        result = event.processor()

        return {'result': result}
    except KeyError as err:
        log.warning(
            msg=f"Can`t process event from Prometheus.\nERROR: {err}\nStack: {traceback.format_exc()}\nMessage: {data}"
        )

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
    except Exception as err:
        log.error(
            msg=f"Can`t process event from Prometheus.\nERROR: {err}\nStack: {traceback.format_exc()}\nMessage: {data}"
        )

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
