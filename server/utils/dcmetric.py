import json

class DC(object):
    metrics = []

    @classmethod
    def register_metric(cls, metric):
        cls.metrics.append(metric)

    @classmethod
    def save_metrics(cls, file_name):
        data = {}
        for metric in cls.metrics:
            data[metric.name] = metric.getValue()
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

class DCMetric:

    def __init__(self, metric_name):
        self.name = str(metric_name)
        self.values = []

    def setValue(self, value):
        self.values.append(value)

    def getValue(self):
        if len(self.values) == 0:
            return None
        return self.values[-1]