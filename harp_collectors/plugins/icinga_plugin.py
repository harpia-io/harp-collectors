import requests
from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid

log = service_logger()


class IcingaProcessor(object):
    def __init__(self, content):
        self.content = content
        self.ms_unique_data = {}
        self.event_id = None

    def icinga_alert_status(self):
        alert_status = self.content['NOTIFICATIONTYPE'].lower()

        if alert_status == 'problem':
            return 1
        elif alert_status == 'recovery':
            return 0
        elif alert_status == 'acknowledgement':
            self.ms_unique_data['notification_author'] = self.content['NOTIFICATIONAUTHORNAME']
            self.ms_unique_data['notification_comment'] = self.content['NOTIFICATIONCOMMENT']
            return 10
        elif alert_status == 'flappingstart':
            return 0
        elif alert_status == 'flappingstop':
            return 0
        elif alert_status == 'downtimeend':
            return 0
        elif alert_status == 'downtimestart':
            return 0
        elif alert_status == 'downtimeremoved':
            return 1
        else:
            log.error(msg=f"Notification status is unknown. Content: {self.content}",
                      extra={"monitoring_system": "icinga",
                             "event_name": "decorated_icinga_alert_status",
                             "event_id": self.event_id})

    def prepare_details_url(self):
        if self.content['PROBLEMTYPE'] == 'service_level':
            service = requests.utils.quote(self.content['SERVICENAME'])
            url = f"http://{self.content['ICINGASERVER']}/icingaweb2/monitoring/service/show?host={self.content['HOSTNAME']}&service={service}"
        else:
            url = f"http://{self.content['ICINGASERVER']}/icingaweb2/monitoring/host/show?host={self.content['HOSTNAME']}"

        return url

    def additional_urls(self):
        info_url = {
            "Details URL": self.prepare_details_url()
        }

        return info_url

    def prepare_action_url(self):
        if self.content['PROBLEMTYPE'] == 'service_level':
            action_url = {
                "Icinga Recheck": "icinga_recheck"
            }
            return action_url
        else:
            return {}

    def notification_output(self):
        if self.content['PROBLEMTYPE'] == 'service_level' or self.content['PROBLEMTYPE'] == 'Service':
            return self.content['SERVICEOUTPUT']
        else:
            return self.content['HOSTOUTPUT']

    def unique_data(self):
        self.ms_unique_data['service_role'] = self.content['HOSTROLE']

    def graph_url(self):
        if self.content['SERVICEGRAPH']:
            return self.content['SERVICEGRAPH']

        if 'SERVICENOTESURL' in self.content:
            if 'http' in self.content['SERVICENOTESURL']:
                return self.content['SERVICENOTESURL']

    def severity_to_name(self):
        if self.content['SEVERITY'] == 2112:
            return 'unknown'

    def severity_to_id(self):
        if 'SEVERITY' in self.content:
            if self.content['SEVERITY'] != '':
                return settings.SEVERITY_MAPPING[self.severity_to_name()]

        if 'SERVICESTATE' in self.content:
            severity = settings.SEVERITY_MAPPING[self.content['SERVICESTATE'].lower()]
        elif 'HOSTSTATE' in self.content:
            if self.content['HOSTSTATE'].lower() == 'up':
                self.content['HOSTSTATE'] = 'ok'
            severity = settings.SEVERITY_MAPPING[self.content['HOSTSTATE'].lower()]
        else:
            log.error(msg=f"SERVICESTATE or HOSTSTATE are not present in incoming message: {self.content}")
            raise Exception(f"SERVICESTATE or HOSTSTATE are not present in incoming message: {self.content}")

        return severity

    def event_name(self):
        if 'SERVICESTATE' in self.content:
            return self.content['SERVICENAME']
        else:
            return "Host Unreachable"

    def define_studio(self):
        return self.content['environment_id']

    def define_procedure_id(self):
        return self.content['scenario_id']

    def define_object_name(self):
        return self.content['HOSTNAME']

    def define_source(self):
        return self.content['ICINGASERVER']

    def define_service(self):
        return self.content['HOSTSERVICE']

    def prepare_final_json(self):
        final_json = {
            "object_name": self.define_object_name(),
            "alert_name": self.event_name(),
            "notification_status": self.icinga_alert_status(),
            "studio": self.define_studio(),
            "severity": self.severity_to_id(),
            "source": self.define_source(),
            "monitoring_system": "icinga",
            "service": self.define_service(),
            "notification_output": self.notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.graph_url(),
            "ms_unique_data": {
                "icinga": self.ms_unique_data
            },
            "additional_urls": self.additional_urls(),
            "additional_fields": {},
            "actions": self.prepare_action_url(),
            "procedure_id": self.define_procedure_id(),
            "integration_key": self.content['integration_key']
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
