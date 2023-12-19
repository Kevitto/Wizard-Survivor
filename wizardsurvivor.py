#!/usr/bin/python3
from ws_constants import SCREEN_WIDTH, SCREEN_HEIGHT, EXTRAS, WEAPONS, PASSIVES, PICKUPS, MAPS, CHARACTERS
from ws_classes import Enemy, Boss, Player, CameraGroup
from pyqtree import Index
import pygame, sys, asyncio, random, math, os, pickle

class Game():
    LAYER_IMAGES = ["graphics/abg_layer{}.png".format(i) for i in range(1, 7)]
    def __init__(self):
        self.game_save = "game.save"
        self.name = "Wizard Survivor"
        self.version = "0.0.1"
        self.game_state = "titlescreen"
        self.load()
        self.title_font = pygame.font.Font(None, 48)
        self.text_font = pygame.font.Font(None, 24)
        self.bg_layers = [pygame.image.load(image).convert_alpha() for image in self.LAYER_IMAGES]
        self.bg_layers[3].fill((255, 255, 255, int(255 * 0.6)), None, pygame.BLEND_RGBA_MULT)
        self.bg_layer5_x = 0
        self.title_image = pygame.image.load("graphics/title.png").convert_alpha()
        self.frame = 0
        self.animation_speed = 2
        self.text_up = True
        self.text_y = 0
        self.title_y = 50

    def save(self):
        print('saved...?')
        pickle.dump(self.game_data, open(self.game_save, 'wb'))

    def load(self):
        try:
            print('loaded game')
            self.game_data = pickle.load(open(self.game_save, 'rb'))
        except FileNotFoundError:
            print('loaded garbage')
            self.game_data = {"game_difficulty": 1,
                "game_character": "Wizard Bob",
                "game_map": "1",
                "game_talents": 0,
                "game_money": 0,
                "game_level": 0,
                "game_exp": 0,
                "permanent_modifiers": {"health_mult": 1,
                                        "health_regen": 0,
                                        "armor": 0,
                                        "damage": 0,
                                        "damage_mult": 1,
                                        "speed_mult": 1,
                                        "extra_projectiles": 0,
                                        },}

    def animated_bg(self):
        for i, layer in enumerate(self.bg_layers):
            if i == 3:
                temp_image = layer.copy()
                screen.blit(temp_image, (self.bg_layer5_x, 0))
                screen.blit(temp_image, (self.bg_layer5_x - temp_image.get_width(), 0))
                self.bg_layer5_x += 1
                if self.bg_layer5_x >= temp_image.get_width():
                    self.bg_layer5_x = 0
            else:
                screen.blit(layer, (0, 0))
        
    def title_screen_ui(self): # Title Screen UI
        self.frame += 1
        if self.frame / self.animation_speed < 50:
            if self.frame % self.animation_speed == 0:
                self.title_y -= 1
                self.animated_bg()
                temp_image = self.title_image.copy()
                temp_image.fill((255, 255, 255, int(self.frame / self.animation_speed * 5)), None, pygame.BLEND_RGBA_MULT)
                screen.blit(temp_image, (SCREEN_WIDTH // 2 - temp_image.get_width() // 2, 50 + self.title_y))
        else:
            if self.frame % self.animation_speed == 0:
                self.animated_bg()
            screen.blit(self.title_image, (SCREEN_WIDTH // 2 - self.title_image.get_width() // 2, 50 + self.title_y))
            if self.text_up == True:
                self.text_y += 0.25
            else:
                self.text_y -= 0.25
                
            if self.text_y == 5:
                self.text_up = False
            elif self.text_y == 0:
                self.text_up = True
                
            text = self.text_font.render("Press any key to start", True, (255, 255, 255))
            text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 200 + self.text_y))
            screen.blit(text, text_rect)
        
    def character_select_ui(self):
        pass
    
    def map_select_ui(self):
        pass
    
    def store_ui(self):
        pass
    
    def talent_ui(self):
        pass

class CurrentMap():
    def __init__(self, current_map, difficulty):
        self.running = True
        self.spawn_mult = 1.0
        self.boss_alive = False
        self.finished_upgrades = []
        self.money_lost_percentage = .5
        self.available_weapons = list(WEAPONS.keys())
        self.available_passives = list(PASSIVES.keys())
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
        self.distance = math.hypot(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        self.title_font = pygame.font.Font(None, 48)
        self.stats_font = pygame.font.Font(None, 16)
        self.victory = False
        pygame.time.set_timer(pygame.USEREVENT, 1000)
        self.choices = self.generate_choices()
        self.load_map()
        self.set_powers()
    
    # ------------------------ SPAWNING ------------------------
    def spawn_enemies(self, enemy, amount, grouped = False):
        if grouped:
            group_pos = self.random_point_on_circle(self.player.rect.centerx, 
                                              self.player.rect.centery, 
                                              self.distance + random.randrange(-100, 100))
            player_pos = pygame.Vector2(self.player.rect.centerx, self.player.rect.centery)
            target = (player_pos - (group_pos - player_pos))
            for i in range(min(10, amount)):
                pos = self.random_point_on_circle(group_pos[0], 
                                              group_pos[1], 
                                              75)
                Enemy(pos, [self.camera_group, self.camera_group.enemy_group], enemy, self, target)
        else:
            for i in range(amount):
                pos = self.random_point_on_circle(self.player.rect.centerx, 
                                                self.player.rect.centery, 
                                                self.distance + random.randrange(-100, 100))
                Enemy(pos, [self.camera_group, self.camera_group.enemy_group], enemy, self)
    
    def spawn_boss(self, boss, is_boss):
        self.boss_alive = True
        pos = self.random_point_on_circle(self.player.rect.centerx,
                                        self.player.rect.centery,
                                        self.distance)
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
            
            #Pickup(pos, [self.camera_group, self.camera_group.pickup_group], random_pickup, PICKUPS[random_pickup], magnetize)

    # ------------------------ MISC ------------------------
    def generate_choices(self):
        distribution_list = ((1,4), (2,3), (3,2), (4,1))
        distribution = random.choice(distribution_list)
        num_weapons = len(self.available_weapons)
        num_passives = len(self.available_passives)

        try:
            weapons = random.sample(self.available_weapons, distribution[0])
            passives = random.sample(self.available_passives, distribution[1])
            choices = random.sample(weapons + passives, 5)
        except ValueError:
            choices = random.sample(self.available_weapons + self.available_passives,
                                    min(5, num_weapons + num_passives))

        choices += ["200 Coins"] * (5 - len(choices))
        return choices
    
    def set_gamestate(self, state):
        set_gamestate(state)

    def level_up(self, choice):
        not_found = True
        if choice in EXTRAS:
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
            weapon_names = [power[0] for power in self.player.weapons]
            passive_names = [power[0] for power in self.player.passives]
            if choice in WEAPONS:
                self.player.weapons.append([choice, 0])
                if len(self.player.weapons) == 5:
                    self.available_weapons = [key for key in self.available_weapons if key in weapon_names]
            elif choice in PASSIVES:
                self.player.passives.append([choice, 0])
                if len(self.player.passives) == 5:
                    self.available_passives = [key for key in self.available_passives if key in passive_names]

        set_gamestate("gameplay")
        self.set_powers()        
        self.choices = self.generate_choices()
    
    def set_powers(self):
        for orb in self.camera_group.orb_group:
            orb.kill()

        for aura in self.camera_group.aura_group:
            aura.kill()

        for i, weapon in enumerate(self.player.weapons):
            pygame.time.set_timer(100 + i, WEAPONS[weapon[0]][weapon[1]]["cooldown"])

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
        words = text.split()
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
    print(f' projectiles: {len(current_map.camera_group.projectile_group)}\n enemies: {len(current_map.camera_group.enemy_group)}\n pickups: {len(current_map.camera_group.pickup_group)}\n orbs: {len(current_map.camera_group.orb_group)}\n auras: {len(current_map.camera_group.aura_group)}')
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
            
    if len(current_map.camera_group.enemy_group) <= 500:
        for i, enemy in enumerate(current_map.enemies):
            if wave[i] != (0,0):
                current_map.spawn_enemies(enemy, int(random.randrange(wave[i][0], wave[i][1]) * current_map.spawn_mult), grouped)

def detect_collisions(): #tracking enemies
    game_area = (0, 0, current_map.width, current_map.height)
    enemy_quadtree = Index(bbox=game_area, max_items = 10)
    for enemy in current_map.camera_group.enemy_group:
        if not enemy.is_damaged:
            enemy_quadtree.insert(enemy, enemy.rect)
    
    for projectile in current_map.camera_group.projectile_group:
        nearby_enemies = enemy_quadtree.intersect(projectile.rect)
        for enemy in nearby_enemies:
            if enemy.rect.colliderect(projectile.rect):
                if enemy.is_damaged:
                    continue
                else:
                    enemy.damaged(projectile.damage, projectile)
            
def detect_collisions2(): #tracking projectiles
    game_area = (0, 0, current_map.width, current_map.height)
    projectile_quadtree = Index(bbox=game_area, max_items = 50)
    for projectile in current_map.camera_group.projectile_group:
        projectile_quadtree.insert(projectile, projectile.rect)

    print(f' projectiles: {len(current_map.camera_group.projectile_group)}')
    for enemy in current_map.camera_group.enemy_group:
        if enemy.is_damaged: 
            continue

        nearby_projectiles = projectile_quadtree.intersect(enemy.rect)
        max_damage = 0
        max_projectile = None
        for projectile in nearby_projectiles:
            dx = enemy.rect.left - projectile.circle_hitbox.centerx if enemy.rect.left > projectile.circle_hitbox.centerx else 0
            dx = max(dx, projectile.circle_hitbox.centerx - enemy.rect.right)
            dy = enemy.rect.top - projectile.circle_hitbox.centery if enemy.rect.top > projectile.circle_hitbox.centery else 0
            dy = max(dy, projectile.circle_hitbox.centery - enemy.rect.bottom)
            distance = (dx**2 + dy**2) ** 0.5
            if distance < projectile.radius:
                if projectile.damage > max_damage:
                    max_damage = projectile.damage
                    max_projectile = projectile

        if max_damage > 0:
            enemy.damaged(max_damage, max_projectile)

def start_map():
    global current_map
    for i in range(5):
        pygame.time.set_timer(100 + i, 0)
    current_map = CurrentMap(MAPS["1"], 1)
    set_gamestate("gameplay")

async def game_loop(framerate_limit=30):
    clock = pygame.time.Clock()
    menu_rendered = False
    loop = asyncio.get_event_loop()
    while True:
        clock.tick(framerate_limit)
        if game_state == "gameplay":
            screen.fill(current_map.ground_fill)
            current_map.camera_group.custom_draw(current_map.player)
            detect_collisions()
            current_map.camera_group.update(current_map.player, current_map.camera_group.enemy_group)
            current_map.map_ui()
            menu_rendered = False

        elif game_state in ("paused", "levelup", "mainmenu", "mapend", "titlescreen"):
            if not menu_rendered:
                if game_state not in ("mainmenu", "titlescreen"):
                    screen.fill(current_map.ground_fill)
                    current_map.camera_group.custom_draw(current_map.player)
                    current_map.map_ui()
                    if game_state == "levelup":
                        current_map.levelup_ui()
                    elif game_state == "paused":
                        current_map.pause_ui()
                    elif game_state == "mapend":
                        current_map.end_ui()
                    menu_rendered = True
                else:
                    if game_state == "titlescreen":
                        game.title_screen_ui()
                    elif game_state == "mainmenu":
                        current_map.mainmenu_ui()

        events_to_handle = list(pygame.event.get())
        events_handled = loop.create_task(handle_events(events_to_handle))
        await loop.run_in_executor(None, pygame.display.update)
        await events_handled

async def handle_events(events_to_handle):
    for event in events_to_handle:
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if game_state == "titlescreen":
            if event.type == pygame.KEYDOWN:
                set_gamestate("gameplay")
                
        elif game_state == "gameplay":
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
                elif cast_type == "aura":
                    if len(current_map.camera_group.aura_group) == 0:
                        current_map.player.cast_aura(WEAPONS[current_map.player.weapons[event.type - 100][0]], 
                                                    current_map.player.weapons[event.type - 100][1],
                                                    [current_map.camera_group,
                                                        current_map.camera_group.projectile_group,
                                                        current_map.camera_group.aura_group])

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_gamestate("paused")
                if event.key == pygame.K_1:
                    current_map.spawn_mult += 1
                if event.key == pygame.K_2:
                    current_map.player.collect("experience", {"value": 999})
                if event.key == pygame.K_3:
                    current_map.spawn_pickup((current_map.player.rect.centerx - 300, current_map.player.rect.centery - 300), "chest")
                if event.key == pygame.K_4:
                    start_map()
                    return
                if event.key == pygame.K_5:
                    game.save()
                if event.key == pygame.K_6:
                    game.load()
                    
        elif game_state == "paused":
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    set_gamestate("gameplay")
                    
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if box1_rect_paused.collidepoint(mouse_x, mouse_y):
                    set_gamestate("gameplay")
                elif box2_rect_paused.collidepoint(mouse_x, mouse_y):
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
                
        elif game_state == "mapend":
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                if box1_rect.collidepoint(mouse_x, mouse_y):
                    start_map()
                    return
                elif box2_rect.collidepoint(mouse_x, mouse_y):
                    pygame.quit()
                    sys.exit()

if __name__ == "__main__":
    pygame.init()
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    event_handler = ...
    game_state = "titlescreen"
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT),flags=pygame.SCALED, vsync=1)
    box1_rect = pygame.Rect(40, 100, 200, 300)
    box2_rect = pygame.Rect(290, 100, 200, 300)
    box3_rect = pygame.Rect(540, 100, 200, 300)
    box4_rect = pygame.Rect(790, 100, 200, 300)
    box5_rect = pygame.Rect(1040, 100, 200, 300)
    box1_rect_paused = pygame.Rect(480, 555, 150,50)
    box2_rect_paused = pygame.Rect(650, 555, 150, 50)
    current_map = CurrentMap(MAPS["1"], 1)
    game = Game()
    asyncio.run(game_loop(120))