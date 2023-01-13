from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json

log = service_logger()


class AtatusProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        info_url = {"Incident URL": self.content['incident_url']}

        if 'dashboard_url' in self.content:
            info_url['Grafana Dashboard'] = self.content['dashboard_url']

        return info_url

    @staticmethod
    def define_additional_fields():
        info_url = {}

        return info_url

    def define_notification_status(self):
        if self.content['status'] == 'Opened':
            return 1
        elif self.content['status'] == 'Closed':
            return 0
        else:
            log.error(
                msg=f"Unknown Atatus status: {self.content['status']}. Currently integration support only ok and alerting",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.define_notification_status() == 1:
            if self.content['severity'] == 'Critical':
                severity = 'critical'
            elif self.content['severity'] == 'Warning':
                severity = 'warning'
            else:
                severity = 'ok'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = f"AlertID:{self.content['rule_id']}"

        return object_name

    def define_service_name(self):
        return self.content['target_name']

    def define_notification_output(self):
        return f"Details: {self.content['description']}"

    def define_studio(self):
        return json.loads(self.content['message'].split(":::")[-1])['environment_id']

    def define_source(self):
        return self.content['product']

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        return self.content['scenario_id']

    def define_alert_name(self):
        full_name = self.content['rule_name']

        return full_name

    def prepare_final_json(self, scenario_id, environment_id, integration_key):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "atatus",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": scenario_id,
            "integration_key": integration_key
        }

        return final_json

    def process_event(self):
        scenario_id = self.content['scenario_id']
        environment_id = self.content['environment_id']
        integration_key = self.content['integration_key']
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json(scenario_id=scenario_id, environment_id=environment_id, integration_key=integration_key))
