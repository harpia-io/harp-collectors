import os

KAFKA_SERVERS = os.getenv('KAFKA_SERVERS', '127.0.0.1:9092')
EVENTS_TOPIC = os.getenv('EVENTS_TOPIC', 'harpia-notifications')

CREATE_NOTIFICATION_ICINGA_TOPIC = os.getenv('CREATE_NOTIFICATION_ICINGA_TOPIC', 'harpia-create-notifications-icinga')
CREATE_NOTIFICATION_ZABBIX_TOPIC = os.getenv('CREATE_NOTIFICATION_ZABBIX_TOPIC', 'harpia-create-notifications-zabbix')
KAFKA_CONSUMER_THREADS = int(os.getenv('KAFKA_CONSUMER_THREADS', 1))

producer_message_send_max_retries = os.getenv('producer_message_send_max_retries', 6)
producer_retry_backoff_ms = os.getenv('producer_retry_backoff_ms', 5000)
producer_queue_buffering_max_ms = os.getenv('producer_queue_buffering_max_ms', 10000)
producer_queue_buffering_max_messages = os.getenv('producer_queue_buffering_max_messages', 100000)
producer_request_timeout_ms = os.getenv('producer_request_timeout_ms', 30000)
consumer_session_timeout_ms = os.getenv('consumer_session_timeout_ms', 30000)
consumer_heartbeat_interval_ms = os.getenv('consumer_heartbeat_interval_ms', 15000)
POD_NAME = os.getenv('POD_NAME', '')

SEVERITY_MAPPING = {
	"ok": 0,
	"information": 1,
	"warning": 2,
	"critical": 3,
	"unknown": 4,
	"urgent": 5,
	"down": 6
}

NOTIFICATION_TYPE_MAPPING = {
	"alert": 1,
	"email": 2,
	"jira": 3,
	"skype": 4,
	"teams": 5,
	"telegram": 6
}

EMAIL_INTEGRATION = {
	"default_procedure": 1
}
