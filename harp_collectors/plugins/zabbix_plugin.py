from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid

log = service_logger()


class ZabbixProcessor(object):
    def __init__(self, content):
        self.content = content
        self.ms_unique_data = {}
        self.event_id = None

    def define_notification_status(self):
        if 'trigger_status' in self.content:
            alert_status = self.content['trigger_status'].lower()
        else:
            alert_status = 'problem'

        if alert_status == 'problem':
            return 1
        elif alert_status == 'ok':
            return 0
        else:
            log.error(
                msg=f"Notification status is unknown. Content: {self.content}",
                extra={"monitoring_system": "zabbix", "event_id": self.content["event_id"]})

    def define_alert_name(self):
        alert_name = self.content['trigger_name']

        return alert_name

    def severity_transformation(self):
        if 'trigger_severity' in self.content:
            severity = self.content['trigger_severity']
        else:
            severity = 'High'

        if self.define_notification_status() == 0:
            severity = 'ok'

        try:
            severity = int(severity)
        except Exception:
            severity = severity

        if isinstance(severity, int):
            # Severity mapping from Kafka topic
            if severity == 0:
                severity = 'unknown'
            elif severity == 1:
                severity = 'information'
            elif severity == 2:
                severity = 'warning'
            elif severity == 3:
                severity = 'warning'
            elif severity == 4:
                severity = 'critical'
            elif severity == 5:
                severity = 'urgent'
        else:
            # Severity mapping from REST API
            if severity == 'Information':
                severity = 'information'
            elif severity == 'Warning':
                severity = 'warning'
            elif severity == 'High':
                severity = 'critical'
            elif severity == 'Disaster':
                severity = 'urgent'
            elif severity == 'Average':
                severity = 'warning'
            elif severity == 'Not classified':
                severity = 'unknown'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_ms_alert_id(self):
        if 'trigger_id' in self.content:
            return self.content['trigger_id']

    def define_notification_output(self):
        output = f"Value: {self.content['triggeropdata']}\nExpression: {self.content['trigger_expression']}\nDescription: {self.content['trigger_description']}"

        return output

    @staticmethod
    def define_graph_url():
        return None

    def define_additional_urls(self):
        info_url = {}

        if 'trigger_id' in self.content:
            trigger_url = f"{self.content['source']}/tr_events.php?triggerid={self.content['trigger_id']}&eventid={self.content['event_id']}"
            info_url['Trigger URL'] = trigger_url

        return info_url

    def define_additional_fields(self):
        additional_fields = {
            "group": self.content['trigger_hostgroup_name'],
            "host": self.content['host_name']
        }

        return additional_fields

    def define_service_name(self):
        if 'trigger_hostgroup_name' in self.content:
            return self.content['trigger_hostgroup_name']
        else:
            return 'not_defined'

    def define_studio(self):
        if 'environment_id' in self.content:
            if self.content['environment_id']:
                return self.content['environment_id']

        if 'studio' in self.content:
            return self.content['studio']

    def define_procedure_id(self):
        if 'scenario_id' in self.content:
            if self.content['scenario_id']:
                return self.content['scenario_id']

        if 'procedure_id' in self.content:
            return self.content['procedure_id']

    def define_object_name(self):
        return self.content['host_name']

    def define_source(self):
        return self.content['source']

    def prepare_final_json(self):

        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "zabbix",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": self.define_ms_alert_id(),
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": {},
            "procedure_id": self.define_procedure_id(),
            "integration_key": self.content['integration_key']
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
