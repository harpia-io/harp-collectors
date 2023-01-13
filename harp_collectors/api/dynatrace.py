from logger.logging import service_logger
from harp_collectors.collectors import ReceiveEvent
import traceback
from pydantic import BaseModel
from fastapi import APIRouter, HTTPException, Header
import harp_collectors.settings as settings
from typing import Optional, Union

log = service_logger()

router = APIRouter(prefix=settings.URL_PREFIX)


class MSBody(BaseModel):
    studio_id: Optional[int] = None
    procedure_id: Optional[int] = None
    PID: str
    ProblemDetailsText: str
    ProblemID: str
    ProblemImpact: str
    ProblemSeverity: str
    ProblemTitle: str
    ProblemURL: str
    State: str
    Tags: Union[dict, str]


@router.post('/monitoring-system/dynatrace')
async def api_ms(
        row_data: MSBody,
        integration_key: Optional[str] = None,
        environment_id: Optional[int] = None,
        scenario_id: Optional[int] = None,
        dynatrace_dns: Optional[str] = Header(None)
):
    """
    Handle Dynatrace alerts
    """

    data = row_data.dict()

    try:
        data['scenario_id'] = scenario_id
        data['environment_id'] = environment_id
        data['dynatrace_dns'] = dynatrace_dns
        data['integration_key'] = integration_key

        event = ReceiveEvent(content=data, ms='dynatrace')
        result = event.processor()

        return {'result': result}
    except Exception as err:
        log.error(msg=f"Can`t process event from Dynatrace.\nERROR: {err}\nStack: {traceback.format_exc()}")

        raise HTTPException(status_code=500, detail=f"Backend error: {err}")
