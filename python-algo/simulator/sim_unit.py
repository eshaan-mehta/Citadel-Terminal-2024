from queue import Queue
from typing import Literal
import pygame

from .constants import *
from .game_configs import configs

class SimUnit:
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], health: float = None, unit_count = 1) -> None:
        self.unit_count = unit_count
        self.unit_type = unit_type
        self.x, self.y = xy
        self.health = health if health else configs["unitInformation"][unit_type_to_index[unit_type]]["startHealth"]
        self.player_index = player_index
        self.upgraded = False
        self.cost = configs["unitInformation"][unit_type_to_index[UnitType(unit_type)]]["cost"]
        self.attackRange = configs["unitInformation"][unit_type_to_index[UnitType(unit_type)]].get("attackRange", 0)
        self.damage_structure = configs["unitInformation"][unit_type_to_index[UnitType(unit_type)]].get("attackDamageTower", 0)
        self.damage_walker = configs["unitInformation"][unit_type_to_index[UnitType(unit_type)]].get("attackDamageMobile", 0)
        # self.pending_removal = False
    
    def inflict_damage(self, damage: float) -> float:
        self.health -= damage
        return self.health
    
    def upgrade(self):
        self.upgraded = True
        if self.unit_type == UnitType.TURRET:
            self.attackRange = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["upgrade"]["attackRange"]
            self.damage_walker = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["upgrade"]["attackDamageMobile"]

    def color_by_health(self, color: tuple[int, int, int] = (255,255,255), health: float = None) -> tuple[int, int, int]:
        scaling_factor = (health or self.health) / configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["startHealth"]
        scaling_factor = max(0, min(1, scaling_factor))
        return (int(color[0]*scaling_factor), int(color[1]*scaling_factor), int(color[2]*scaling_factor))
    
    def draw_upgraded(self, xy: tuple[int, int], screen: pygame.display):
        pygame.draw.circle(screen, (255, 255, 0), (12 + xy[0]*25, 50 + 12 + (27-xy[1])*25), 4)
        pygame.draw.circle(screen, (0, 0, 0), (12 + xy[0]*25, 50 + 12 + (27-xy[1])*25), 4, 1) #outline

    def draw(self, screen: pygame.display, font: pygame.font.Font):
        color = self.color_by_health()

        if self.unit_type == UnitType.WALL:
            rect = pygame.Rect(0, 0, 10, 10)
        elif self.unit_type == UnitType.TURRET:
            rect = pygame.Rect(0, 0, 20, 20)

        rect.center = (12 + self.x*25, 50 + 12 + (27-self.y)*25)
        pygame.draw.rect(screen, color, rect)
        if self.upgraded:
            self.draw_upgraded((self.x, self.y), screen)

class SimSupport(SimUnit):
    def __init__(self, xy: tuple[int, int], player_index: Literal[0, 1],  health:int = None) -> None:
        super().__init__(UnitType.SUPPORT, xy, player_index, health)
        self.given_shield = set()
        self.shieldPerUnit = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["shieldPerUnit"]
        self.shieldBonusPerY = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["shieldBonusPerY"]
        self.shieldRange = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["shieldRange"]
    
    def upgrade(self):
        self.shieldRange = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["upgrade"]["shieldRange"]
        self.shieldPerUnit = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["upgrade"]["shieldPerUnit"]
        self.shieldBonusPerY = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["upgrade"]["shieldBonusPerY"]
    
    def draw(self, screen: pygame.display):
        color = self.color_by_health()
        center = (12 + self.x*25, 50 + 12 + (27-self.y)*25)
        pygame.draw.circle(screen, color, center, 10)
        if self.upgraded:
            self.draw_upgraded((self.x, self.y), screen)

class SimWalkerStack(SimUnit):
    def __init__(self, unit_type: UnitType, xy: tuple[int, int], player_index: Literal[0, 1], unit_count) -> None:
        super().__init__(unit_type, xy, player_index, unit_count)
        self.target_edge = self.get_target_edge()
        self.health = [configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]]["startHealth"] for _ in range(unit_count)]
        self.path = Queue()
        self.speed = configs["unitInformation"][unit_type_to_index[UnitType(self.unit_type)]].get("speed", 0)

    def get_target_edge(self):
        # if self.target_edge:
        #     return self.target_edge

        # hard coded half arena size
        return MapEdges.TOP_LEFT if self.x >= 14 else MapEdges.TOP_RIGHT        

    def set_path(self, path):
        self.path.queue.clear()
        for step in path: 
            self.path.put(step)

    def next_step(self):
        return tuple(self.path.get())
    
    def add_to_stack(self):
        self.unit_count += 1
        self.health.append(self.health[0])
    
    def inflict_damage(self, damage: float) -> float:
        """
        returns health of the last unit in the stack
        """
        if len(self.health) == 0:
            return 0
        
        self.health[-1] -= damage

        if self.health[-1] <= 0:
            self.unit_count -= 1
            return self.health.pop()
        
        return self.health[-1]
    
    def draw(self, screen: pygame.display, font: pygame.font.Font):
        color = self.color_by_health((0, 255, 0), self.health[-1])
        center = (12 + self.x*25, 50 + 12 + (27-self.y)*25)
        pygame.draw.circle(screen, color, center, 10)
        
        text_surface = font.render(str(self.unit_count), True, (0, 0, 0))  # White color text
        text_rect = text_surface.get_rect(center=center)

        # Blit the text onto the screen
        screen.blit(text_surface, text_rect)



    