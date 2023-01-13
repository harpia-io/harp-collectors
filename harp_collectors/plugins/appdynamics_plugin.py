from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import urllib.parse

log = service_logger()


class AppDynamicsProcessor(object):
    def __init__(self, content):
        self.content = content
        self.ms_unique_data = {}
        self.scenario_id = None
        self.environment_id = None
        self.integration_key = None

    def transform_appd_hostname(self):
        if self.content['affected_entities'][0]['type'] == "APPLICATION_COMPONENT_NODE":
            short_name = self.content['affected_entities'][0]['name'].split(".")[0]
            try:
                additional_info = self.content['affected_entities'][0]['name'].split(".")[1]
            except IndexError:
                additional_info = self.content['affected_entities'][0]['name']

            hostname = "{0}.{1}".format(short_name, additional_info.split("-")[0])

            short_service_name = additional_info.split("-")[1:]
            service_name = "-".join(short_service_name)

            date = {
                "hostname": hostname,
                "service": service_name
            }

            return date
        else:
            date = {
                "hostname": self.content['affected_entities'][0]['name'],
                "service": None
            }

            return date

    def appd_alert_status(self):
        open_alert = ['POLICY_OPEN_WARNING', 'POLICY_OPEN_CRITICAL', 'POLICY_CONTINUES_CRITICAL', 'POLICY_CONTINUES_WARNING']
        close_alert = ['POLICY_CLOSE_WARNING', 'POLICY_CLOSE_CRITICAL', 'POLICY_CANCELED_WARNING', 'POLICY_CANCELED_CRITICAL']
        other_alert = ['POLICY_UPGRADED', 'POLICY_DOWNGRADED']

        if self.content['event_type'] in open_alert:
            return 1
        elif self.content['event_type'] in close_alert:
            return 0
        else:
            return 1

    def severity_transformation(self):
        warning_severity = ['POLICY_OPEN_WARNING', 'POLICY_CONTINUES_WARNING', 'POLICY_CLOSE_WARNING', 'POLICY_CANCELED_WARNING']
        critical_severity = ['POLICY_OPEN_CRITICAL', 'POLICY_CONTINUES_CRITICAL', 'POLICY_CLOSE_CRITICAL', 'POLICY_CANCELED_CRITICAL']

        if self.content['event_type'] in warning_severity:
            severity = 'warning'
        elif self.content['event_type'] in critical_severity:
            severity = 'critical'
        else:
            severity = 'unknown'

        if self.appd_alert_status() == 0:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_procedure_id(self):
        try:
            if 'PR_ID' in self.content['health_rule_name']:
                procedure_id = self.content['health_rule_name'].split("]")[0].split(":")[1].replace(" ", "")

                return procedure_id

            if self.scenario_id:
                return self.scenario_id
        except Exception as err:
            log.error(
                msg=f"Can`t get procedure_id from AppD alert name: {self.content['health_rule_name']}. ERROR: {err}",
                extra={
                    "event_id": self.content['event_id']
                })

    def define_source(self):
        o = urllib.parse.urlsplit(self.content['deep_link_url'])
        source = f"{o.scheme}://{o.hostname}:{o.port}"

        return source

    def define_additional_urls(self):
        info_url = {"Details URL": self.content['deep_link_url']}

        return info_url

    def define_additional_fields(self):
        additional_fields = {}
        for single_entities in self.content['affected_entities']:
            for key, value in single_entities.items():
                if isinstance(value, str):
                    additional_fields[key] = str(value)

        return additional_fields

    def prepare_final_json(self):
        final_json = {
            "object_name": self.transform_appd_hostname()['hostname'],
            "alert_name": self.content['health_rule_name'],
            "notification_status": self.appd_alert_status(),
            "studio": self.environment_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "appdynamics",
            "service":  self.transform_appd_hostname()['service'],
            "notification_output": self.content['event_message'],
            "event_id": self.content['event_id'],
            "ms_alert_id": None,
            "graph_url": None,
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": {},
            "procedure_id": self.define_procedure_id(),
            "integration_key": self.integration_key
        }

        return final_json

    def process_event(self):
        result = None
        multi_events = self.content['full_events_list']
        self.scenario_id = self.content['scenario_id']
        self.environment_id = self.content['environment_id']
        self.integration_key = self.content['integration_key']

        for single_event in multi_events:
            self.content = single_event
            self.content['event_id'] = str(uuid.uuid4())
            prepare_result = self.prepare_final_json()

            result = push_to_kafka(prepare_result)

        return result
