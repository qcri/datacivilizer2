import operator
from dc import *

def customOp(metric, constant1, constant2):
    val = metric.getValue()
    return constant1 < val and constant2 > val

def main():
    metric1 = DCMetric("m1")
    metric2 = DCMetric("m2", 2, 3)
    metric3 = DCMetric("m3")
    DC.register_metric(metric1)
    DC.register_metric(metric2)
    DC.register_metric(metric3)
    bp1 = DCBreakpoint('<', metric1, metric2)
    DC.register_breakpoint(bp1)
    DC.register_breakpoint(operator.ge, metric3, 5)
    bp2 = DCBreakpoint(customOp, metric3, 2, 4)
    DC.register_breakpoint(bp2)
    metric1.setValue(1)
    metric3.setValue(3)
    print(DC.evaluate_breakpoints())
    print(bp1)
    print(bp2)

if __name__ == '__main__':
    main()