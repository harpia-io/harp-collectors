from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json

log = service_logger()


class ApiProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        info_url = {}
        if 'additional_urls' in self.content:
            for key, value in self.content['additional_urls'].items():
                info_url[key] = value

        if 'graph_url' in self.content:
            if self.content['graph_url'] is not None:
                info_url['Graph URL'] = self.content['graph_url']

        return info_url

    def define_additional_fields(self):
        info_url = {}
        if 'additional_fields' in self.content:
            for key, value in self.content['additional_fields'].items():
                info_url[key] = str(value)

        return info_url

    def define_notification_status(self):
        if self.content['alert_severity'] != 'ok':
            return 1
        else:
            return 0

    def severity_transformation(self):
        severity_id = settings.SEVERITY_MAPPING[self.content['alert_severity']]

        return severity_id

    def define_object_name(self):
        # log.info(
        #     msg=f"Change object name. Before - {self.content['object']}",
        # )

        if 'additional_fields' in self.content:
            if 'script' in self.content['additional_fields']:
                script_name = self.content['additional_fields']['script']
            elif 'plugin_name' in self.content['additional_fields']:
                script_name = self.content['additional_fields']['plugin_name']
            else:
                script_name = None

            if script_name:
                object_name = f"{self.content['object']}:{script_name.split('/')[-1]}"

                # log.info(msg=f"Change object name. After - {object_name}", )

                return object_name
            # else:
            #     log.info(
            #         msg="script or plugin_name fields were not detected for API alert. Please check if your script sends it."
            #             f"Details:\n{self.content['additional_fields']}",
            #         extra={"event_id": self.event_id})

        # elif self.content['notification_status'] != 0:
        #     log.info(
        #         msg="additional_fields were not detected for API alert. "
        #             "It means that script or plugin_name are empty as well. Please check if your script sends it. "
        #             f"Details:\n{self.content}",
        #         extra={"event_id": self.event_id})

        return self.content['object']

    def define_service_name(self):
        if 'service' in self.content:
            return self.content['service']

        if 'service_name' in self.content:
            return self.content['service_name']

        return 'not_defined'

    def define_notification_output(self):
        if 'notification_output' in self.content:
            if isinstance(self.content['notification_output'], dict):
                # log.info(msg=f"Convert output to string: {self.content['notification_output']}: {type(self.content['notification_output'])}")
                return json.dumps(self.content['notification_output'])
            else:
                # log.info(msg=f"Output: {self.content['notification_output']}: {type(self.content['notification_output'])}")
                return str(self.content['notification_output'])

    def define_environment(self):
        return self.content['environment_id']

    @staticmethod
    def define_actions():
        return {}

    def define_scenario_id(self):
        if 'scenario_id' in self.content:
            return self.content['scenario_id']

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.content['alert_name'],
            "notification_status": self.define_notification_status(),
            "studio": self.define_environment(),
            "severity": self.severity_transformation(),
            "source": self.content['source'],
            "monitoring_system": "api",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": self.define_scenario_id(),
            "integration_key": self.content['integration_key']
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
