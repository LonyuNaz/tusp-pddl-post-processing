import os
import re

def extract_tfd_plan(file: str):
    with open(file) as f:
        lines = f.readlines()
    
    plan_lines = []
    start_adding = False
    i = len(lines)-1

    all_plans = []
    while i > 0:
        if lines[i].lower().startswith('found new plan'):
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
    while i > 0:
        if lines[i].lower().startswith('found plan'):
            plan_lines.reverse()
            all_plans.append(plan_lines[:-1])
            plan_lines = []
            start_adding = False
        else:
            if start_adding:
                plan_lines.append(lines[i])
            if lines[i].lower().startswith('plan-length'):
                start_adding = True 
        i -= 1

    return all_plans

def extract_tfd_info(plan_lines: list):
    actions = []
    trains = []
    tracks = []
    for line in plan_lines:
        trains += re.findall('train_\w+', line)
        tracks += re.findall('track_\w+', line)
        parsed_line = line.split('(')[1].split(')')[0]
        parts = parsed_line.split(' ')
        actions.append((parts[0], parts[1:]))

    return actions, set(trains), set(tracks)

def count_useless_turns(actions: list, trains: set):
    turns = 0
    counter = 0
    for train in trains:
        act_train = [act[0] for act in actions if train in act[1]]
        for i in range(len(act_train)-1):
            if act_train[i].startswith('turn') and not act_train[i+1].startswith('move'):
                counter += 1
            if act_train[i].startswith('turn'):
                turns += 1
        if act_train[-1].startswith('turn'):
            counter += 1
            turns += 1
    return counter, turns

def count_useless_enters(actions: list, trains: set):
    enters = 0
    counter = 0
    for train in trains:
        act_train = [act[0] for act in actions if train in act[1]]
        for i in range(len(act_train)-1):
            if 'enter' in act_train[i] and not act_train[i+1].startswith('move'):
                counter += 1
            if 'enter' in  act_train[i]:
                enters += 1
        if 'enter' in  act_train[-1]:
            counter += 1
            enters += 1
    return counter, enters

def count_moves_until_2nd_service(actions: list):
    num_services = 0
    num_moves = 0
    for act, args in actions:
        if 'move' in act:
            num_moves += 1
        elif 'service' in act:
            num_services += 1
        if num_services == 2:
            return num_moves


    