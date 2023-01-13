from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json
from urllib.parse import urlparse

log = service_logger()


class AnodotProcessor(object):
    def __init__(self, content):
        self.content = content
        self.investigation_url = None
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        info_url = {"Alert Settings": self.content['alertSettingsUrl']}

        if self.investigation_url:
            info_url['Investigation Url'] = self.investigation_url

        return info_url

    def define_additional_fields(self):
        info_url = {"Description": self.content['description']}

        return info_url

    def define_notification_status(self):
        if self.content['metrics'][0]['state'] == 'OPEN':
            return 1
        elif self.content['metrics'][0]['state'] == 'CLOSED':
            return 0
        else:
            log.error(
                msg=f"Unknown Anodot status: {self.content['metrics']}. Currently integration support only ok and alerting",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.content['metrics'][0]['state'] == 'OPEN':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = f"AlertID:{self.content['alertId']}"

        return object_name

    def define_service_name(self):
        if 'service' in self.content:
            return self.content['service']
        else:
            return 'not_defined'

    @staticmethod
    def define_notification_output():
        return ""

    def define_studio(self):
        return json.loads(self.content['message'].split(":::")[-1])['environment_id']

    def define_source(self):
        o = urlparse(self.content['alertSettingsUrl'])
        return o.netloc

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self, scenario_id):
        try:
            if 'PR_ID' in self.content['title']:
                procedure_id = self.content['title'].split("]")[0].split(":")[1].replace(" ", "")

                return procedure_id
            else:
                return scenario_id
        except Exception as err:
            log.error(
                msg=f"Can`t get procedure_id from Anodot alert name: {self.content['title']}. ERROR: {err}",
                extra={
                    "event_id": self.content['event_id']
                })

    def define_alert_name(self):
        full_name = self.content['title']

        return full_name

    def define_investigation_url(self):
        if 'investigationUrl' in self.content:
            return self.content['investigationUrl']
        else:
            return None

    def prepare_final_json(self, environment_id, scenario_id, integration_key):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "anodot",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": self.define_procedure_id(scenario_id=scenario_id),
            "integration_key": integration_key
        }

        return final_json

    def process_event(self):
        result = None
        environment_id = self.content['environment_id']
        scenario_id = self.content['scenario_id']
        integration_key = self.content['integration_key']
        self.investigation_url = self.define_investigation_url()
        multi_events = self.content['alerts']
        for single_event in multi_events:
            self.content = single_event
            self.event_id = str(uuid.uuid4())

            result = push_to_kafka(self.prepare_final_json(environment_id=environment_id, scenario_id=scenario_id, integration_key=integration_key))

        return result
