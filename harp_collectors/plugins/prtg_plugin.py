from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid

log = service_logger()


class PRTGProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None
        self.scenario_id = None
        self.environment_id = None
        self.integration_key = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        linkprobe = self.content['linkprobe']
        linkdevice = self.content['linkdevice']
        linksensor = self.content['linksensor']

        info_url = {
            "Probe URL": linkprobe,
            "Device URL": linkdevice,
            "Sensor URL": linksensor
        }

        return info_url

    def define_additional_fields(self):
        additional_fields = {
            "status": self.content['laststatus'],
            "device": self.content['device'],
            "group": self.content['group'],
            "sensor": self.content['sensor'],
            "server": self.content['server'],
            "host": self.content['host']
        }

        return additional_fields

    def define_notification_status(self):
        if self.content['laststatus'].lower() == 'down':
            return 1
        elif self.content['laststatus'].lower() == 'unknown':
            return 1
        elif self.content['laststatus'].lower() == 'warning':
            return 1
        elif self.content['laststatus'].lower() == '%laststatus':
            return 1
        elif self.content['laststatus'].lower() == 'up':
            return 0
        elif self.content['laststatus'].lower() == 'paused':
            return 0
        else:
            log.error(
                msg=f"Unknown PRTG state: {self.content['laststatus']}. Currently integration support only UP, DOWN, unknown and Warning states",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.define_notification_status() == 1:
            if self.content['laststatus'] == 'Down':
                severity = 'critical'
            elif self.content['laststatus'] == 'Warning':
                severity = 'warning'
            elif self.content['laststatus'] == 'Unknown':
                severity = 'unknown'
            elif self.content['laststatus'] == 'Paused':
                severity = 'ok'
            else:
                severity = 'ok'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = self.content['device']

        return object_name

    def define_service_name(self):
        return self.content['group']

    def define_notification_output(self):
        output = self.content['lastmessage']

        if 'lastvalue' in self.content:
            output = f"{output}. Value - {self.content['lastvalue']}"

        return output

    def define_studio(self):
        return self.content['studio_id']

    def define_source(self):
        source = self.content['home']
        return source

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        return self.content['procedure_id']

    def define_alert_name(self):
        full_name = self.content['name']

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "prtg",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
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
        self.scenario_id = self.content['scenario_id']
        self.environment_id = self.content['environment_id']
        self.integration_key = self.content['integration_key']
        return push_to_kafka(self.prepare_final_json())
