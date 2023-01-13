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
    host_name: str
    trigger_severity: str
    eventname: str
    trigger_expression: str
    source: str
    trigger_description: str
    trigger_id: str
    event_id: str
    trigger_hostgroup_name: str
    event_action: str
    trigger_status: str
    eventack: str
    eventdate: str
    eventtags: str
    eventtime: str
    eventupdate: str
    eventvalue: str
    event_source: str
    hostip: str
    triggeropdata: str
    trigger_name: str


@router.post('/monitoring-system/zabbix')
async def api_ms(row_data: MSBody, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle Zabbix alerts
    """

    data = row_data.dict()
    try:
        data['integration_key'] = integration_key

        if 'environment_id' not in data:
            data['environment_id'] = environment_id

        if 'scenario_id' not in data:
            data['scenario_id'] = scenario_id

        log.info(msg=f"Receive Zabbix Event: {data}")

        event = ReceiveEvent(content=data, ms='zabbix')
        result = event.processor()

        log.info(msg=f"Zabbix event was proceeded - {result}")

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from Zabbix endpoint\nData:{data}\nError: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
