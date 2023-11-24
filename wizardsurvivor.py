#!/usr/bin/python3
from ws_constants import SCREEN_WIDTH, SCREEN_HEIGHT, EXTRAS, WEAPONS, PASSIVES, PICKUPS, MAPS, CHARACTERS
from ws_classes import Pickup, Enemy, Boss, Player, CameraGroup
import pygame, sys, time, asyncio, random, math

class CurrentMap():
    def __init__(self, current_map, difficulty):
        self.running = True
        self.spawn_mult = 1.0
        self.boss_alive = False
        self.finished_upgrades = []
        self.money_lost_percentage = .5
        self.available_weapons = list(WEAPONS.keys())
        self.available_passives = list(PASSIVES.keys())
        self.available_upgrades = self.available_weapons + self.available_passives
        self.countdown = current_map["timeout"] * 60
        self.time = self.countdown
        self.enemies = current_map["enemies"]
        self.minibosses = [current_map["boss"]]
        self.boss = current_map["boss"]
        self.waves = current_map["waves"]
        self.current_wave = 1
        self.ground = current_map["background"]
        self.ground_fill = current_map["bgcolor"]
        self.difficulty = difficulty
        self.width = current_map["width"]
        self.height = current_map["height"]
        self.exp_wave_offset = 0
        self.bar_width = 100
        self.bar_height = 10
        self.title_font = pygame.font.Font(None, 48)
        self.stats_font = pygame.font.Font(None, 16)
        self.victory = False
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.choices = random.sample(self.available_upgrades, 5)
        self.load_map()
        self.set_powers()
    
    # ------------------------ SPAWNING ------------------------
    def spawn_enemies(self, enemy, amount, grouped = False):
        if grouped:
            pos = self.random_point_on_circle(self.player.rect.centerx, 
                                              self.player.rect.centery, 
                                              SCREEN_WIDTH // 2)
            player_pos = pygame.Vector2(self.player.rect.centerx, self.player.rect.centery)
            target = (player_pos - (pos - player_pos))
            for i in range(0, amount):
                Enemy(pos, [self.camera_group, self.camera_group.enemy_group], enemy, self, target)
        else:
            for i in range(0, amount):
                pos = self.random_point_on_circle(self.player.rect.centerx, 
                                                self.player.rect.centery, 
                                                SCREEN_WIDTH // 2)
                Enemy(pos, [self.camera_group, self.camera_group.enemy_group], enemy, self)
    
    def spawn_boss(self, boss, is_boss):
        self.boss_alive = True
        pos = self.random_point_on_circle(self.player.rect.centerx,
                                        self.player.rect.centery,
                                        SCREEN_WIDTH // 2)
        Boss(pos, [self.camera_group, self.camera_group.enemy_group], boss, self, is_boss)
        
    def spawn_pickup(self, pos, choice = None):
        if choice is not None:
            random_pickup = choice
        else:
            random_pickup = random.choices(list(PICKUPS.keys()), weights=[pickup["weight"] for pickup in PICKUPS.values()])[0]
        if random_pickup != "nothing":
            magnetize = False
            delta_x = self.player.rect.centerx - pos[0]
            delta_y = self.player.rect.centery - pos[1]
            distance = math.hypot(delta_x, delta_y)
            if distance < self.player.modifiers["pickup_radius"]:
                magnetize = True
            
            Pickup(pos, [self.camera_group, self.camera_group.pickup_group], random_pickup, PICKUPS[random_pickup], magnetize)

    # ------------------------ MISC ------------------------
    def set_gamestate(self, state):
        set_gamestate(state)

    def level_up(self, choice):
        not_found = True
        if choice in EXTRAS.keys():
            not_found = False
            self.player.money += 200
            
        for power in self.player.weapons + self.player.passives:
            if choice == power[0]:
                not_found = False
                power[1] += 1
                if power[1] == 5:
                    self.available_weapons = [key for key in self.available_weapons if key != choice]
                    self.available_passives = [key for key in self.available_passives if key != choice]
                    self.finished_upgrades.append(choice)
                break
        
        if not_found:
            if choice in WEAPONS.keys():
                self.player.weapons.append([choice, 0])
                if len(self.player.weapons) == 5:
                    self.available_weapons = [key for key in self.available_weapons if key in [power[0] for power in self.player.weapons]]
            elif choice in PASSIVES.keys():
                self.player.passives.append([choice, 0])
                if len(self.player.passives) == 5:
                    self.available_passives = [key for key in self.available_passives if key in [power[0] for power in self.player.passives]]

        self.available_upgrades = list(self.available_weapons + self.available_passives)
        while len(self.available_upgrades) < 5:
            self.available_upgrades.append("200 Coins")

        set_gamestate("gameplay")
        self.set_powers()        
        self.choices = random.sample(self.available_upgrades, 5)
    
    def set_powers(self):
        i = 0
        for orb in self.camera_group.orb_group:
            orb.kill()
            
        for weapon in self.player.weapons:
            pygame.time.set_timer(100 + i, WEAPONS[weapon[0]][weapon[1]]["cooldown"])
            i += 1
        for passive in self.player.passives:
            for key, value in PASSIVES[passive[0]][passive[1]].items():
                self.player.modifiers[key] = value
        pygame.time.set_timer(98, 5000)

    def load_map(self):
        self.camera_group = CameraGroup(self.ground, self)
        self.player = Player((self.width // 2, self.height // 2), self.camera_group, CHARACTERS["Wizard Bob"], self)
        self.camera_group.set_player(self.player)
    
    def random_point_on_circle(self, center_x, center_y, radius):
        angle = random.uniform(0, 2 * math.pi)
        x = center_x + radius * math.cos(angle)
        y = center_y + radius * math.sin(angle)
        return (int(x), int(y))
    
    def draw_text(self, surface, text, font, color, rect, max_width=None):
        words = text.split(' ')
        space_width, _ = font.size(' ')
        word_height = 0
        lines = []
        current_line = []
        current_width = 0
        for word in words:
            word_width, word_height = font.size(word)
            if max_width and current_width + word_width > max_width:
                lines.append(' '.join(current_line))
                current_line = [word]
                current_width = word_width + space_width
            else:
                current_line.append(word)
                current_width += word_width + space_width

        lines.append(' '.join(current_line))
        y = rect.centery - (len(lines) - 1) * word_height // 2
        for line in lines:
            text_surface = font.render(line, True, color)
            text_rect = text_surface.get_rect(center=(rect.centerx, y))
            surface.blit(text_surface, text_rect)
            y += word_height
    
    # ------------------------ UI ------------------------
    def display_box(self, x, y, width, height, title, image_path, second_title, text):
        box_surface = pygame.Surface((width, height), pygame.SRCALPHA)
        background_image = pygame.image.load("graphics/upgrade_bg.png").convert_alpha()
        box_surface.blit(background_image, (0, 0))
        image = pygame.image.load(image_path).convert_alpha()
        image_rect = image.get_rect(center=(width // 2, height // 2 - 22))
        box_surface.blit(image, image_rect)
        font_title = pygame.font.Font(None, 22)
        font_second_title = pygame.font.Font(None, 18)
        font_text = pygame.font.Font(None, 16)
        title_shadow = font_title.render(title, True, (0, 0, 0))
        title_shadow_rect = title_shadow.get_rect(center=((width // 2) + 1, 15))
        second_title_shadow = font_second_title.render(second_title, True, (0, 0, 0))
        second_title_shadow_rect = second_title_shadow.get_rect(center=((width // 2) + 1, 35))
        title_text = font_title.render(title, True, (255, 0, 255) if title != "NEW" else (255,255,0))
        title_rect = title_text.get_rect(center=((width // 2) - 1, 13))
        second_title_text = font_second_title.render(second_title, True, (255, 255, 255))
        second_title_rect = second_title_text.get_rect(center=((width // 2) - 1, 33))
        text_rect = pygame.Rect(0, 0, width, height + 165)
        self.draw_text(box_surface, text, font_text, (255, 255, 255), text_rect, max_width=text_rect.width - 67)
        box_surface.blit(title_shadow, title_shadow_rect)
        box_surface.blit(second_title_shadow, second_title_shadow_rect)
        box_surface.blit(title_text, title_rect)
        box_surface.blit(second_title_text, second_title_rect)
        screen.blit(box_surface, (x, y))
    
    def mainmenu_ui(self):
        pass
      
    def levelup_ui(self):
        transparent_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bg, (0, 0, 0, 128), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(transparent_bg, (0,0))
        i = 0
        for choice in self.choices:
            level = 0
            for weapon in self.player.weapons:
                if choice == weapon[0]:
                    level = weapon[1] + 1
                    break
            for passive in self.player.passives:
                if choice == passive[0]:
                    level = passive[1] + 1
                    break
                    
            if choice in WEAPONS.keys():
                item = WEAPONS[choice]
                description = item["description"]
                
            elif choice in PASSIVES.keys():
                item = PASSIVES[choice]
                description = f'{item[level]["description"]}'
                
            else:
                item = EXTRAS[choice]
                description = item["description"]
            
            self.display_box(40 + (250 * i), 100, 200, 300, f'Level {level}' if level != 0 else "NEW", item["image"], choice, description)
            i += 1
    
    def pause_ui(self):
        frame_width = 600
        frame_height = 400
        font = pygame.font.Font(None, 36)
        transparent_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bg, (0, 0, 0, 128), (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(transparent_bg, (0, 0))
        frame_rect = pygame.Rect((SCREEN_WIDTH - frame_width) // 2, (SCREEN_HEIGHT - frame_height) // 2 - 75, frame_width, frame_height)
        pygame.draw.rect(screen, (255, 255, 255), frame_rect)
        title_label = font.render(self.player.name, True, (0,0,0))
        title_rect = title_label.get_rect(center = (frame_rect.centerx, frame_rect.top + 20))
        screen.blit(title_label, title_rect)
        stats = (f'Level: {self.player.level}',
                 f'{"Life" if self.player.lives == 1 else "Lives"}: {self.player.lives}',
                 f'Health: {self.player.health}/{self.player.max_health}',
                 f'Regen: {self.player.health_regen} HP/5s',
                 f'Experience: {self.player.exp}/{self.player.exp_to_level}',
                 f'Money: {self.player.money}',
                 f'Speed: {self.player.max_speed * self.player.modifiers["speed_mult"]}',
                 f'Armor: {self.player.armor}',
                 f'Damage: {(self.player.damage + self.player.modifiers["damage"]) * self.player.modifiers["damage_mult"]}',
                 f'Extra projectiles: {self.player.extra_projectiles + self.player.modifiers["extra_projectiles"]}',
                 f'')

        i = 1
        for line in stats:
            label = font.render(line, True, (0,0,0))
            label_rect = label.get_rect(topleft = (frame_rect.left + 20, frame_rect.top + 50 + (30 * i)))
            screen.blit(label, label_rect)
            i += 1
            
        i = 1
        for power in list(self.player.weapons + self.player.passives):
            text = f'{power[0]} - Lv.{power[1]}'
            label = font.render(text, True, (0,0,0))
            label_rect = label.get_rect(topleft = (frame_rect.centerx + 20, frame_rect.top + 50 + (30 * i)))
            screen.blit(label, label_rect)
            i += 1
            
        # Create buttons
        button_width, button_height = 150, 50
        resume_button_rect = pygame.Rect((frame_rect.left + frame_rect.width // 2 - button_width - 10, frame_rect.bottom + 70, button_width, button_height))
        quit_button_rect = pygame.Rect((frame_rect.left + frame_rect.width // 2 + 10, frame_rect.bottom + 70, button_width, button_height))
        
        # Draw buttons
        pygame.draw.rect(screen, (0, 255, 0), resume_button_rect)
        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)

        # Create button labels
        resume_label = font.render("Resume", True, (0, 0, 0))
        quit_label = font.render("Quit", True, (0, 0, 0))

        # Position button labels
        resume_label_rect = resume_label.get_rect(center=resume_button_rect.center)
        quit_label_rect = quit_label.get_rect(center=quit_button_rect.center)

        # Draw button labels
        screen.blit(resume_label, resume_label_rect)
        screen.blit(quit_label, quit_label_rect)

    def map_ui(self):
        # Title and text
        countdown = self.title_font.render(f'{max(0, self.countdown // 60)}:{str(self.countdown % 60).zfill(2)}', True, (255, 255, 255))
        countdown_rect = countdown.get_rect(center=(SCREEN_WIDTH // 2, 20))
        screen.blit(countdown, countdown_rect)
        experience = self.stats_font.render(f'Level: {self.player.level}', True, (255, 255, 255))
        experience_rect = experience.get_rect(topleft=(10, SCREEN_HEIGHT - 40))
        screen.blit(experience, experience_rect)
        money = self.stats_font.render(f'Money: {self.player.money}', True, (255, 255, 255))
        money_rect = money.get_rect(topleft=(10, SCREEN_HEIGHT - 20))
        screen.blit(money, money_rect)
        
        # Health bar
        health_ratio = self.player.health / self.player.max_health
        health_bar_x = self.player.rect.centerx - self.bar_width // 2 - self.camera_group.offset.x
        health_bar_y = self.player.rect.y - 30 - self.camera_group.offset.y
        transparent_bg = pygame.Surface((self.bar_width, self.bar_height), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bg, (0, 0, 0, 64), (0, 0, self.bar_width, self.bar_height))
        screen.blit(transparent_bg, (health_bar_x, health_bar_y))
        pygame.draw.rect(screen, (255, 0, 0), (health_bar_x, health_bar_y, self.bar_width * health_ratio, self.bar_height))

        # Experience bar
        experience_ratio = self.player.exp / self.player.exp_to_level if self.player.exp < self.player.exp_to_level else 1
        experience_bar_x = self.player.rect.centerx - self.bar_width // 2 - self.camera_group.offset.x
        experience_bar_y = self.player.rect.y - 20 - self.camera_group.offset.y
        transparent_bg = pygame.Surface((self.bar_width, self.bar_height // 2), pygame.SRCALPHA)
        pygame.draw.rect(transparent_bg, (0, 0, 0, 64), (0, 0, self.bar_width, self.bar_height // 2))
        screen.blit(transparent_bg, (experience_bar_x, experience_bar_y))
        pygame.draw.rect(screen, (0, 255, 0), (experience_bar_x, experience_bar_y, self.bar_width * experience_ratio, self.bar_height // 2))
    
    def end_ui(self):
        title_font = pygame.font.Font(None, 48)
        text_font = pygame.font.Font(None, 24)
        transparent_bg = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        if self.victory:
            color = (0, 255, 0, 128)
            title = "VICTORY!"
            money = f'Money: {self.player.money}'
        else:
            color = (255, 0, 0, 128)
            title = "DEFEAT..."
            money = f'Retained money: {int(self.player.money * self.money_lost_percentage)}'

        pygame.draw.rect(transparent_bg, color, (0, 0, SCREEN_WIDTH, SCREEN_HEIGHT))
        screen.blit(transparent_bg, (0, 0))
        title_label = title_font.render(title, True, (0,0,0))
        title_rect = title_label.get_rect(center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        screen.blit(title_label, title_rect)
        text_label = text_font.render(money, True, (0,0,0))
        text_label_rect = text_label.get_rect(topleft = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + (50)))
        screen.blit(text_label, text_label_rect) 
        button_width, button_height = 150, 50
        menu_button_rect = pygame.Rect((480, 555, button_width, button_height))
        quit_button_rect = pygame.Rect((650, 555, button_width, button_height))
        pygame.draw.rect(screen, (0, 255, 0), menu_button_rect)
        pygame.draw.rect(screen, (255, 0, 0), quit_button_rect)
        resume_label = text_font.render("Main Menu", True, (0, 0, 0))
        quit_label = text_font.render("Quit", True, (0, 0, 0))
        resume_label_rect = resume_label.get_rect(center=menu_button_rect.center)
        quit_label_rect = quit_label.get_rect(center=quit_button_rect.center)
        screen.blit(resume_label, resume_label_rect)
        screen.blit(quit_label, quit_label_rect)   

def set_gamestate(state):
    global game_state
    game_state = state
    
def wave_spawn():
    wave = current_map.waves[current_map.current_wave]
    grouped = False
    if not current_map.boss_alive:
        current_map.countdown -= 1
        if current_map.countdown == 0:
            current_map.spawn_boss(current_map.boss, True)

        elif (current_map.time - current_map.countdown) % 180 == 0:
            current_map.current_wave += 1
            current_map.spawn_boss(current_map.minibosses[0], False)
            
        if current_map.countdown % 30 == 0:
            current_map.exp_wave_offset += 1
            wave = current_map.waves[5]
            grouped = True
        
        if current_map.countdown % 60 == 0:
            current_map.spawn_mult += 0.25
            
    print("Enemies:", len(current_map.camera_group.enemy_group)) ## to test for lagging, remember to check here
    if len(current_map.camera_group.enemy_group) <= 1000:
        i = 0
        for enemy in current_map.enemies:
            if wave[i] != (0,0):
                current_map.spawn_enemies(enemy, int(random.randrange(wave[i][0], wave[i][1]) * current_map.spawn_mult), grouped)
            i += 1

def detect_collisions():
    collisions = pygame.sprite.groupcollide(current_map.camera_group.enemy_group, current_map.camera_group.projectile_group, False, False)
    for enemy, projectiles in collisions.items():
        max_damage = 0
        max_projectile = None
        for projectile in projectiles:
            if projectile.damage > max_damage:
                max_damage = projectile.damage
                max_projectile = projectile
        
        if not enemy.is_damaged and max_projectile is not None:
            max_projectile.collide()
            enemy.damaged(max_damage)

async def game_loop(framerate_limit=30):
    loop = asyncio.get_event_loop()
    next_frame_target = 0.0
    limit_frame_duration = (1.0 / framerate_limit)
    menu_rendered = False
    while True:
        if limit_frame_duration:  
            this_frame = time.time()
            delay = next_frame_target - this_frame
            if delay > 0:
                await asyncio.sleep(delay)
            next_frame_target = this_frame + limit_frame_duration

        if game_state == "gameplay":
            screen.fill(current_map.ground_fill)
            current_map.camera_group.custom_draw(current_map.player)
            detect_collisions()
            current_map.camera_group.update(current_map.player, current_map.camera_group.enemy_group)
            current_map.map_ui()
            menu_rendered = False

        elif game_state in ("paused", "levelup", "mainmenu", "mapend"):
            if not menu_rendered:
                screen.fill(current_map.ground_fill)
                current_map.camera_group.custom_draw(current_map.player)
                current_map.map_ui()
                if game_state == "levelup":
                    current_map.levelup_ui()
                elif game_state == "paused":
                    current_map.pause_ui()
                elif game_state == "mainmenu":
                    current_map.mainmenu_ui()
                elif game_state == "mapend":
                    current_map.end_ui()
                menu_rendered = True

        events_to_handle = list(pygame.event.get())
        events_handled = loop.create_task(handle_events(events_to_handle))
        await loop.run_in_executor(None, pygame.display.update)
        await events_handled

async def handle_events(events_to_handle):
    box1_rect = pygame.Rect(40, 100, 200, 300)
    box2_rect = pygame.Rect(290, 100, 200, 300)
    box3_rect = pygame.Rect(540, 100, 200, 300)
    box4_rect = pygame.Rect(790, 100, 200, 300)
    box5_rect = pygame.Rect(1040, 100, 200, 300)
    if game_state == "paused":
        box1_rect = pygame.Rect(480, 555, 150,50)
        box2_rect = pygame.Rect(650, 555, 150, 50)

    for event in events_to_handle:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if current_map is not None:
            if game_state == "gameplay":
                if event.type == pygame.USEREVENT:
                    wave_spawn()

                if event.type == 98:
                    current_map.player.heal(current_map.player.modifiers["health_regen"])

                if event.type == 99:
                    current_map.player.invincible = False
                    current_map.player.state = "idle"
                    pygame.time.set_timer(99, 0)

                if event.type in range(100, 100 + len(WEAPONS)):
                    cast_type = WEAPONS[current_map.player.weapons[event.type - 100][0]]["type"]
                    if cast_type == "projectile":
                        current_map.player.cast_projectile(WEAPONS[current_map.player.weapons[event.type - 100][0]], 
                                                current_map.player.weapons[event.type - 100][1], 
                                                [current_map.camera_group, 
                                                    current_map.camera_group.projectile_group])
                    elif cast_type == "orb":
                        if len(current_map.camera_group.orb_group) == 0:
                            current_map.player.cast_orb(WEAPONS[current_map.player.weapons[event.type - 100][0]], 
                                                    current_map.player.weapons[event.type - 100][1], 
                                                    [current_map.camera_group, 
                                                        current_map.camera_group.projectile_group, 
                                                        current_map.camera_group.orb_group])
                        
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        set_gamestate("paused")

                    if event.key == pygame.K_1:
                        current_map.spawn_mult += 1
                
                    if event.key == pygame.K_2:
                        current_map.player.collect("experience", {"value": 999})
                    
                    if event.key == pygame.K_3:
                        current_map.spawn_pickup((SCREEN_WIDTH // 3, SCREEN_HEIGHT // 3), "chest")
                        
            elif game_state == "paused":
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_0:
                        set_gamestate("gameplay")
                        
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if box1_rect.collidepoint(mouse_x, mouse_y):
                        set_gamestate("gameplay")
                    elif box2_rect.collidepoint(mouse_x, mouse_y):
                        pygame.quit()
                        sys.exit()
            
            elif game_state == "levelup":
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    if box1_rect.collidepoint(mouse_x, mouse_y):
                        current_map.level_up(current_map.choices[0])
                    elif box2_rect.collidepoint(mouse_x, mouse_y):
                        current_map.level_up(current_map.choices[1]) 
                    elif box3_rect.collidepoint(mouse_x, mouse_y):
                        current_map.level_up(current_map.choices[2])
                    elif box4_rect.collidepoint(mouse_x, mouse_y):
                        current_map.level_up(current_map.choices[3])
                    elif box5_rect.collidepoint(mouse_x, mouse_y):
                        current_map.level_up(current_map.choices[4])
                    else:
                        continue

if __name__ == "__main__":
    pygame.init()
    event_handler = ...
    game_state = "gameplay"
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),flags=pygame.SCALED, vsync=1)
    current_map = CurrentMap(MAPS["1"], 1)
    asyncio.run(game_loop(120))