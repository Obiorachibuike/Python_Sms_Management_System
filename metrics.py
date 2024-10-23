class Metrics:
    def __init__(self):
        self.metrics_data = {}

    def update_metrics(self, country_operator, success):
        if country_operator not in self.metrics_data:
            self.metrics_data[country_operator] = {'success': 0, 'failure': 0}
        if success:
            self.metrics_data[country_operator]['success'] += 1
        else:
            self.metrics_data[country_operator]['failure'] += 1

    def get_metrics(self):
        return self.metrics_data
