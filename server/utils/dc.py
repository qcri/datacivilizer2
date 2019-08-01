import json
import operator

class DC(object):
    metrics = []
    breakpoints = []
    bp_values = []

    @classmethod
    def register_metric(cls, metric):
        cls.metrics.append(metric)

    @classmethod
    def register_breakpoint(cls, *args):
        if len(args) == 1:
            cls.breakpoints.append(args[0])
        else:
            cls.breakpoints.append(DCBreakpoint(*args))

    @classmethod
    def evaluate_breakpoints(cls):
        cls.bp_values = []
        for bp in cls.breakpoints:
            cls.bp_values.append(bp.evaluate())
        return cls.bp_values

    @classmethod
    def save_metrics_and_bp(cls, file_name):
        data = {'metrics': {}, 'breakpoints': {}}
        for metric in cls.metrics:
            data['metrics'][metric.name] = metric.evaluate()
        for bp in cls.breakpoints:
            data['breakpoints'][str(bp)] = bp.evaluate()
        with open(file_name, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    @classmethod
    def end(cls, file_name):
        cls.save_metrics_and_bp(file_name)

class DCMetric:

    def __init__(self, metric_name, *values):
        self.name = str(metric_name)
        self.values = list(values)

    def setValue(self, value):
        self.values.append(value)

    def getValues(self):
        return self.values

    def getValue(self):
        if len(self.values) == 0:
            return None
        return self.values[-1]

    def evaluate(self):
        return self.getValue()

    def __repr__(self):
        return self.name + "(" + str(self.evaluate()) + ")"

    def __str__(self):
        return self.__repr__()

class DCBreakpoint:

    ops = {"<": operator.lt, "<=": operator.le, "==": operator.eq, "!=": operator.ne, ">=": operator.ge, ">": operator.gt}
    opStrings = {operator.lt: "<", operator.le: "<=", operator.eq: "==", operator.ne: "!=", operator.ge: ">=", operator.gt: ">"}

    def __init__(self, op, *args):
        self.operator = op
        self.args = list(args)

    def getOpString(self):
        if isinstance(self.operator, str):
            return self.operator
        else:
            return self.opStrings[self.operator]

    def getArgValue(self, arg):
        if type(arg) is DCMetric:
            return arg.evaluate()
        else:
            return arg

    def evaluate(self):
        if isinstance(self.operator, str):
            op = self.ops[self.operator]
            return op(*map(self.getArgValue,self.args))
        elif self.operator in self.opStrings:
            return self.operator(*map(self.getArgValue,self.args))
        else:
            return self.operator(*self.args)

    def __repr__(self):
        if isinstance(self.operator, str) or self.operator in self.opStrings:
            return str(self.args[0]) + " " + self.getOpString() + " " + str(self.args[1])
        else:
            return self.operator.__name__ + "(" + ','.join(str(arg) for arg in self.args) + ")"

    def __str__(self):
        return self.__repr__()

class BpOps:

    @staticmethod
    def always_lt(metric, const):
        values = metric.getValues()
        for val in values:
            if val >= const:
                return False
        return True

    @staticmethod
    def always_le(metric, const):
        values = metric.getValues()
        for val in values:
            if val > const:
                return False
        return True

    @staticmethod
    def always_eq(metric, const):
        values = metric.getValues()
        for val in values:
            if val != const:
                return False
        return True

    @staticmethod
    def always_ne(metric, const):
        values = metric.getValues()
        for val in values:
            if val == const:
                return False
        return True

    @staticmethod
    def always_ge(metric, const):
        values = metric.getValues()
        for val in values:
            if val < const:
                return False
        return True

    @staticmethod
    def always_gt(metric, const):
        values = metric.getValues()
        for val in values:
            if val <= const:
                return False
        return True
