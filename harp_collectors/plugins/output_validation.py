from logger.logging import service_logger
import ujson as json
import os
import jsonschema as js

PWD = os.path.dirname(os.path.abspath(__file__))
log = service_logger()


def validate_data(data_to_validate, schema_name, event_id=None):
    input_alert_schema = f'{PWD}/../../schemas/{schema_name}'
    # log.debug(
    #     msg=f"Start validating input alert: {input_alert_schema}",
    #     extra={"event_id": event_id}
    # )
    with open(input_alert_schema, 'r') as f:
        schema_data = f.read()
    schema = json.loads(schema_data)

    try:
        js.validate(data_to_validate, schema=schema)
        valid_error = 'valid'
    except js.ValidationError as e:
        log.error(
            msg=f"Wrong alert format according JSON Scheme - {e}",
            extra={"event_id": event_id}
        )
        valid_error = e.message
    except js.SchemaError as e:
        valid_error = e
        log.error(
            msg=f"Wrong alert format according JSON Scheme - {e}",
            extra={"event_id": event_id}
        )

    # log.debug(
    #     msg=f"Stop validating input alert. Error - {valid_error}",
    #     extra={"event_id": event_id}
    # )

    return {"error": valid_error, "output_data": data_to_validate}
