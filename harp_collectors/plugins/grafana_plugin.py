from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json
from urllib.parse import urlparse

log = service_logger()


class GrafanaProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None
        self.scenario_id = None
        self.environment_id = None
        self.integration_key = None

    def define_graph_url(self):
        return self.content['ruleUrl']

    def define_additional_urls(self):
        info_url = {"URL to Grafana": self.content['ruleUrl']}

        return info_url

    def define_additional_fields(self):
        additional_fields = {}
        for metric in self.content['evalMatches']:
            additional_fields.update(metric['tags'])

        return additional_fields

    def define_notification_status(self):
        if self.content['state'] == 'alerting':
            return 1
        elif self.content['state'] == 'ok':
            return 0
        else:
            log.warning(
                msg=f"Unknown Grafana state: {self.content['state']}. Currently integration support only ok and alerting\nContent: {self.content}",
                extra={"event_id": self.event_id}
            )
            return 0

    def severity_transformation(self):
        if self.content['state'] == 'alerting':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    @staticmethod
    def define_object_name():
        object_name = 'grafana'

        return object_name

    def define_service_name(self):
        o = urlparse(self.content['ruleUrl'])
        dashboard_name = o.path.split("/")[-1]

        return dashboard_name

    def define_notification_output(self):
        if self.content['evalMatches']:
            metrics_list = []
            for index, metric in enumerate(self.content['evalMatches']):
                metrics_list.append(f'Metric {index + 1}: {metric}')

            return '<br>'.join(metrics_list)
        else:
            return f"Value: {self.content['evalMatches']}"

    def define_studio(self):
        if "tags" in self.content:
            if "environment_id" in self.content['tags']:
                environment_id = int(self.content['tags']['environment_id'])
                # log.info(msg=f"Get environment_id from alert tags - {environment_id}")

                return environment_id

        if "environment_id" in self.content['message']:
            environment_id = int(json.loads(self.content['message'].split(":::")[-1])['environment_id'])
            # log.info(msg=f"Get environment_id from alert message body - {environment_id}")

            return environment_id

        if self.environment_id:
            environment_id = int(self.environment_id)
            # log.info(msg=f"Get environment_id from notification channel URL - {environment_id}")

            return environment_id

        # log.info(msg="environment_id is not defined in alert message body and notification channel URL. Set to None")
        return None

    def define_source(self):
        o = urlparse(self.content['ruleUrl'])
        return o.netloc

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        if "tags" in self.content:
            if "scenario_id" in self.content['tags']:
                scenario_id = int(self.content['tags']['scenario_id'])
                # log.info(msg=f"Get scenario_id from alert tags - {scenario_id}")

                return scenario_id

        if "scenario_id" in self.content['message']:
            scenario_id = int(json.loads(self.content['message'].split(":::")[-1])['scenario_id'])
            # log.info(msg=f"Get scenario_id from alert message body - {scenario_id}")

            return scenario_id

        if self.scenario_id:
            scenario_id = int(self.scenario_id)
            # log.info(msg="Get scenario_id from notification channel URL")

            return scenario_id

        # log.info(msg="scenario_id is not defined in alert message body and notification channel URL. Set to None")
        return None

    def define_alert_name(self):
        full_name = self.content['ruleName']

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "grafana",
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
            "integration_key": self.integration_key
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        self.scenario_id = self.content['scenario_id']
        self.environment_id = self.content['environment_id']
        self.integration_key = self.content['integration_key']
        return push_to_kafka(self.prepare_final_json())
