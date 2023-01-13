from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid

log = service_logger()


class GCProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None
        self.scenario_id = None
        self.environment_id = None
        self.integration_key = None

    @staticmethod
    def define_graph_url():
        return None

    def define_additional_urls(self):
        info_url = {
            "Alert URL": self.content['incident']['url'],
        }

        return info_url

    def define_additional_fields(self):
        additional_fields = {}

        for key, value in self.content['incident']['resource']['labels'].items():
            additional_fields[key] = str(value)

        return additional_fields

    def define_notification_status(self):
        if self.content['incident']['state'] == 'open':
            return 1
        elif self.content['incident']['state'] == 'closed':
            return 0
        else:
            log.error(
                msg=f"Unknown GCP state: {self.content['incident']['state']}. Currently integration support only OPEN and CLOSED states",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.content['incident']['state'] == 'open':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = self.content['incident']['resource_display_name']

        return object_name

    def define_service_name(self):
        return self.content['incident']['resource_type_display_name']

    def define_notification_output(self):
        output = self.content['incident']['summary']

        return output

    def define_studio(self):
        return self.content['studio_id']

    def define_source(self):
        source = self.content['incident']['resource']['type']
        return source

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        return self.content['procedure_id']

    def define_alert_name(self):
        full_name = self.content['incident']['policy_name']

        return full_name

    def define_ms_alert_id(self):
        ms_alert_id = self.content['incident']['incident_id']

        return ms_alert_id

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "gcp",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": self.define_ms_alert_id(),
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": self.scenario_id,
            "integration_key": self.integration_key
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        self.integration_key = self.content['integration_key']
        return push_to_kafka(self.prepare_final_json())
