from logger.logging import service_logger
from harp_collectors.collectors import ReceiveEvent
import traceback
from pydantic import BaseModel
from fastapi import Request, APIRouter, HTTPException
import harp_collectors.settings as settings
from typing import Optional
import urllib.parse
import uuid

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class MSBody(BaseModel):
    datetime: str
    device: str
    deviceid: str
    group: str
    home: str
    host: str
    lastmessage: str
    laststatus: str
    lastvalue: str
    linkprobe: str
    linkdevice: str
    linksensor: str
    location: str
    name: str
    priority: str
    probe: str
    programname: str
    sensor: str
    server: str
    serviceurl: str
    shortname: str
    status: str


@router.post('/monitoring-system/prtg')
async def api_ms(row_data: Request, integration_key: Optional[str] = None, environment_id: Optional[int] = None, scenario_id: Optional[int] = None):
    """
    Handle PRTG alerts
    """
    event_id = uuid.uuid4()
    data = await row_data.body()

    try:
        log.info(
            msg=f'Receive PRTG raw data: {data}',
            extra={"event_id": event_id}
        )

        decode_data = urllib.parse.unquote(data).replace('["State":"ok"]', '[State:ok]')

        res = urllib.parse.parse_qs(decode_data)

        data = {k: v[0] for k, v in res.items()}
    except Exception as err:
        log.error(msg=f"Can`t process event from PRTG.\nERROR: {err}\nStack: {traceback.format_exc()}\nData: {data}")

    try:
        data['integration_key'] = integration_key
        data['scenario_id'] = environment_id
        data['environment_id'] = scenario_id

        event = ReceiveEvent(content=data, ms='prtg')
        result = event.processor()

        log.info(
            msg=f'PRTG result: {result}\n{data}',
            extra={"event_id": event_id}
        )

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from PRTG.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
