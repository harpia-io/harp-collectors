from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json

log = service_logger()


class CloudwatchProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

        if 'graph_url' in json.loads(self.content['AlarmDescription']):
            return json.loads(self.content['AlarmDescription'])['graph_url']

    @staticmethod
    def define_additional_urls():
        info_url = {}

        return info_url

    def define_additional_fields(self):
        info_url = {
            "Region": self.content['Region'],
            "Namespace": self.content['Trigger']['Namespace'],
            "Period": self.content['Trigger']['Period'],
            "EvaluationPeriods": self.content['Trigger']['EvaluationPeriods'],
            "ComparisonOperator": self.content['Trigger']['ComparisonOperator'],
            "Threshold": self.content['Trigger']['Threshold']
        }

        return info_url

    def define_notification_status(self):
        if self.content['NewStateValue'] != 'OK':
            return 1
        else:
            return 0

    def severity_transformation(self):
        if self.content['NewStateValue'] != 'OK':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        # log.info(
        #     msg=f"Define object name. Before - {self.content['Trigger']['Dimensions']}\nFull Message: {self.content}",
        #     extra={"event_id": self.event_id}
        # )

        if self.content['Trigger']['Dimensions']:
            return self.content['Trigger']['Dimensions'][0]['value']
        else:
            return self.content['Trigger']['Namespace']

    def define_service_name(self):
        if 'service' in self.content:
            return self.content['service']

        if 'service_name' in self.content:
            return self.content['service_name']

        return 'not_defined'

    def define_notification_output(self):
        return self.content['NewStateReason']

    def define_studio(self):
        if 'environment_id' in json.loads(self.content['AlarmDescription']):
            return json.loads(self.content['AlarmDescription'])['environment_id']
        else:
            return self.content['environment_id']

    def define_source(self):
        return json.loads(self.content['AlarmDescription'])['source']

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        if 'scenario_id' in json.loads(self.content['AlarmDescription']):
            return json.loads(self.content['AlarmDescription'])['scenario_id']

    def define_alert_name(self):
        full_name = f"{self.content['AlarmName']}. MetricName: {self.content['Trigger']['MetricName']}"

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "cloudwatch",
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
