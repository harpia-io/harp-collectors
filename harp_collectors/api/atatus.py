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
    account_id: str
    alert_url: str
    incident_id: str
    incident_url: str
    alert_policy_id: str
    alert_policy_name: str
    rule_id: str
    rule_name: str
    target_name: str
    status: str
    duration: Union[None, str]
    acknowledge_url: str
    acknowledged_user: Union[None, str]
    description: str
    severity: str
    product: str
    timestamp: str


@router.post('/monitoring-system/atatus')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Atatus alerts
    """

    data = row_data.dict()

    try:
        data['integration_key'] = integration_key
        data['environment_id'] = environment_id
        data['scenario_id'] = scenario_id

        event = ReceiveEvent(content=data, ms='atatus')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from Atatus.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
