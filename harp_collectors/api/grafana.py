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
    dashboardId: int
    evalMatches: list
    message: str
    orgId: int
    panelId: int
    ruleId: int
    ruleName: str
    ruleUrl: str
    state: str
    tags: dict
    title: str


@router.post('/monitoring-system/grafana')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Grafana alerts
    """

    data = row_data.dict()
    grafana_state_ignore = ['paused', 'pending', 'no_data']

    log.info(msg=f"Received Grafana alert.\nData: {data}")

    try:
        if data['state'] not in grafana_state_ignore:
            data['scenario_id'] = scenario_id
            data['environment_id'] = environment_id
            data['integration_key'] = integration_key
            event = ReceiveEvent(content=data, ms='grafana')
            result = event.processor()

            return {'result': result}
        else:
            return {'result': f'Current alert state in ignore list: {grafana_state_ignore}'}
    except Exception as err:
        log.error(msg=f"Can`t process event from Grafana.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")


