import traceback
from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
from urllib.parse import urlparse
import urllib.parse

log = service_logger()


class DynatraceProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content:
            return self.content['graph_url']

    def define_additional_urls(self):
        try:
            dynatrace_local_dns_netloc = urlparse(self.content['ProblemURL']).netloc
            dynatrace_local_dns_schema = urlparse(self.content['ProblemURL']).scheme
            dynatrace_external_dns_netloc = urlparse(self.content['ProblemURL']).netloc
            problem_url = self.content['ProblemURL'].replace('http://', dynatrace_local_dns_schema).replace(dynatrace_external_dns_netloc, dynatrace_local_dns_netloc)
            info_url = {"Investigation URL": problem_url}
        except Exception as err:
            log.warning(msg=f"Can`t parse ProblemURL. Probably format is not correct - {self.content}\nError: {err}\nTrace: {traceback.format_exc()}")
            info_url = {}

        return info_url

    def define_additional_fields(self):
        additional_fields = {}
        if isinstance(self.content['Tags'], dict):
            additional_fields.update(self.content['Tags'])

        return additional_fields

    def define_notification_status(self):
        if self.content['State'] == 'OPEN':
            return 1
        if self.content['State'] == 'MERGED':
            return 1
        elif self.content['State'] == 'RESOLVED':
            return 0
        else:
            log.error(
                msg=f"Unknown Dynatrace state: {self.content['state']}. Currently integration support only OPEN, RESOLVED and MERGED States",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if self.content['State'] == 'OPEN':
            severity = 'critical'
        elif self.content['State'] == 'MERGED':
            severity = 'critical'
        else:
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    @staticmethod
    def define_object_name():
        object_name = 'dynatrace'

        return object_name

    def define_service_name(self):
        return self.content['ProblemImpact']

    def define_notification_output(self):
        return self.content['ProblemDetailsText']

    def define_studio(self):
        return self.content['environment_id']

    def define_source(self):
        o = urllib.parse.urlsplit(self.content['ProblemURL'])
        source = f"{o.scheme}://{o.hostname}"

        return source

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self):
        return self.content['scenario_id']

    def define_alert_name(self):
        full_name = f"Problem {self.content['ProblemID']}: {self.content['ProblemTitle']}"

        return full_name

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": self.define_studio(),
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "dynatrace",
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
