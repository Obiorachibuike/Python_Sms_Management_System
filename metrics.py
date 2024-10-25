from prometheus_client import Counter, start_http_server
import threading

class Metrics:
    _instance = None  # Class variable to hold the singleton instance

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(Metrics, cls).__new__(cls)
            cls._instance.init_metrics(*args, **kwargs)  # Initialize metrics only once
        return cls._instance

    def init_metrics(self, port=9091):
        self.sms_sent_counter = Counter('sms_sent_total', 'Total number of SMS sent')
        self.sms_failure_counter = Counter('sms_failure_total', 'Total number of failed SMS')
        self.sms_success_rate = Counter('sms_success_rate', 'SMS success rate')
        self.start_metrics_server(port)

    def start_metrics_server(self, port):
        """Start the Prometheus metrics server on a separate thread to avoid blocking."""
        thread = threading.Thread(target=start_http_server, args=(port,))
        thread.daemon = True  # This ensures the thread will exit when the main program does
        thread.start()

    def record_sms_sent(self):
        self.sms_sent_counter.inc()

    def record_failure(self):
        self.sms_failure_counter.inc()

    def record_success_rate(self, rate):
        self.sms_success_rate.inc(rate)

# Example usage
# metrics = Metrics()  # Create a metrics instance
# metrics.record_sms_sent()
