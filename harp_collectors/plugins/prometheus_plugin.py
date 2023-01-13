from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid
import ujson as json
from urllib.parse import urlparse

log = service_logger()


class PrometheusProcessor(object):
    def __init__(self, content):
        self.content = content
        self.event_id = None

    def define_graph_url(self):
        if 'graph_url' in self.content['labels']:
            return self.content['labels']['graph_url']

    def define_additional_urls(self):
        info_url = {"Prometheus Graph": self.content['generatorURL'].replace("tab=1", "tab=0")}

        if 'dashboard_url' in self.content['labels']:
            info_url['Grafana Dashboard'] = self.content['labels']['dashboard_url']

        if 'alert_url' in self.content['labels']:
            info_url['Prometheus Alert'] = self.content['labels']['alert_url']

        if 'runbook_url' in self.content['annotations']:
            info_url['Runbook URL'] = self.content['annotations']['runbook_url']

        return info_url

    def define_additional_fields(self):
        labels_to_ignore = ['alertname', 'pod']
        info_url = {}

        for key, value in self.content['labels'].items():
            if key not in labels_to_ignore:
                info_url[key] = str(value)

        return info_url

    def define_notification_status(self):
        if self.content['status'] == 'firing':
            return 1
        elif self.content['status'] == 'resolved':
            return 0
        else:
            log.error(
                msg=f"Unknown Prometheus status: {self.content['status']}. Currently integration support only ok and alerting",
                extra={"event_id": self.event_id}
            )

    def severity_transformation(self):
        if 'severity' in self.content['labels']:
            if self.content['labels']['severity'] == 'warning':
                severity = 'warning'
            elif self.content['labels']['severity'] == 'critical':
                severity = 'critical'
            elif self.content['labels']['severity'] == 'urgent':
                severity = 'urgent'
            elif self.content['labels']['severity'] == 'info':
                severity = 'information'
            else:
                severity = 'unknown'
        else:
            if self.content['status'] == 'firing':
                severity = 'critical'
            else:
                severity = 'ok'

        if self.content['status'] == 'resolved':
            severity = 'ok'

        severity_id = settings.SEVERITY_MAPPING[severity]

        return severity_id

    def define_object_name(self):
        object_name = f"AlertID:{self.content['fingerprint']}"

        return object_name

    def define_service_name(self):
        if 'service' in self.content['labels']:
            return self.content['labels']['service']
        else:
            return 'not_defined'

    def define_notification_output(self):
        if 'description' in self.content['annotations']:
            return f'Description: {self.content["annotations"]["description"]}'

        if self.content['annotations']:
            metrics_list = []
            for metric, value in self.content['annotations'].items():
                metrics_list.append(f'{metric}: {value}')

            return '\n'.join(metrics_list)
        else:
            return f"Value: {self.content['annotations']}"

    def define_studio(self):
        return json.loads(self.content['message'].split(":::")[-1])['studio_id']

    def define_source(self):
        o = urlparse(self.content['generatorURL'])
        return o.netloc

    @staticmethod
    def define_actions():
        return {}

    def define_procedure_id(self, procedure_id):
        if 'procedure_id' in self.content['labels']:
            return self.content['labels']['procedure_id']
        else:
            return procedure_id

    def define_alert_name(self):
        full_name = self.content['labels']['alertname']

        return full_name

    def prepare_final_json(self, procedure_id, studio_id, integration_key):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.define_alert_name(),
            "notification_status": self.define_notification_status(),
            "studio": studio_id,
            "severity": self.severity_transformation(),
            "source": self.define_source(),
            "monitoring_system": "prometheus",
            "service": self.define_service_name(),
            "notification_output": self.define_notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.define_graph_url(),
            "ms_unique_data": {},
            "additional_urls": self.define_additional_urls(),
            "additional_fields": self.define_additional_fields(),
            "actions": self.define_actions(),
            "procedure_id": self.define_procedure_id(procedure_id),
            "integration_key": integration_key
        }

        return final_json

    def process_event(self):
        result = None
        procedure_id = self.content['procedure_id']
        event_id = self.content['event_id']
        studio_id = self.content['studio_id']
        integration_key = self.content['integration_key']
        multi_events = self.content['alerts']
        for single_event in multi_events:
            if single_event['labels']['alertname'] == "Watchdog":
                # Skip Watchdog alerts
                continue

            self.content = single_event
            if event_id is None:
                self.event_id = str(uuid.uuid4())
            else:
                self.event_id = event_id
            try:
                result = push_to_kafka(
                    event_body=self.prepare_final_json(procedure_id=procedure_id, studio_id=studio_id, integration_key=integration_key),
                    event_id=self.event_id
                )
                # log.debug(
                #     msg=f"Prometheus result was pushed to Kafka - {result}",
                #     extra={'tags': {'event_id': event_id}}
                # )
            except Exception as err:
                log.error(
                    msg=f"Cannot pusu Prometheus result to Kafka - {err}",
                    extra={'tags': {'event_id': event_id}}
                )

        return result
