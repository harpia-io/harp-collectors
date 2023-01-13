from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json

log = service_logger()


class CrashlyticsProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        info_url = {'URL to Crashlytics': self.content['payload']['url']}

        return info_url

    @staticmethod
    def define_additional_fields():
        info_url = {}

        return info_url

    def define_notification_status(self):
        if self.content['payload_type'] == 'issue':
            return 1
        else:
            return 0

    def severity_transformation(self):
        if self.content['payload_type'] == 'issue':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = self.content['event']

        return object_name

    @staticmethod
    def define_service_name():
        return 'Client'

    def define_notification_output(self):
        return f"Crashes count: {self.content['payload']['crashes_count']}, " \
               f"impacted device count: {self.content['payload']['impacted_devices_count']}, " \
               f"method name of issue: {self.content['payload']['method']}"

    def define_studio(self):
        return self.content['environment_id']

    @staticmethod
    def define_source():
        return 'Crashlytics'

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        return self.content['scenario_id']

    def define_alert_name(self):
        full_name = self.content['payload']['title']

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "crashlytics",
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
            "integration_key": self.content['integration_key']
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
