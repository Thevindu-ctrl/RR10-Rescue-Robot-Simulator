import pygame
import time
import os

#Constants
LOG_FILE = r"C:\Users\acer\RR10_Simulation\logs\log.txt"
SCREEN_W, SCREEN_H = 1100, 600
CENTER_Y = SCREEN_H // 2
SCALE_X = 6 

class RescueRobotGUI:
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_W, SCREEN_H))
        pygame.display.set_caption("RR-10 Simulation - Single Pass")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont("Arial", 18, bold=True)
        self.blink_start = 0
        self.in_zone = False

    def run(self):
        if not os.path.exists(LOG_FILE): 
            print("Error: Run C++ code first to generate log.txt")
            return
            
        with open(LOG_FILE, 'r') as f:
            logs = [line.strip().split(',') for line in f.readlines()[1:]]
        
        # Mode definitions from C++ enum
        mode_map = {
            0: "MODE: NOMINAL LINE FOLLOWING",
            1: "MODE: SEARCHING FOR LINE",
            2: "MODE: OBSTACLE / HAZARD DETECTED",
            3: "MODE: MANUAL OVERRIDE (INTERRUPT)"
        }
        
        start_t = time.time()
        idx = 0

        # LOOP TERMINATION
        while idx < len(logs):
            for event in pygame.event.get():
                if event.type == pygame.QUIT: return

            # Sync with C++ log timestamps
            elapsed = (time.time() - start_t) * 1000
            while idx < len(logs) - 1 and int(logs[idx][0]) < elapsed:
                idx += 1
            
            ts, x, y, state = int(logs[idx][0]), float(logs[idx][1]), float(logs[idx][2]), int(logs[idx][3])
            
            #Rendering
            self.screen.fill((10, 10, 12)) 

            #Navigation Line
            pygame.draw.line(self.screen, (50, 50, 50), (0, CENTER_Y), (SCREEN_W, CENTER_Y), 2)

            #Obsticle
            obs_draw_x = (50 * SCALE_X) 
            pygame.draw.rect(self.screen, (150, 0, 0), (obs_draw_x, CENTER_Y - 15, 30, 30))
            pygame.draw.rect(self.screen, (255, 255, 255), (obs_draw_x, CENTER_Y - 15, 30, 30), 1)

            #Hazard Zone
            h_start = (150 * SCALE_X) 
            pygame.draw.rect(self.screen, (255, 69, 0), (h_start, CENTER_Y - 15, 180, 50), 1)

            #Color Indicator Logic
            now = time.time()
            color = (0, 255, 0) # Default Green

            if 35 <= x < 75: 
                if not self.in_zone:
                    self.blink_start = now
                    self.in_zone = True
                
                timer = now - self.blink_start
                if timer < 1.2:
                    color = (255, 0, 0) if int(timer / 0.3) % 2 == 0 else (20, 20, 20)
                else:
                    color = (255, 255, 0) if int(timer / 0.1) % 2 == 0 else (20, 20, 20)
            elif 150 <= x <= 180:
                color = (255, 0, 0) 
            else:
                self.in_zone = False

            # Robot design
            rx, ry = (x * SCALE_X), CENTER_Y + (y * 15)
            pygame.draw.circle(self.screen, color, (int(rx), int(ry)), 15)
            pygame.draw.circle(self.screen, (255, 255, 255), (int(rx), int(ry)), 15, 2)

            # Dashboard & Modes ---
            self.screen.blit(self.font.render(f"X_COORD: {x:.1f}", True, (200,200,200)), (20, 20))
            self.screen.blit(self.font.render(f"Y_OFFSET: {y:.1f}", True, (200,200,200)), (20, 45))
            
            # Display Mode Status
            current_mode_text = mode_map.get(state, "MODE: UNKNOWN")
            mode_color = (255, 50, 50) if state in [2, 3] else (0, 255, 0)
            self.screen.blit(self.font.render(current_mode_text, True, mode_color), (20, 70))

            # Action description 
            action_text = "Action: Proceeding on Path"
            if 35 <= x < 45:
                action_text = "Action: BRAKING - Obstacle Ahead"
            elif 45 <= x < 65:
                action_text = "Action: DETOUR - Avoiding Obstacle"
            elif 65 <= x < 75:
                action_text = "Action: RE-ENTRY - Returning to Line"
            elif 150 <= x <= 180:
                action_text = "Action: CAUTION - Entering Hazard Zone"
            
            self.screen.blit(self.font.render(action_text, True, (255, 255, 255)), (20, 95))
            
            # EXIT 
            if rx > SCREEN_W:
                print("End of Track Reached.")
                break

            pygame.display.flip()
            self.clock.tick(60)

        # Keep the screen open for 2 seconds after finishing before closing
        time.sleep(2)
        pygame.quit()

if __name__ == "__main__":
    RescueRobotGUI().run()