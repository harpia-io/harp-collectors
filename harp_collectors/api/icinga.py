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
    PROCEDURE: str
    NOTIFICATIONAUTHORNAME: str
    SERVICENOTES: str
    SERVICENAME: str
    SERVICEDOWNTIME: str
    SERVICEACTIONURL: str
    HOSTNAME: str
    HOSTADDRESS: str
    SEVERITY: int
    SERVICENOTESURL: str
    LASTSTATETYPE: str
    NOTIFICATIONTYPE: str
    HOSTSERVICE: str
    HOSTROLE: str
    ICINGASERVER: str
    SERVICESTATE: str
    SERVICEOUTPUT: str
    SERVICESTATETYPE: str
    NOTIFICATIONCOMMENT: str
    PROCEDURE_ID: str
    PROBLEMTYPE: str
    SERVICEGRAPH: str


@router.post('/monitoring-system/icinga')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Icinga alerts
    """

    data = row_data.dict()
    try:
        data['integration_key'] = integration_key

        if 'environment_id' not in data:
            data['environment_id'] = environment_id

        if 'scenario_id' not in data:
            data['scenario_id'] = scenario_id

        event = ReceiveEvent(content=data, ms='icinga')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from Icinga endpoint\nData:{data}\nError: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
