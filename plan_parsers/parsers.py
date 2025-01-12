from parsing import parse_planner_file, ParsedPlan, PlannerOutput, Indicator, FindOperator

def parse_enhsp_file(filename: str):
    start_ind = Indicator(FindOperator.STARTSWITH, 'found plan')
    end_ind = Indicator(FindOperator.STARTSWITH, 'plan-length')
    cost_ind = Indicator(FindOperator.CONTAINS, 'metric (search)')
    exp_ind = Indicator(FindOperator.CONTAINS, 'expanded nodes:')
    st_ind = Indicator(FindOperator.CONTAINS, 'search time (msec)')
    return parse_planner_file(filename, start_ind, end_ind, cost_ind, exp_ind, st_ind)

def parse_metricff_file(filename: str):
    start_ind = Indicator(FindOperator.CONTAINS, 'found legal plan')
    end_ind = Indicator(FindOperator.STARTSWITH, 'plan cost')
    cost_ind = Indicator(FindOperator.STARTSWITH, 'plan cost')
    st_ind = Indicator(FindOperator.CONTAINS, 'seconds total time')
    return parse_planner_file(filename, start_ind, end_ind, cost_ind, None, st_ind)

def parse_nfd_file(filename: str):
    start_ind = Indicator(FindOperator.CONTAINS, '???????')
    end_ind = Indicator(FindOperator.CONTAINS, 'cost')
    cost_ind = Indicator(FindOperator.CONTAINS, 'cost')
    return parse_planner_file(filename, start_ind, end_ind, cost_ind, None, None)

def parse_optic_file(filename: str):
    start_ind = Indicator(FindOperator.CONTAINS, '; time')
    end_ind = Indicator(FindOperator.CONTAINS, 'all goal deadlines')
    cost_ind = Indicator(FindOperator.CONTAINS, 'plan found with metric')
    st_ind = Indicator(FindOperator.CONTAINS, 'time')
    return parse_planner_file(filename, start_ind, end_ind, cost_ind, None, st_ind)

def parse_tfd_file(filename: str):
    start_ind = Indicator(FindOperator.STARTSWITH, 'found new plan')
    end_ind = Indicator(FindOperator.STARTSWITH, 'init')
    cost_ind = Indicator(FindOperator.STARTSWITH, 'makespan   :')
    exp_ind = Indicator(FindOperator.CONTAINS, 'expanded')
    st_ind = Indicator(FindOperator.STARTSWITH, 'search time')
    return parse_planner_file(filename, start_ind, end_ind, cost_ind, exp_ind, st_ind)
