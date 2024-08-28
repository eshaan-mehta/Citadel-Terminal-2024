import json
import pygame
from .sim_game_state import SimGameState



class Simulator:
    def __init__(self, last_action_frame: json, test: json, using_pygame: bool = False) -> None:
        self.last_action_frame = last_action_frame
        self.test = test
        self.game_state = SimGameState(self.last_action_frame, self.test)
        self.using_pygame = using_pygame

        if using_pygame:
            self.pygame_init()

    def pygame_init(self):
        pygame.init()
        self.screen = pygame.display.set_mode((700,900))
        pygame.display.set_caption("Terminal Tower Defense")
        
        pygame.font.init()
        self.font = pygame.font.SysFont('Comic Sans MS', 15)
        self.clock = pygame.time.Clock()
    
    def run_simulation(self) -> list[str]:
        running = True
        run_full_round = False
        run_single_frame = False
        self.game_state.draw(self.screen, self.font)
        while running:
            # self.screen.fill((200, 200, 200))

            p = pygame.key.get_pressed()
            if p[pygame.K_SPACE]:
                run_full_round = not run_full_round
            if p[pygame.K_RIGHT]:
                run_single_frame = True

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

            mx, my = pygame.mouse.get_pos()
            x_index, y_index = (mx - 12)//25, 27 - (my - 50 - 12)//25
            # print(x_index, y_index)
            font = self.font.render(f"{x_index}, {y_index}", True, (255,255,255))
            font_rect = font.get_rect(center=(750, 100))
            self.screen.blit(font, font_rect) 
            
            if (run_full_round or run_single_frame) and not self.game_state.is_round_over():
                self.game_state.run_frame()
                self.game_state.draw(self.screen, self.font)
                run_single_frame = False
            
            pygame.display.update()
            self.clock.tick(10) #10 FPS, ie delay 100ms between frames

        pygame.quit()
        return self.game_state.get_results()
    
import os
if __name__ == "__main__":
    obj = {
    "turnInfo": [1,2,57],
    "p1Stats": [22,12.4,2.3,52933],
    "p2Stats": [25,9.5,0.3,82365],
    "p1Units": [
        [],
        [],
        [
            [24,13,75,"2"],
            [22,11,75,"8"],
            [10,9,28,"10"],
            [17,9,75,"12"],
            [14,6,75,"14"],
            [13,6,75,"44"]
        ],
        [],
        [],
        [],
        [],
        []
    ],
    "p2Units": 
    [
        [[4,14,40,"51"],
         [3, 17, 40, "18"],
         [0, 14, 40, "20"],
         [1, 15, 40, "22"],
         [2, 14, 40, "26"],
         [2, 15, 40, "28"],
         [3, 14, 40, "47"],
         [3, 15, 40, "49"]
         ],
        [],
        [],
        [],
        [],
        [],
        [],
        [[4,14,0,"52"]]
    ]
}
    test = {
        "p1Units": [[],[],[],[
            [16, 2, 12, ""],
            ],[],[],[], []],
        "p2Units": [[],[],[],[],[],[],[],[]]
    }

    sim = Simulator(obj, test, using_pygame=True)
    results = sim.run_simulation()
    print(results)
