from logger.logging import service_logger
from harp_collectors.collectors import ReceiveEvent
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException
import harp_collectors.settings as settings
from typing import Optional
import re

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class MSBody(BaseModel):
    account_id: str
    controller_link_url: str
    policy_name: str
    clamped: bool
    action_id: int
    full_events_list: list
    from_web_hook: bool
    account_name: str
    clamp_limit: int
    action_trigger_time: str
    policy_digest: bool
    policy_id: str
    action_name: str


@router.post('/monitoring-system/appdynamics')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle AppDynamics alerts
    """

    data = row_data.dict()

    try:
        data['integration_key'] = integration_key
        data['scenario_id'] = scenario_id
        data['environment_id'] = environment_id

        event = ReceiveEvent(content=data, ms='appdynamics')
        result = event.processor()

        return {'result': result}, 200
    except Exception as err:
        log.error(msg=f""
                      f"Can`t process event from AppDynamics endpoint\n"
                      f"Data:{data}\n"
                      f"Error: {err}\n"
                      f"Stack: {traceback.format_exc()}"
                  )

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")


def appd_wrong_format_fixer(input_json):
    string_without_space = re.sub('\s+', ' ', input_json.decode()).strip()
    new_string = string_without_space.replace("}, ]", "}]")

    return new_string

