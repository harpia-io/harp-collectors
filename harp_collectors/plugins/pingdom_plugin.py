from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json
from urllib.parse import urlparse

log = service_logger()


class PingdomProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        info_url = {"Pingdom URL": f"https://my.pingdom.com/app/reports/uptime#check={self.content['check_id']}"}

        return info_url

    def define_additional_fields(self):
        additional_fields = {
            "check_type": self.content['check_type']
        }

        return additional_fields

    def define_notification_status(self):
        if self.content['current_state'] == 'DOWN':
            return 1
        if self.content['current_state'] == 'UP':
            return 0
        else:
            log.error(
                msg=f"Unknown Pingdom status: {self.content['metrics']}. Currently integration support only UP and DOWN",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.content['current_state'] == 'DOWN':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        return str(self.content['check_id'])

    def define_service_name(self):
        if 'service' in self.content:
            return self.content['service']
        else:
            return 'not_defined'

    def define_notification_output(self):
        return self.content['long_description']

    def define_studio(self):
        return json.loads(self.content['message'].split(":::")[-1])['studio_id']

    @staticmethod
    def define_source():
        return "pingdom"

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        try:
            if 'PR_ID' in self.content['check_name']:
                procedure_id = self.content['check_name'].split("]")[0].split(":")[1].replace(" ", "")

                return procedure_id
            else:
                return self.content['scenario_id']
        except Exception as err:
            log.error(
                msg=f"Can`t get procedure_id from Pingdom alert name: {self.content['check_name']}. ERROR: {err}",
                extra={
                    "event_id": self.content['event_id']
                })

    def define_alert_name(self):
        full_name = self.content['check_name']

        return full_name

    def prepare_final_json(self, environment_id, integration_key):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "pingdom",
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
            "integration_key": integration_key
        }

        return final_json

    def process_event(self):
        environment_id = self.content['environment_id']
        integration_key = self.content['integration_key']
        self.event_id = str(uuid.uuid4())
        result = push_to_kafka(self.prepare_final_json(environment_id=environment_id, integration_key=integration_key))

        return result
