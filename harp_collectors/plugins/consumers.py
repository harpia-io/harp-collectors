from logger.logging import service_logger
import harp_collectors.settings as settings
import ujson as json
import traceback
from harp_collectors.collectors import ReceiveEvent
from harp_collectors.logic.kafka_confluent_consumer import KafkaConsumeMessages

logger = service_logger()


class ConsumeMessages(object):
    def __init__(self, ms_name, topic):
        self.ms_name = ms_name
        self.topic = topic

    def process_message(self, parsed_json):
        # logger.info(msg=f"Receive event from endpoint\n{parsed_json}")
        event = ReceiveEvent(content=parsed_json, ms=self.ms_name)
        event.processor()

    def start_consumer(self, consumer_num=settings.SERVICE_NAME):
        """
        Start metrics consumer
        """

        consumer = KafkaConsumeMessages(kafka_topic=self.topic).start_consumer()

        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                logger.error(msg=f"Consumer error: {msg.error()}")
                continue

            parsed_json = None
            try:
                parsed_json = json.loads(msg.value().decode('utf-8'))
                # logger.info(f"Get event from Kafka: {parsed_json}. Consumer - {consumer_num}")
                self.process_message(parsed_json)
            except Exception as err:
                logger.error(msg=f"Exception in Thread: {err}\nStack: {traceback.format_exc()}\n{parsed_json}")
                continue

    def main(self):
        self.start_consumer()


