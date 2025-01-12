from typing import Tuple, List, Union
from numpy.typing import ArrayLike
from enum import Enum
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.ticker import MultipleLocator
from objects import Service, Movement

from datetime import datetime, timedelta
from typing import Tuple, List

DT_MINS = 5

ENTER_TRAIN = 0.1
EXIT_TRAIN = 0.2
CHANGE_DIRECTION = 0.3

class DriverStatus(Enum):
    IDLE = 0
    DRIVING = 1


def init_train_driver_schedules(start_times: ArrayLike, 
                                durations: ArrayLike, 
                                action_train: ArrayLike,
                                action_driver: ArrayLike) -> Tuple[ArrayLike, ArrayLike]:
    num_trains = np.max(action_train)
    num_drivers = np.max(action_driver)
    max_end_time = np.max(start_times)+np.max(durations)
    FIRST_TRAIN = np.min(action_train)
    FIRST_DRIVER = np.min(action_driver)
    DRIVER_IDLE = FIRST_DRIVER-1
    train_schedule = np.zeros((num_trains,max_end_time))
    driver_schedule = np.ones((num_drivers,max_end_time)) * (FIRST_TRAIN-1)


    for i in range(len(start_times)):
        train_id = action_train[i]
        driver_id = action_driver[i]
        train_schedule[train_id-FIRST_TRAIN,start_times[i]:start_times[i]+durations[i]] = i+1
        driver_schedule[driver_id-FIRST_DRIVER,start_times[i]:start_times[i]+durations[i]] = train_id

    return train_schedule, driver_schedule

def finalize_driver_schedule(driver_schedule: ArrayLike) -> ArrayLike:
    DS = driver_schedule.copy()
    IDLE = np.min(DS)

    new_schedule = dict()

    for d in range(DS.shape[0]):
        status = DriverStatus.IDLE
        for t in range(DS.shape[1]-2):
            train = f'train_slt{40+t}'
            if driver_schedule[d,t] != IDLE:
                if status == DriverStatus.IDLE:
                    new_schedule[t] = f'enter {train}' 
                    status = DriverStatus.DRIVING
            if driver_schedule[d,t] == IDLE:
                if status == DriverStatus.DRIVING:
                    new_schedule[t] = f'exit {train}' 
                    status = DriverStatus.IDLE

    return new_schedule

def parse_mzn_arrays(start_times: ArrayLike, 
                    durations: ArrayLike, 
                    action_train: ArrayLike,
                    action_driver: ArrayLike,
                    movement_labels: List[str] = None):
    train_schedule, driver_schedule = init_train_driver_schedules(start_times,durations, 
                                                                  action_train, action_driver)
    driver_schedule = finalize_driver_schedule(driver_schedule)
    print(driver_schedule)
    train_labels = (['idle'] + movement_labels) if movement_labels else [f'action {int(i)}' for i in np.sort(np.unique(action_train))]
    plot_schedule(train_schedule, train_labels)
    driver_labels = [f'action {int(i)}' for i in np.sort(np.unique(driver_schedule))]
    plot_schedule(train_schedule, driver_labels)

def plot_schedule(schedule: ArrayLike, labels: List[str], savename: str):
    fig, ax = plt.subplots(figsize=(20,10))
    minorLocator = MultipleLocator(1)
    im = plt.imshow(schedule, aspect='auto', cmap='tab20b')
    # get the colors of the values, according to the 
    # colormap used by imshow
    colors = [ im.cmap(im.norm(i)) for i in range(len(labels))]
    # create a patch (proxy artist) for every color 
    patches = [ mpatches.Patch(color=colors[i], label=labels[i] ) for i in range(len(labels)) ]
    # put those patched as legend-handles into the legend
    ax.xaxis.set_minor_locator(minorLocator)
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2)
    plt.grid(which='both')
    fig.tight_layout()
    fig.savefig(f'{savename}.png')
    plt.close()

def plot_schedule2(schedule: ArrayLike, actions: List[Union[Service, Movement]], savename: str):
    movement_labels = []
    for a in actions:
        if type(a) is Service:
            movement_labels.append(f'service {a.train.name.split("_")[1]} {a.track.name.split("_")[1]}')
        else:
            movement_labels.append(f'move {a.train.name.split("_")[1]} {a.origin.name.split("_")[1]} {a.destination.name.split("_")[1]}')

    fig, ax = plt.subplots(figsize=(20,10))
    minorLocator = MultipleLocator(1)
    im = plt.imshow(schedule, aspect='auto', cmap='tab20b')
    # get the colors of the values, according to the 
    # colormap used by imshow
    colors = [ im.cmap(im.norm(i)) for i in range(len(movement_labels))]
    # create a patch (proxy artist) for every color 
    patches = [ mpatches.Patch(color=colors[i], label=movement_labels[i] ) for i in range(len(movement_labels)) ]
    # put those patched as legend-handles into the legend
    ax.xaxis.set_minor_locator(minorLocator)
    ax.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2)
    plt.grid(which='both')
    fig.tight_layout()
    fig.savefig(f'{savename}.png')
    plt.close()
    
    