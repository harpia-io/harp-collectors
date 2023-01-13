from logger.logging import service_logger
import harp_collectors.settings as settings
from confluent_kafka import Consumer

logger = service_logger()


class KafkaConsumeMessages(object):
    def __init__(self, kafka_topic):
        self.kafka_topic = kafka_topic

    def start_consumer(self):
        """
        Start consumer
        """

        logger.debug(f"Initializing Kafka Confluent Consumer - {settings.SERVICE_NAME}. Topic - {self.kafka_topic}")

        consumer = Consumer(
            {
                'bootstrap.servers': settings.KAFKA_SERVERS,
                'group.id': settings.SERVICE_NAME,
                'auto.offset.reset': 'latest',
                'allow.auto.create.topics': True,
                'session.timeout.ms': settings.consumer_session_timeout_ms,
                'heartbeat.interval.ms': settings.consumer_heartbeat_interval_ms,
                'offset.store.method': 'broker'
            }
        )

        consumer.subscribe([self.kafka_topic])

        return consumer
