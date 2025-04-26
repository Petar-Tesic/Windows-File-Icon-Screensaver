import pygame
import sys
import random
import math
import time
import os
import platform

IS_WINDOWS = platform.system() == 'Windows'

if IS_WINDOWS:
    import win32gui
    import win32ui
    import win32con
    import win32api
    from PIL import Image

class IconScreensaver:
    def __init__(self):
        pygame.init()
        info = pygame.display.Info()
        self.width, self.height = info.current_w, info.current_h
        self.screen = pygame.display.set_mode((self.width, self.height), pygame.FULLSCREEN)
        pygame.display.set_caption("Icon Screensaver")
        self.clock = pygame.time.Clock()
        self.running = True
        self.last_mouse_pos = pygame.mouse.get_pos()
        self.mouse_distance = 0
        self.icons = []
        self.icon_objects = []
        if IS_WINDOWS:
            self.load_system_icons()
            if self.icons:
                self.create_icon_objects()
        self.current_phase = "normal"
        self.phase_start_time = time.time()
        self.phase_durations = {
            "normal": random.uniform(20, 30),
            "freeing": 15,
            "dvd": 15
        }
        self.freed_icons = []

    def load_system_icons(self):
        if not IS_WINDOWS:
            return
        try:
            shell32 = os.path.join(os.environ['SystemRoot'], 'System32', 'shell32.dll')
            if not os.path.exists(shell32):
                print("BRO I CANT FIND SHELL32")
                raise Exception("BRO I CANT FIND SHELL32")
            screen_dc = win32gui.GetDC(0)
            if not screen_dc:
                raise Exception("Could not get screen DC :(")
            memory_dc = win32ui.CreateDCFromHandle(screen_dc)
            save_dc = memory_dc.CreateCompatibleDC()
            ico_x = win32api.GetSystemMetrics(win32con.SM_CXICON)
            ico_y = win32api.GetSystemMetrics(win32con.SM_CYICON)
            bitmap = win32ui.CreateBitmap()
            bitmap.CreateCompatibleBitmap(memory_dc, ico_x, ico_y)
            save_dc.SelectObject(bitmap)
            for i in range(50):
                try:
                    large, _ = win32gui.ExtractIconEx(shell32, i, 1)
                    if not large:
                        continue
                    hicon = large[0]
                    try:
                        save_dc.FillSolidRect((0, 0, ico_x, ico_y), 0)
                        win32gui.DrawIconEx(save_dc.GetHandleOutput(), 0, 0, hicon, ico_x, ico_y, 0, None, win32con.DI_NORMAL)
                        bmpstr = bitmap.GetBitmapBits(True)
                        img = Image.frombuffer('RGBA', (ico_x, ico_y), bmpstr, 'raw', 'BGRA', 0, 1)
                        if any(px[3] > 0 for px in img.getdata()):
                            pygame_surface = pygame.image.fromstring(img.tobytes(), (ico_x, ico_y), 'RGBA')
                            self.icons.append(pygame_surface)
                            print(f"Added icon {i}")
                    finally:
                        win32gui.DestroyIcon(hicon)
                except Exception as e:
                    print(f"cant load icon {i}: {str(e)}")
                    continue
            win32gui.ReleaseDC(0, screen_dc)
            save_dc.DeleteDC()
            memory_dc.DeleteDC()
            win32gui.DeleteObject(bitmap.GetHandle())
            print(f"loaded {len(self.icons)} icons from shell32.dll")
            if self.icons:
                return
        except Exception as e:
            print(f"Error icon loading: {str(e)}")
        if not self.icons:
            print("Creating defaults")
            colors = [
                (255, 0, 0),
                (0, 255, 0),
                (0, 0, 255),
                (255, 255, 0),
                (255, 0, 255),
                (0, 255, 255),
                (255, 128, 0),
                (128, 0, 255),
                (0, 255, 128),
                (255, 255, 255),
            ]
            for color in colors:
                surf = pygame.Surface((32, 32), pygame.SRCALPHA)
                surf.fill((0, 0, 0, 0))
                pygame.draw.circle(surf, (*color, 255), (16, 16), 14)
                pygame.draw.circle(surf, (255, 255, 255, 128), (16, 16), 10)
                pygame.draw.circle(surf, (*color, 255), (16, 16), 8)
                self.icons.append(surf)
            print("Done creating defaults")

    def create_icon_objects(self):
        icon_size = 48
        spacing = 60
        cols = self.width // spacing
        rows = self.height // spacing
        self.icon_objects = []
        for row in range(rows):
            for col in range(cols):
                icon_surf = random.choice(self.icons)
                base_x = col * spacing + spacing/2
                base_y = row * spacing + spacing/2
                offset_x = random.uniform(-5, 5)
                offset_y = random.uniform(-5, 5)
                pattern = random.choice(['circle', 'wave', 'bounce'])
                self.icon_objects.append({
                    'surface': icon_surf,
                    'x': base_x + offset_x,
                    'y': base_y + offset_y,
                    'base_x': base_x,
                    'base_y': base_y,
                    'speed_x': random.uniform(-1, 1),
                    'speed_y': random.uniform(-1, 1),
                    'rotation': random.uniform(0, 360),
                    'rot_speed': random.uniform(-2, 2),
                    'scale': random.uniform(0.8, 1.2),
                    'pattern': pattern,
                    'pattern_offset': random.uniform(0, 2 * math.pi),
                    'amplitude': random.uniform(5, 15),
                    'frequency': random.uniform(0.02, 0.05),
                    'is_freed': False,
                    'dvd_speed_x': random.choice([-5, 5]),
                    'dvd_speed_y': random.choice([-5, 5]),
                    'target_scale': random.uniform(0.8, 1.2)
                })

    def update_icons(self):
        current_time = time.time()
        phase_elapsed = current_time - self.phase_start_time
        if phase_elapsed >= self.phase_durations[self.current_phase]:
            if self.current_phase == "normal":
                self.current_phase = "freeing"
                self.phase_start_time = current_time
                self.freed_icons = random.sample(self.icon_objects, 10)
                for icon in self.freed_icons:
                    icon['is_freed'] = True
                    icon['target_scale'] = random.uniform(2.0, 3.0)
                    icon['speed_x'] = random.uniform(-8, 8)
                    icon['speed_y'] = random.uniform(-8, 8)
            elif self.current_phase == "freeing":
                self.current_phase = "dvd"
                self.phase_start_time = current_time
                for icon in self.icon_objects:
                    icon['is_freed'] = False
                    icon['target_scale'] = 1.0
            elif self.current_phase == "dvd":
                self.current_phase = "normal"
                self.phase_start_time = current_time
                self.phase_durations["normal"] = random.uniform(20, 30)
        for icon in self.icon_objects:
            scale_diff = icon['target_scale'] - icon['scale']
            icon['scale'] += scale_diff * 0.1
            icon['rotation'] += icon['rot_speed']
            if icon['rotation'] > 360:
                icon['rotation'] -= 360
            if self.current_phase == "normal":
                if not icon['is_freed']:
                    if icon['pattern'] == 'circle':
                        angle = current_time * 2 + icon['pattern_offset']
                        icon['x'] = icon['base_x'] + math.cos(angle) * icon['amplitude']
                        icon['y'] = icon['base_y'] + math.sin(angle) * icon['amplitude']
                    elif icon['pattern'] == 'wave':
                        icon['x'] = icon['base_x'] + math.sin(current_time * 3 + icon['pattern_offset']) * icon['amplitude']
                        icon['y'] = icon['base_y'] + math.cos(current_time * 2 + icon['pattern_offset']) * icon['amplitude']
                    else:
                        icon['x'] += icon['speed_x']
                        icon['y'] += icon['speed_y']
                        if abs(icon['x'] - icon['base_x']) > 20:
                            icon['speed_x'] *= -1
                        if abs(icon['y'] - icon['base_y']) > 20:
                            icon['speed_y'] *= -1
            elif self.current_phase == "freeing":
                if icon['is_freed']:
                    icon['x'] += icon['speed_x']
                    icon['y'] += icon['speed_y']
                    if icon['x'] < 0 or icon['x'] > self.width:
                        icon['speed_x'] *= -1
                    if icon['y'] < 0 or icon['y'] > self.height:
                        icon['speed_y'] *= -1
                else:
                    icon['x'] = icon['base_x'] + random.uniform(-2, 2)
                    icon['y'] = icon['base_y'] + random.uniform(-2, 2)
            elif self.current_phase == "dvd":
                icon['x'] += icon['dvd_speed_x']
                icon['y'] += icon['dvd_speed_y']
                if icon['x'] < 0 or icon['x'] > self.width:
                    icon['dvd_speed_x'] *= -1
                    icon['rot_speed'] = random.uniform(-4, 4)
                if icon['y'] < 0 or icon['y'] > self.height:
                    icon['dvd_speed_y'] *= -1
                    icon['rot_speed'] = random.uniform(-4, 4)

    def draw_icons(self):
        for y in range(0, self.height, 2):
            progress = y / self.height
            if self.current_phase == "normal":
                color = (
                    int(0 * (1 - progress) + 0 * progress),
                    int(0 * (1 - progress) + 20 * progress),
                    int(30 * (1 - progress) + 50 * progress)
                )
            elif self.current_phase == "freeing":
                color = (
                    int(20 * (1 - progress) + 40 * progress),
                    int(0 * (1 - progress) + 0 * progress),
                    int(30 * (1 - progress) + 50 * progress)
                )
            else:
                color = (
                    int(0 * (1 - progress) + 20 * progress),
                    int(20 * (1 - progress) + 40 * progress),
                    int(20 * (1 - progress) + 40 * progress)
                )
            pygame.draw.line(self.screen, color, (0, y), (self.width, y))
        for icon in self.icon_objects:
            shadow = pygame.transform.rotozoom(icon['surface'], icon['rotation'], icon['scale'] * 1.1)
            shadow.set_alpha(50)
            shadow_rect = shadow.get_rect()
            shadow_rect.center = (int(icon['x']) + 2, int(icon['y']) + 2)
            self.screen.blit(shadow, shadow_rect)
            rotated = pygame.transform.rotozoom(icon['surface'], icon['rotation'], icon['scale'])
            rect = rotated.get_rect()
            rect.center = (int(icon['x']), int(icon['y']))
            self.screen.blit(rotated, rect)

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.running = False
        current_mouse_pos = pygame.mouse.get_pos()
        dx = current_mouse_pos[0] - self.last_mouse_pos[0]
        dy = current_mouse_pos[1] - self.last_mouse_pos[1]
        distance_moved = math.sqrt(dx*dx + dy*dy)
        self.mouse_distance += distance_moved
        if self.mouse_distance > 200:
            self.running = False
        self.last_mouse_pos = current_mouse_pos

    def run(self):
        while self.running:
            self.handle_events()
            if IS_WINDOWS:
                self.update_icons()
                self.draw_icons()
            pygame.display.flip()
            self.clock.tick(60)
        pygame.quit()

if __name__ == "__main__":
    screensaver = IconScreensaver()
    screensaver.run()
