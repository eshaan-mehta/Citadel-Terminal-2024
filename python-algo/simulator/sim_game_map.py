import math
import pygame
from .constants import MapEdges, UnitType
from .sim_unit import *

class SimGameMap:
    edges = MapEdges
    ARENA_SIZE = 28
    HALF_ARENA = 14

    def __init__(self) -> None:
        self.map = [[None for _ in range(self.ARENA_SIZE)] for _ in range(self.ARENA_SIZE)]

    def __getitem__(self, key: tuple[int, int]) -> SimUnit | None:
        return self.map[key[0]][key[1]]
    
    def __setitem__(self, key: tuple[int, int], unit: SimUnit) -> None:
        self.map[key[0]][key[1]] = unit

    def draw(self, screen: pygame.display, font: pygame.font.Font) -> None:
        rect = pygame.Rect(0, 50, 700, 700)
        pygame.draw.rect(screen, (0,0,0), rect)
        for y in range(self.ARENA_SIZE):
            for x in range(self.ARENA_SIZE):
                if self.is_in_bounds(x, y):
                    color = (255, 0, 0) if y < self.HALF_ARENA else (0, 255, 255)
                else:
                    color = (0, 0, 0)
                
                pygame.draw.circle(screen, color, (12 + x*25, 50 + 12 + y*25), 2)
    
    def contains_stationary_unit(self, xy: tuple[int, int]) -> bool:
        """
        Checks if given location contains a stationary unit (WALL, TURRET, SUPPORT)
        """
        return type(self[xy]) in [SimUnit, SimSupport]

    def is_in_bounds(self, x: int, y: int) -> bool:
        """Checks if the given location is inside the diamond shaped game board.

        Args:
            location: A map location

        Returns:
            True if the location is on the board, False otherwise
        
        """
        half_board = self.HALF_ARENA

        row_size = y + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        top_half_check = (y < self.HALF_ARENA and x >= startx and x <= endx)

        row_size = (self.ARENA_SIZE - 1 - y) + 1
        startx = half_board - row_size
        endx = startx + (2 * row_size) - 1
        bottom_half_check = (y >= self.HALF_ARENA and x >= startx and x <= endx)

        return bottom_half_check or top_half_check

    def get_quadrant(self, x: int, y: int) -> MapEdges:
        """"
        Gets the quadrant of the map that a location is in
        """
        if x < self.ARENA_SIZE // 2 and y < self.ARENA_SIZE // 2:
            return self.edges.BOTTOM_LEFT
        if x >= self.ARENA_SIZE // 2 and y < self.ARENA_SIZE // 2:
            return self.edges.BOTTOM_RIGHT
        if x >= self.ARENA_SIZE // 2 and y >= self.ARENA_SIZE // 2:
            return self.edges.TOP_RIGHT
        if x < self.ARENA_SIZE // 2 and y >= self.ARENA_SIZE // 2:
            return self.edges.TOP_LEFT

    def get_edge_locations(self, quadrant: MapEdges) -> list[tuple[int, int]]:
        return self.get_edges()[quadrant.value]

    def get_edges(self) -> list[list[tuple[int, int]]]:

        """Gets all of the edges and their edge locations

        Returns:
            A list with four lists inside of it of locations corresponding to the four edges.
            [0] = top_right, [1] = top_left, [2] = bottom_left, [3] = bottom_right.
        """
        # assume 0,0 is bottom left
        top_right = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA + num
            y = self.ARENA_SIZE - 1 - num
            top_right.append([int(x), int(y)])
        top_left = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA - 1 - num
            y = self.ARENA_SIZE - 1 - num
            top_left.append([int(x), int(y)])
        bottom_left = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA - 1 - num
            y = num
            bottom_left.append([int(x), int(y)])
        bottom_right = []
        for num in range(0, self.HALF_ARENA):
            x = self.HALF_ARENA + num
            y = num
            bottom_right.append([int(x), int(y)])
        return [top_left, top_right, bottom_left, bottom_right]
    
    def distance_between_locations(self, location_1: tuple[int, int], location_2: tuple[int, int]) -> float:
        """Euclidean distance

        Args:
            location_1: An arbitrary location, [x, y]
            location_2: An arbitrary location, [x, y]

        Returns:
            The euclidean distance between the two locations

        """
        x1, y1 = location_1
        x2, y2 = location_2

        return math.sqrt((x1 - x2)**2 + (y1 - y2)**2)
    
    # TODO: by AJ
    def distance_to_closest_edge(self, x: int, y: int) -> float:
        """Calculates the distance from a location to the closest edge"""
        quadrant = self.get_quadrant(x, y)
        edge_locations = self.get_edge_locations(quadrant)
        min_distance = float("inf")
        for edge_location in edge_locations:
            distance = self.distance_between_locations((x, y), edge_location)
            min_distance = min(min_distance, distance)
        return min_distance
    
    def add_unit(self, xy: tuple[int, int], unit: SimUnit | SimSupport | SimWalkerStack) -> None:
        self[xy] = unit

    def remove_unit(self, x, y) -> None:
        if not self.is_in_bounds(x, y):
            return
        self[x,y] = None

    def get_locations_in_range(self, location: tuple[int, int], radius: float) -> list[tuple[int, int]]:
        """Gets locations in a circular area around a location

        Args:
            location: The center of our search area
            radius: The radius of our search area

        Returns:
            The locations that are within our search area

        """
        if radius < 0 or radius > self.ARENA_SIZE:
            self.warn("Radius {} was passed to get_locations_in_range. Expected integer between 0 and {}".format(radius, self.ARENA_SIZE))
        if not self.is_in_bounds(location[0], location[1]):
            self._invalid_coordinates(location)

        x, y = location
        locations = []
        search_radius = math.ceil(radius)
        getHitRadius = 0.01 #from the configs
        for i in range(int(x - search_radius), int(x + search_radius + 1)):
            for j in range(int(y - search_radius), int(y + search_radius + 1)):
                new_location = (i, j)
                # A unit with a given range affects all locations whose centers are within that range + get hit radius
                if self.is_in_bounds(new_location[0], new_location[1]) and self.distance_between_locations(location, new_location) < radius + getHitRadius:
                    locations.append(new_location)
        return locations
    
    def get_best_target(self, unit: SimUnit) -> SimUnit | None: 
        visible_locations = self.get_locations_in_range((unit.x, unit.y), unit.attackRange)
        if not visible_locations:
            return None
        
        best_target_location = visible_locations[0]
        for xy in visible_locations: 
            # None or SimUnit/derived classes
            target = self[xy]

            # No unit at this location
            if not target:
                continue
                
            # Don't target your own units
            if target.player_index == unit.player_index:
                continue

            # turret can not it stationary units
            if unit.unit_type == UnitType.TURRET and target.unit_type in [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]:
                continue
        
            if target.unit_type in [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]:
                target_hp = target.health
            else: 
                target_hp =  0 if target.unit_count <= 0 else target.health[-1]
        
            # If we have nothing, settle for the first thing that is valid 
            if not self[best_target_location] and target and target_hp > 0:
                best_target_location = xy
                continue

            

            # 1. Priority Targeting
            # NOTE: This won't happen because we aren't simulating opponent walkers
            # if best_target_location.unit_type in [WALL, SUPPORT, TURRET] and target.unit_type in [SCOUT, DEMOLISHER, INTERCEPTOR]:
            #     best_target_location = tuple(target.x, target.y)
            # 2. Distance Targeting
            if self.distance_between_locations((unit.x, unit.y), xy) < self.distance_between_locations((unit.x, unit.y), best_target_location):
                best_target_location = (target.x, target.y)
                continue
        
            if self.distance_between_locations((unit.x, unit.y), xy) == self.distance_between_locations((unit.x, unit.y), best_target_location):
                # 3. Health Targeting (make sure to not shoot a target that is already dead (not yet cleaned up!))
                if self[best_target_location].unit_type in [UnitType.WALL, UnitType.TURRET, UnitType.SUPPORT]:
                    best_target_hp = self[best_target_location].health
                else:
                    best_target_hp = 0 if self[best_target_location].unit_count <= 0 else self[best_target_location].health[-1]

                # target hp is better than current best
                if target_hp < best_target_hp and target_hp > 0:
                    best_target_location = (target.x, target.y)
                    continue

                if target.health == best_target_hp:
                    # 4. Furthest into Your Side (Assume your side is the bottom)
                    if (unit.player_index == 0 and target.y < best_target_location[1]) or (unit.player_index == 1 and target.y > best_target_location[1]):
                        best_target_location = (target.x, target.y)
                        continue
                    elif target.y == best_target_location[1]:
                        # 5. Closest to an Edge
                        if self.distance_to_closest_edge(target.x, target.y) < self.distance_to_closest_edge(best_target_location):
                            best_target_location = (target.x, target.y)
        return self[best_target_location]
    