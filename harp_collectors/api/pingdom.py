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
    version: int
    check_id: int
    check_name: str
    check_type: str
    check_params: dict
    tags: list
    importance_level: str
    custom_message: str
    previous_state: str
    current_state: str
    state_changed_timestamp: int
    state_changed_utc_time: str
    long_description: str
    description: str
    first_probe: dict
    second_probe: dict


@router.post('/monitoring-system/pingdom')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Pingdom alerts
    """

    data = row_data.dict()
    try:
        data['integration_key'] = integration_key
        data['environment_id'] = environment_id
        data['scenario_id'] = scenario_id

        event = ReceiveEvent(content=data, ms='pingdom')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from Pingdom.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
