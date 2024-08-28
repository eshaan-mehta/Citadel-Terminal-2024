# from game import *
from .sim_game_state import SimGameState
from typing import List
import json

# Format of test: 
        # {
        #   "p1Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE],
        #   "p2Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE]
        # }
class Simulator: 
    def __init__(self, config, game_state_string, tests_string):
        self.config = config
        self.serialized_string = game_state_string #last action frame
        self.tests = json.loads(tests_string) # array of tests

        global WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR
        WALL = config["unitInformation"][0]["shorthand"]
        SUPPORT = config["unitInformation"][1]["shorthand"]
        TURRET = config["unitInformation"][2]["shorthand"]
        SCOUT = config["unitInformation"][3]["shorthand"]
        DEMOLISHER = config["unitInformation"][4]["shorthand"]
        INTERCEPTOR = config["unitInformation"][5]["shorthand"]

        self.game_state = None
        self.simulation_results = []

    def get_results(self) -> list[str]:
        return self.simulation_results
    
    """
    An individual test is of the format: 
        {
            "p1Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE],
            "p2Units": [WALL, SUPPORT, TURRET, SCOUT, DEMOLISHER, INTERCEPTOR, REMOVE, UPGRADE]
        }
    """
    def run_simulations(self):
        # run each individual simulation
        for test in self.tests:
            self.game_state = SimGameState(self.config, self.serialized_string, test)
            res = self.simulation_loop()
            self.simulation_results.append(res)
            
    def simulation_loop(self) -> dict[str, List[float]]:
        """Having loaded game state, run simulation loop

        Returns:
            dict[str, List[float]]: game result summary
        """ 
        frame_count = -1
        # Action Phase
        is_round_over = False
        while not is_round_over: 
            frame_count += 1
            # Round ends when no more walkers
            walkers = self.game_state.get_walkers()
            if len(walkers) == 0:
                is_round_over = True

            # Give shields:
            for support in self.game_state.get_supports(): 
                # check if a new walker has entered and give it shield
                support_location = [support.x, support.y]
                locations = self.game_state.game_map.get_locations_in_range(support_location, support.shieldRange)
                for i, j in locations: 
                    if self.game_state.game_map[(i, j)] and not self.game_state.contains_stationary_unit([i, j]):
                        units = self.game_state.game_map[(i, j)][support.player_index]
                        for u in units: 
                            if u.player_index == support.player_index and u not in support.given_shield: 
                                support.given_shield.add(u)
                                u.health += support.shieldPerUnit + support.shieldBonusPerY * (support.y - j)
        
            # Move walkers, by the tile
            have_moved = set()
            for walker in self.game_state.get_walkers():
                if walker in have_moved:
                    continue
                #Type of game_map[x, y] = [p1 = set[units], p2 = set[units]]

                # ensure movement only happens every speed frames
                if frame_count % walker.speed != 0:
                    continue

                # Check if the walker's current position is an edge
                quadrant = self.game_state.game_map.get_quadrant(walker.x, walker.y)
                if (walker.x, walker.y) in self.game_state.game_map.get_edge_locations(quadrant):
                    self.game_state.game_map[walker.x, walker.y][walker.player_index].remove(walker)
                    self.game_state.fighters.remove(walker)
                    self.game_state.walkers.remove(walker)
                    if walker.player_index == 0:
                        self.game_state.enemy_health -= 2 if walker.unit_type == DEMOLISHER else 1
                    if walker.player_index == 1:
                        self.game_state.my_health -= 2 if walker.unit_type == DEMOLISHER else 1
                    continue

                #move walker to next 
                next_step = walker.next_step() #automatically dequeues from the path #tuple(x, y)
                self.game_state.game_map[walker.x, walker.y][walker.player_index].remove(walker)
                self.game_state.game_map[next_step][walker.player_index].add(walker)



            # Attack
            def get_target(unit): 
                locations = self.game_state.game_map.get_locations_in_range([unit.x, unit.y], unit.attackRange)
                best_target = None
                for i, j in locations: 
                    targets = []
                    # [] or [STATIONARY] or [{WALKERS}, {WALKERS}]

                    # empty square
                    if len(self.game_state.game_map[i, j]) == 0: 
                        continue
                    # stationary unit
                    elif self.game_state.contains_stationary_unit([i, j]):
                        targets = self.game_state.game_map[i, j]
                    # walkers
                    else: 
                        targets = self.game_state.game_map[i, j][1 if unit.player_index == 0 else 0]
                        
                    for target in targets:
                        if not best_target:
                            best_target = target
                            continue
                    
                        # 1. Priority Targeting
                        if best_target.unit_type in [WALL, SUPPORT, TURRET] and target.unit_type in [SCOUT, DEMOLISHER, INTERCEPTOR]:
                            best_target = target

                        # 2. Distance Targeting
                        if self.game_state.game_map.distance_between_locations([unit.x, unit.y], [i, j]) < self.game_state.game_map.distance_between_locations([unit.x, unit.y], [best_target.x, best_target.y]):
                            best_target = target
                            
                        # 3. Health Targeting
                        if target.health < best_target.health:
                            best_target = target
                            
                        # 4. Furthest into Your Side (Assume your side is the bottom)
                        if target.y < best_target.y:
                            best_target = target

                        # 5. Closest to an Edge
                        if self.game_state.game_map.distance_to_closest_edge(target.x, target.y) < self.game_state.game_map.distance_to_closest_edge(best_target.x, best_target.y):
                            best_target = target
                        
                return best_target
                
            # Units that die will be pending for removal
            pending_removal = set()
            structure_destroyed = False
            for unit in self.game_state.get_attackers():
                target = get_target(unit)
                if target and not (unit.unit_type == TURRET and target.unit_type == [WALL, SUPPORT, TURRET]): 
                    target.health -= unit.damage_f if target.unit_type in [WALL, SUPPORT, TURRET] else unit.damage_i
                    if target.health <= 0:
                        pending_removal.add(target)
                        if target in [WALL, SUPPORT, TURRET]:
                            structure_destroyed = True
            
            
            # Check if we need to recompute walker paths
            if structure_destroyed:
                for walker in self.game_state.get_walkers(): 
                    if walker in pending_removal: 
                        continue
                
                    # Recompute path
                    start_location = [walker.x, walker.y]
                    squares_on_edge = self.game_state.game_map.get_edge_locations(walker.target_edge)
                    path = self.game_state._shortest_path_finder.navigate_multiple_endpoints(start_location, squares_on_edge, self.game_state)
                    walker.set_path(path)

            # Cleanup dead structures and units
            for unit in pending_removal: 
                if unit.unit_type in [WALL, SUPPORT, TURRET]:
                    self.game_state.game_map[unit.x, unit.y] = []
                else: 
                    self.game_state.game_map[unit.x, unit.y][unit.player_index].remove(unit)
                    self.game_state.walkers.remove(unit)
                
                if unit.unit_type in [TURRET, SCOUT, DEMOLISHER, INTERCEPTOR]:
                    self.game_state.fighters.remove(unit)
                
        return self.game_state.get_summary()