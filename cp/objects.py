

from typing import List
from enum import Enum


class Direction(Enum):
    ASIDE = 0
    BSIDE = 1


class Driver:
    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name
    
    def __str__(self) -> str:
        return f'Driver(id={self.id}, name={self.name})'
    
    def __repr__(self) -> str:
        return self.__str__()

class Train:
    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name

    def __str__(self) -> str:
        return f'Train(id={self.id}, name={self.name})'
    
    def __repr__(self) -> str:
        return self.__str__()

class Track:
    def __init__(self, id: int, name: str):
        self.id: int = id
        self.name: str = name
    
    def __str__(self) -> str:
        return f'Track(id={self.id}, name={self.name})'
    
    def __repr__(self) -> str:
        return self.__str__()
    

class Movement:
    def __init__(self, id: int, train: Train, direction: Direction, origin: Track, destination: Track):
        self.id: int = id
        self.train: Train = train
        self.direction: Direction = direction
        self.origin: Track = origin
        self.destination: Track = destination
    
    def __str__(self) -> str:
        return f'(move_{self.direction} {self.train} {self.origin} {self.destination}) [id={self.id}]'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def compact_str(self):
        if self.direction == Direction.ASIDE:
            dirr = 'aside'
        elif self.direction == Direction.BSIDE:
            dirr = 'bside'
        return f'(move_{dirr} {self.train.name} {self.origin.name} {self.destination.name})'

class Enter:
    def __init__(self, id: int, driver: Driver, train: Train):
        self.id: int = id
        self.driver = driver
        self.train: Train = train

    def __str__(self) -> str:
        return f'(enter {self.driver} {self.train})'
    
    def __repr__(self) -> str:
        return self.__str__()

class Exit:
    def __init__(self, id: int, driver: Driver, train: Train):
        self.id: int = id
        self.driver = driver
        self.train: Train = train

    def __str__(self) -> str:
        return f'(exit {self.driver} {self.train})'
    
    def __repr__(self) -> str:
        return self.__str__()
    
class Service:
    def __init__(self, id: int, train: Train, track: Track):
        self.id: int = id
        self.train: Train = train
        self.track: Track = track

    def __str__(self) -> str:
        return f'(service {self.train} {self.track}) [id={self.id}]'
    
    def __repr__(self) -> str:
        return self.__str__()
    
    def compact_str(self):
        return f'(service {self.train.name})'


class Switch:
    def __init__(self, tracks: List[Track]):
        self.tracks = tracks

    def __str__(self) -> str:
        return f'(switch [{self.tracks[0].name} - {self.tracks[1].name}] [{self.tracks[2].name} - {self.tracks[3].name}])'
        
    
    def __repr__(self) -> str:
        return self.__str__()