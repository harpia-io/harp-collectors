import requests
from logger.logging import service_logger
from harp_collectors.plugins.kafka_client import push_to_kafka
import harp_collectors.settings as settings
import uuid

log = service_logger()


class NagiosProcessor(object):
    def __init__(self, content):
        self.content = content
        self.ms_unique_data = {}
        self.event_id = None

    def nagios_alert_status(self, alert_status):
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
                      extra={"monitoring_system": "nagios",
                             "event_name": "nagios_alert_status",
                             "event_id": self.event_id})

    def prepare_details_url(self):
        if self.content['PROBLEMTYPE'] == 'service_level':
            service = requests.utils.quote(self.content['SERVICEDESC'])
            url = f"http://{self.content['NAGIOSSERVER']}/nagios/cgi-bin/extinfo.cgi?type=2&host={self.content['HOSTNAME']}&service={service}"
        else:
            url = f"http://{self.content['NAGIOSSERVER']}/nagios/cgi-bin/extinfo.cgi?type=2&host={self.content['HOSTNAME']}"

        return url

    def additional_urls(self):
        info_url = {
            "Details URL": self.prepare_details_url()
        }

        return info_url

    def notification_output(self):
        if self.content['PROBLEMTYPE'] == 'service_level':
            return self.content['SERVICEOUTPUT']
        else:
            return self.content['HOSTOUTPUT']

    def unique_data(self):
        self.ms_unique_data['service_role'] = self.content['HOSTROLE']

    def graph_url(self):
        if self.content['SERVICEGRAPH']:
            return self.content['SERVICEGRAPH']

    def severity_to_id(self):
        try:
            if 'SEVERITY' in self.content:
                if self.content['SEVERITY'] != '' or self.content['SEVERITY'] != '$':
                    return settings.SEVERITY_MAPPING[self.content['SEVERITY'].lower()]
        except Exception:
            pass

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
        if self.content['PROBLEMTYPE'] == 'service_level':
            return self.content['SERVICEDESC']
        else:
            return 'Host Unreachable'

    def define_studio(self):
        return self.content['environment_id']

    def define_procedure_id(self):
        return self.content['scenario_id']

    def prepare_final_json(self):
        final_json = {
            "object_name": self.content['HOSTNAME'],
            "alert_name": self.event_name(),
            "notification_status": self.nagios_alert_status(self.content['NOTIFICATIONTYPE'].lower()),
            "studio": self.define_studio(),
            "severity": self.severity_to_id(),
            "source": self.content['NAGIOSSERVER'],
            "monitoring_system": "nagios",
            "service": None,
            "notification_output": self.notification_output(),
            "event_id": self.event_id,
            "ms_alert_id": None,
            "graph_url": self.graph_url(),
            "ms_unique_data": {
                "nagios": self.ms_unique_data
            },
            "additional_urls": self.additional_urls(),
            "additional_fields": {},
            "actions": {},
            "procedure_id": self.define_procedure_id(),
            "integration_key": self.content['integration_key']
        }

        return final_json

    def process_event(self):
        self.event_id = str(uuid.uuid4())
        return push_to_kafka(self.prepare_final_json())
