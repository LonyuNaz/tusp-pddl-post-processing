
import re
import os
import json
import numpy as np
import networkx as nx

from typing import List, Union
from objects import Driver, Track, Train, Movement, Enter, Exit, Service, Direction, Switch

class PartialPlan:

    def __init__(self, lines: List[str]):
        self.actions = list()
        self.trains = list()
        self.tracks = list()
        self.drivers = list()
        self.switches = list()
        
        self.plan_lines = [re.findall(r'\(.*\)', line)[0][1:-1] 
                        for line in lines 
                        if any(x in line for x in ('track', 'train', 'driver'))]
        
        self._extract_objects()
        self._extract_actions()

    def _add_train(self, name: str):
        if all(t.name != name for t in self.trains):
            self.trains.append(Train(len(self.trains)+1, name))

    def _add_track(self, name: str):
        if all(t.name != name for t in self.tracks):
            self.tracks.append(Track(len(self.tracks)+1, name))

    def _add_driver(self, name: str):
        if all(d.name != name for d in self.drivers):
            self.drivers.append(Driver(len(self.drivers)+1, name))
    
    def _extract_objects(self):
        trains = list()
        tracks = list()
        drivers = list()
        for line in self.plan_lines:
            for element in line.split(' '):
                if element.startswith('train_'):
                    trains.append(element)
                elif element.startswith('track_'):
                    tracks.append(element)
                elif element.startswith('driver_'):
                    drivers.append(element)
        for t in trains:
            self._add_train(t)
        for t in tracks:
            self._add_track(t)
        for d in drivers:
            self._add_driver(d)

    def get_train(self, name: str) -> Train:
        return next(t for t in self.trains if t.name == name)

    def get_track(self, name: str) -> Track:
        return next(t for t in self.tracks if t.name == name)
    
    def find_track(self, name: str) -> Track:
        for track in self.tracks:
            if f'track_{name}' == track.name or f'track_{name}_service' == track.name:
                return track    
        return


    def get_driver(self, name: str) -> Driver:
        return next(t for t in self.drivers if t.name == name)      

    def _extract_actions(self):
        self.actions = list()
        for line in self.plan_lines:
            if line.startswith('enter_and_move'):
                direction = Direction.ASIDE if 'aside' in line else Direction.BSIDE
                t_name = re.findall(r'train_\w+', line)[0]
                # d_name = re.findall(r'driver_\w+', line)[0]
                train = self.get_train(t_name)
                # driver = self.get_driver(d_name)
                # self.actions.append(Enter(self.count_enters(), driver, train))
                [t_from_name, t_to_name] = re.findall(r'track_\w+', line)
                track_from = self.get_track(t_from_name)
                track_to = self.get_track(t_to_name)
                self.actions.append(Movement(len(self.actions)+1, train, direction, track_from, track_to))
            elif line.startswith('move'):
                direction = Direction.ASIDE if 'aside' in line else Direction.BSIDE
                t_name = re.findall(r'train_\w+', line)[0]
                train = self.get_train(t_name)
                [t_from_name, t_to_name] = re.findall(r'track_\w+', line)
                track_from = self.get_track(t_from_name)
                track_to = self.get_track(t_to_name)
                self.actions.append(Movement(len(self.actions)+1, train, direction, track_from, track_to))
            elif line.startswith('walk_and_enter_and_move'):
                direction = Direction.ASIDE if 'aside' in line else Direction.BSIDE
                t_name = re.findall(r'train_\w+', line)[0]
                train = self.get_train(t_name)
                [_, t_from_name, t_to_name] = re.findall(r'track_\w+', line)
                track_from = self.get_track(t_from_name)
                track_to = self.get_track(t_to_name)
                self.actions.append(Movement(len(self.actions)+1, train, direction, track_from, track_to))
            # elif line.startswith('exit'):
            #     d_name = re.findall(r'driver_\w+', line)[0]
            #     train = self.get_train(t_name)
            #     self.actions.append(Exit(self.count_exits(), driver, train))
            elif line.startswith('service'):
                t_name = re.findall(r'train_\w+', line)[0]
                train = self.get_train(t_name)
                tr_name = re.findall(r'track_\w+', line)[0]
                track = self.get_track(tr_name)
                self.actions.append(Service(len(self.actions)+1, train, track))
            # else:
            #     raise Exception(f'Exception! {line}')


    def finalize(self):

        self.switches = []

        connections = []
        for i, movement in enumerate(self.actions):
            if type(movement) is not Movement:
                continue
            if movement.direction == Direction.ASIDE:
                m_bside, m_aside  = (movement.origin, movement.destination)
            else:
                m_bside, m_aside  = (movement.destination, movement.origin)

            if (m_aside, m_bside) in connections:
                continue
            else:
                new_connections = []
                conns_changed = False
                for aside, bside in connections:
                    if aside == m_aside or m_bside == bside:
                        if not conns_changed:
                            start = [aside, bside]
                        end = [m_aside, m_bside]
                        conns_changed = True
                    else:
                        new_connections.append((aside, bside))
                if not conns_changed:
                    connections.append((m_aside, m_bside))
                else:
                    new_connections.append(end)
                    counter = 1
                    prev_move = self.actions[i-counter]
                    while counter < i and (type(prev_move) is not Movement or\
                            (prev_move.origin != movement.origin and prev_move.destination != movement.destination)):
                        counter += 1
                        prev_move = self.actions[i-counter]
                    self.switches.append((prev_move, movement))
                    connections = new_connections
        
        
    def get_links(self, obj: dict):

        tracks = obj['trackParts']
        for track in tracks:
            track['name'] = re.sub('[^0-9a-zA-Z]+', '_', track['name'])

        def find_aside_connection(track, tracks, connections):
            aside_connections = track['aSide']
            for aside_conn_id in aside_connections:
                aside_conn = next(t for t in tracks if t['id'] == aside_conn_id)
                if aside_conn['type'] == 'RailRoad':
                    connections.add(aside_conn['name'])
                else:
                    connections.union(find_aside_connection(aside_conn, tracks, connections))
            return connections 
            
        links = []
        tracks_filtered = []
        for track in tracks:

            track['name'] = re.sub('[^0-9a-zA-Z]+', '_', track['name'])

            if track['type'] != 'RailRoad':
                continue

            tracks_filtered.append((track['name'], int(track['length']), track['parkingAllowed']))

            aside_tracks = find_aside_connection(track, tracks, set())
            for other in aside_tracks:
                if other == track['name']:
                    continue
                track_left = self.find_track(track['name'])
                if track_left is None:
                    self._add_track('track_'+track['name'])
                    track_left = self.find_track(track['name'])
                track_right = self.find_track(other)
                if track_right is None:
                    self._add_track('track_'+other)
                    track_right = self.find_track(other)

                links.append((track_left, track_right))
                
        return links
   
    
    def filter_by_train(self, train: Train) -> List[Union[Service,Movement]]:
        return [a for a in self.actions if a.train == train]
    
    def filter_by_track(self, track: Track):
        return sorted([a for a in self.actions if type(a) is Movement and (a.origin == track or a.destination == track)] +\
            [a for a in self.actions if type(a) is Service and a.track == track], key=lambda x: x.id)
    

    def build_constraints(self):
        self.finalize()

        self.switch_between = set()
        for x, y in self.switches:
            self.switch_between.add((x.id, y.id))
        self.end_before = set()
        self.turn_between = set()
        for train in self.trains:
            filt_act = self.filter_by_train(train)
            for i in range(len(filt_act)-1):
                pair = (filt_act[i].id,filt_act[i+1].id)
                if type(filt_act[i]) is Movement and type(filt_act[i+1]) is Movement and\
                    filt_act[i].direction != filt_act[i+1].direction:
                        self.turn_between.add(pair)
                elif pair not in self.switch_between:
                    self.end_before.add(pair)
        self.switch_between = set([s for s in self.switch_between if s not in self.turn_between])
        for track in self.tracks:
            filt_act = self.filter_by_track(track)
            for i in range(len(filt_act)-1):
                pair = (filt_act[i].id,filt_act[i+1].id)
                if pair not in self.switch_between:
                    self.end_before.add(pair)

    def build_walking_times_matrix(self, walking_times: dict):
        self.walking_arr = np.zeros((len(self.actions), len(self.actions)))
        for i, a1 in enumerate(self.actions):
            if type(a1) is Movement:
                start = a1.destination.name.split('track_')[1]
            elif type(a1) is Service:
                start = a1.track.name.split('track_')[1]
            for j, a2 in enumerate(self.actions):
                if type(a2) is Movement:
                    end = a2.origin.name.split('track_')[1]
                elif type(a2) is Service:
                    end = a2.track.name.split('track_')[1]
                if (start, end) in walking_times.keys():
                    self.walking_arr[a1.id-1,a2.id-1] = walking_times[(start, end)]
                elif (end, start) in walking_times.keys():
                    self.walking_arr[a1.id-1,a2.id-1] = walking_times[(end, start)]
                # else:
                #     print('DID NOT FIND: ', (start, end))
        
                

    def _np_to_dzn_arr(self, arr):
        if len(arr) == 0:
            return '[]'
        if len(np.shape(arr)) > 2:
            raise Exception('Not supported arrays with >2 dimensions')
        if len(np.shape(arr)) > 1 and np.shape(arr)[1] > 1 and np.shape(arr)[0] > 1:
            return '[|' + ',\n|'.join(','.join(str(int(x)) for x in moves) for moves in arr) + '|]'
        else:
            return '[' + ','.join(str(int(x)) for x in arr) + ']'
        
    def get_durations(self):
        durations = []
        for a in self.actions:
            if type(a) is Movement:
                durations.append(1)
            elif type(a) is Service:
                durations.append(30)
        return durations

    def write_dzn(self, num_drivers):

        if os.path.exists('minizinc/data.dzn'):
            os.remove('minizinc/data.dzn')

        preceding_str = self._np_to_dzn_arr([pc[0] for pc in sorted(self.end_before)])
        anteceding_str = self._np_to_dzn_arr([pc[1] for pc in sorted(self.end_before)])
        before_switch_str = self._np_to_dzn_arr([ds[0] for ds in sorted(self.switch_between)])
        after_switch_str = self._np_to_dzn_arr([ds[1] for ds in sorted(self.switch_between)])
        before_turn_str = self._np_to_dzn_arr([tc[0] for tc in sorted(self.turn_between)])
        after_turn_str = self._np_to_dzn_arr([tc[1] for tc in sorted(self.turn_between)])

        

        with open('minizinc/data.dzn', 'w') as f:
            f.writelines([
                f'NUM_TRAINS = {len(self.trains)};\n',
                f'NUM_ACTIONS = {len(self.actions)};\n',
                f'NUM_DRIVERS = {num_drivers};\n',
                '\n',
                f'D = {self._np_to_dzn_arr(self.get_durations())};\n',
                f'TA = {self._np_to_dzn_arr([m.train.id for m in self.actions])};\n',
                '\n',
                f'NUM_PRECEDENCE_CONSTRAINTS = {len(self.end_before)};\n',
                f'preceding = {preceding_str};\n',
                f'anteceding = {anteceding_str};\n',
                '\n',
                f'NUM_SWITCH_CONSTRAINTS = {len(self.switch_between)};\n',
                f'before_switch = {before_switch_str};\n',
                f'after_switch = {after_switch_str};\n',
                '\n',
                f'NUM_TURN_CONSTRAINTS = {len(self.turn_between)};\n',
                f'before_turn = {before_turn_str};\n',
                f'after_turn = {after_turn_str};\n',
                '\n',
                f'MAX_WALKING = {int(np.max(self.walking_arr))};\n',
                'walk_times = ' + self._np_to_dzn_arr(self.walking_arr) + ';'
            ])