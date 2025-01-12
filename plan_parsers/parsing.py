from enum import Enum
from dataclasses import dataclass
from typing import List
import pandas as pd
import re
import inspect

class FindOperator(Enum):
    CONTAINS = 1
    STARTSWITH = 2

@dataclass
class Indicator:
    find_operator: FindOperator
    text: str

class PlannerOutput:

    def __init__(self):
        self.plans: List[ParsedPlan] = []
    
    def show_stats(self):
        stats_dict = dict()
        for i, p in enumerate(self.plans):
            stats_dict[i] =  dict()
            attributes = inspect.getmembers(p, lambda a:not(inspect.isroutine(a)))
            attributes = [a for a in attributes if '__' not in a[0]]
            for k, v in attributes:
                if k == 'lines':
                    k = 'plan length'
                    v = len(v)
                stats_dict[i][k] = v
        return pd.DataFrame(stats_dict).T


class ParsedPlan:
    
    def __init__(self):
        self.lines = []
        self.cost = -1
        self.expansions = -1
        self.searchtime = -1       
    
        
        


NUMBER_REGEX = "[-+]?[.]?[\d]+(?:,\d\d\d)*[\.]?\d*(?:[eE][-+]?\d+)?"

def matches_indicator(line: str, ind: Indicator):
    line = line.lower()
    if ind.find_operator == FindOperator.CONTAINS:
        if ind.text.lower() in line.lower():
            return True
    elif ind.find_operator == FindOperator.STARTSWITH:
        if line.lower().startswith(ind.text.lower()):
            return True
    return False

def parse_planner_file(filepath: str, 
               start_indicator: Indicator, 
               end_indicator: Indicator, 
               cost_indicator: Indicator = None,
               expansion_indicator: Indicator = None,
               searchtime_indicator: Indicator = None):
    
    with open(filepath) as f:
        lines = f.readlines()
    lines.reverse()
    
    reading_plan = False
    i = 0
    out = PlannerOutput()
    current_plan = ParsedPlan()

    while len(lines) > 0:
        line = lines.pop(0).strip().replace('\n','')
        if len(line) == 0:
            continue
        if cost_indicator and matches_indicator(line, cost_indicator):
            current_plan.cost = float(re.findall(NUMBER_REGEX, line)[-1])
        if expansion_indicator and matches_indicator(line, expansion_indicator):
            current_plan.expansions = float(re.findall(NUMBER_REGEX, line)[-1])
        if searchtime_indicator and matches_indicator(line, searchtime_indicator):
            current_plan.searchtime = float(re.findall(NUMBER_REGEX, line)[-1])
        if not reading_plan:
            if end_indicator and matches_indicator(line, end_indicator):
                if len(current_plan.lines) > 0:
                    out.plans.append(current_plan)
                    current_plan = ParsedPlan()
                reading_plan = True
        elif reading_plan:
            if start_indicator and matches_indicator(line, start_indicator):
                reading_plan = False
                current_plan.lines.reverse()
            else:
                if all(x not in line.lower() for x in ['move', 'service', 'walk', 'enter', 'park', 'exit', 'turn']):
                    continue
                current_plan.lines.append(line)
    
    if len(current_plan.lines) > 0:
        out.plans.append(current_plan)

    return out
    




    
