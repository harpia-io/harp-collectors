from logger.logging import service_logger
import harp_collectors.settings as settings
from harp_collectors.logic.kafka_confluent_producer import KafkaProduceMessages

log = service_logger()
producer = KafkaProduceMessages()


def check_object_name_length(object_name):
    if len(object_name) > 90:
        object_name = f'{object_name[:90]}...'

    return object_name


def check_alert_name_length(alert_name):
    if len(alert_name) > 250:
        alert_name = f'{alert_name[:250]}...'

    return alert_name


def push_to_kafka(event_body, event_id=None):
    event_body["object_name"] = check_object_name_length(event_body["object_name"])
    event_body["alert_name"] = check_alert_name_length(event_body["alert_name"])
    if event_body["severity"] != 1:
        try:
            producer.produce_message(settings.EVENTS_TOPIC, event_body)

            log.info(msg=f"Send event to Kafka.\nevent_body: {event_body}")

            return str("Event successfully pushed to Harp")
        except Exception as err:
            log.error(
                msg=f"FAILED. Error during pushing message to Kafka - {err}\n{event_body}",
                extra={'tags': {'event_id': event_id}}
            )

            return str("Error during pushing message to Kafka")
