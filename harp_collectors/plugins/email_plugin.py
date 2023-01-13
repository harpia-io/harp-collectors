from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json

log = service_logger()


class EmailProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    @staticmethod
    def define_additional_urls():
        info_url = {}

        return info_url

    @staticmethod
    def define_additional_fields():
        info_url = {}

        return info_url

    @staticmethod
    def define_notification_status():
        return 1

    @staticmethod
    def severity_transformation():
        severity = 'critical'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    @staticmethod
    def define_object_name():
        object_name = 'email'

        return object_name

    @staticmethod
    def define_service_name():
        return 'email'

    def define_notification_output(self):
        return f"You should receive email with next subject - {self.content['subject']}. Please check it. Pay attention that you should resolve alerts manually once you check it"

    @staticmethod
    def define_studio():
        return 'Other'

    def define_source(self):
        return self.content['sender']

    @staticmethod
    def define_actions():
        return {}

    @staticmethod
    def define_procedure_id():
        return settings.EMAIL_INTEGRATION['default_procedure']

    def define_alert_name(self):
        full_name = self.content['subject']

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "email",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": self.define_procedure_id(),
            "integration_key": None
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
