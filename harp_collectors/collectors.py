from harp_collectors.plugins.icinga_plugin import IcingaProcessor
from harp_collectors.plugins.zabbix_plugin import ZabbixProcessor
from harp_collectors.plugins.appdynamics_plugin import AppDynamicsProcessor
from harp_collectors.plugins.nagios_plugin import NagiosProcessor
from harp_collectors.plugins.api_plugin import ApiProcessor
from harp_collectors.plugins.cloudwatch_plugin import CloudwatchProcessor
from harp_collectors.plugins.crashlytics_plugin import CrashlyticsProcessor
from harp_collectors.plugins.grafana_plugin import GrafanaProcessor
from harp_collectors.plugins.email_plugin import EmailProcessor
from harp_collectors.plugins.prometheus_plugin import PrometheusProcessor
from harp_collectors.plugins.anodot_plugin import AnodotProcessor
from harp_collectors.plugins.newrelic_plugin import NewRelicProcessor
from harp_collectors.plugins.pagerduty_plugin import PagerDutyProcessor
from harp_collectors.plugins.atatus_plugin import AtatusProcessor
from harp_collectors.plugins.pingdom_plugin import PingdomProcessor
from harp_collectors.plugins.dynatrace_plugin import DynatraceProcessor
from harp_collectors.plugins.prtg_plugin import PRTGProcessor
from harp_collectors.plugins.gcp_plugin import GCProcessor
from logger.logging import service_logger

log = service_logger()


class ReceiveEvent(object):
    def __init__(self, content, ms):
        self.content = content
        self.ms = ms

    def process_icinga(self):
        event = IcingaProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_zabbix(self):
        event = ZabbixProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_appdynamics(self):
        event = AppDynamicsProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_nagios(self):
        event = NagiosProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_api(self):
        event = ApiProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_cloudwatch(self):
        event = CloudwatchProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_crashlytics(self):
        event = CrashlyticsProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_grafana(self):
        event = GrafanaProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_email(self):
        event = EmailProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_prometheus(self):
        event = PrometheusProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_anodot(self):
        event = AnodotProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_newrelic(self):
        event = NewRelicProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_pagerduty(self):
        event = PagerDutyProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_atatus(self):
        event = AtatusProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_pingdom(self):
        event = PingdomProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_dynatrace(self):
        event = DynatraceProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_prtg(self):
        event = PRTGProcessor(content=self.content)
        result = event.process_event()

        return result

    def process_gcp(self):
        event = GCProcessor(content=self.content)
        result = event.process_event()

        return result

    def processor(self):
        if self.ms == 'icinga':
            return self.process_icinga()
        elif self.ms == 'zabbix':
            return self.process_zabbix()
        elif self.ms == 'appdynamics':
            return self.process_appdynamics()
        elif self.ms == 'nagios':
            return self.process_nagios()
        elif self.ms == 'api':
            return self.process_api()
        elif self.ms == 'cloudwatch':
            return self.process_cloudwatch()
        elif self.ms == 'crashlytics':
            return self.process_crashlytics()
        elif self.ms == 'grafana':
            return self.process_grafana()
        elif self.ms == 'email':
            return self.process_email()
        elif self.ms == 'prometheus':
            return self.process_prometheus()
        elif self.ms == 'anodot':
            return self.process_anodot()
        elif self.ms == 'newrelic':
            return self.process_newrelic()
        elif self.ms == 'pagerduty':
            return self.process_pagerduty()
        elif self.ms == 'atatus':
            return self.process_atatus()
        elif self.ms == 'pingdom':
            return self.process_pingdom()
        elif self.ms == 'dynatrace':
            return self.process_dynatrace()
        elif self.ms == 'prtg':
            return self.process_prtg()
        elif self.ms == 'gcp':
            return self.process_gcp()
