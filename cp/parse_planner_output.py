def extract_tfd_plan(file: str):
    with open(file) as f:
        lines = f.readlines()
    
    plan_lines = []
    start_adding = False
    i = len(lines)-1

    all_plans = []
    while i > 0:
        if lines[i].lower().startswith('found new plan') or lines[i].lower().startswith('rescheduled plan'):
            plan_lines.reverse()
            all_plans.append(plan_lines)
            plan_lines = []
            start_adding = False
        else:
            if start_adding:
                plan_lines.append(lines[i])
            if lines[i].lower().startswith('solution with original makespan'):
                start_adding = True 
        i -= 1

    return all_plans

def extract_enhsp_plan(file: str):
    with open(file) as f:
        lines = f.readlines()
    
    plan_lines = []
    start_adding = False
    i = len(lines)-1

    all_plans = []
    all_costs = []

    cost = -1
    search_time = -1
    expansions = -1

    while i > 0:
        if lines[i].lower().startswith('found plan'):
            plan_lines.reverse()
            all_plans.append(plan_lines[:-1])
            all_costs.append(cost)
            plan_lines = []
            start_adding = False
        else:
            if start_adding:
                plan_lines.append(lines[i])
            if lines[i].lower().startswith('plan-length'):
                start_adding = True 
            
            if 'metric (search)' in lines[i].lower():
                cost = float(lines[i].split(':')[1].strip())

            if expansions == -1 and 'expanded nodes:' in lines[i].lower():
                try:
                    expansions = float(lines[i].lower().split('expanded nodes: ')[1].split(' ')[0])
                except:
                    pass

            if search_time == -1 and 'time: ' in lines[i].lower():
                search_time = float(lines[i].lower().split('time: ')[1].split(' ')[0][:-1])

        i -= 1

    return all_plans, all_costs, search_time, expansions

def extract_metricff_plan(file: str):
    with open(file) as f:
        lines = f.readlines()
    
    plan_lines = []
    start_adding = False
    i = len(lines)-1

    all_plans = []
    all_costs = []

    cost = -1
    search_time = -1

    while i > 0:
        if 'found legal plan' in lines[i].lower():
            plan_lines.reverse()
            all_plans.append(plan_lines[:-1])
            all_costs.append(cost)
            plan_lines = []
            start_adding = False
        else:
            if start_adding:
                plan_lines.append(lines[i])
            if lines[i].lower().startswith('plan cost'):
                cost = float(lines[i].split(':')[-1].strip())
                start_adding = True 
        
        if 'seconds searching' in lines[i].lower():
            search_time = float(lines[i].split('seconds')[0].strip())/1000
        
        i -= 1    

    return all_plans, all_costs, search_time

def extract_nfd_plan(file: str):
    
    with open(file) as f:
        lines = f.readlines()
    
    return lines[:-1]


