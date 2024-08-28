from enum import Enum

class MapEdges(Enum):
    TOP_LEFT = 0
    TOP_RIGHT = 1
    BOTTOM_LEFT = 2
    BOTTOM_RIGHT = 3

class UnitType(Enum):
    WALL = 0
    SUPPORT = 1
    TURRET = 2
    SCOUT = 3
    DEMOLISHER = 4
    INTERCEPTOR = 5
    REMOVE = 6
    UPGRADE = 7   

unit_type_to_index = {
    UnitType.WALL: 0,
    UnitType.SUPPORT: 1,
    UnitType.TURRET: 2,
    UnitType.SCOUT: 3,
    UnitType.DEMOLISHER: 4,
    UnitType.INTERCEPTOR: 5,
    UnitType.REMOVE: 6,
    UnitType.UPGRADE: 7
}

class ResourceTypes(Enum):
    SP = 0
    MP = 1