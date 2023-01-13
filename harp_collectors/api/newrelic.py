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
    owner: str
    severity: str
    policy_url: str
    closed_violations_count: dict
    current_state: str
    policy_name: str
    incident_url: str
    condition_family_id: int
    incident_acknowledge_url: str
    targets: list
    version: str
    condition_id: int
    duration: int
    account_id: int
    incident_id: int
    event_type: str
    violation_chart_url: str
    account_name: str
    open_violations_count: dict
    details: str
    violation_callback_url: str
    condition_name: str
    timestamp: int


@router.post('/monitoring-system/newrelic')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle NewRelic alerts
    """

    data = row_data.dict()
    try:
        data['integration_key'] = integration_key
        data['environment_id'] = environment_id
        data['scenario_id'] = scenario_id

        event = ReceiveEvent(content=data, ms='newrelic')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from NewRelic.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
