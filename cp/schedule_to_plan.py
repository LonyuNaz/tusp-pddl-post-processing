import os
import re
import json
import os
import networkx as nx
from plan import PartialPlan
from old.run_mzn import run_mzn
from old.mzn_arr_to_schedule import *
from objects import Service, Movement



def extract_info(plan_lines: list):
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
    for st, act in actions:
        if 'move' in act:
            num_moves += 1
        elif 'service ' in act:
            num_services += 1
        if num_services == 2:
            return num_moves


def make_new_schedule(pp, start_times):
    new_schedule = []
    for i in range(len(start_times)):
        st = start_times[i]
        action = pp.actions[i]
        new_schedule.append((st, action))
    new_schedule = sorted(new_schedule, key=lambda x: x[0])
    return new_schedule

def make_new_new_schedule(new_schedule):
    driver_loc = None
    new_new_schedule = []
    for i, (st, act) in enumerate(new_schedule):
        if type(act) is Movement:
            if driver_loc is None:
                new_new_schedule.append((st-2, f'(enter {act.train.name} {act.origin.name})'))
                driver_loc = act.train.name
            elif driver_loc != act.train.name:
                prev_time, prev_act = new_schedule[i-1]
                if type(prev_act) is Movement:
                    prev_time += 1
                    loc = prev_act.destination.name
                elif type(prev_act) is Service:
                    loc = prev_act.track.name
                new_new_schedule.append((prev_time, f'(exit {prev_act.train.name} {loc})'))
                new_new_schedule.append((st-2, f'(enter {act.train.name} {act.origin.name})'))
                driver_loc = act.train.name
        new_new_schedule.append((st, f'{act.compact_str()})'))


    return new_new_schedule

    