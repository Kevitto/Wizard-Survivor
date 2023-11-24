#!/usr/bin/python3
from ws_constants import SCREEN_WIDTH, SCREEN_HEIGHT
import pygame, random, math

class CameraGroup(pygame.sprite.Group):
    def __init__(self, background, current_map):
        super().__init__()
        self.enemy_group = pygame.sprite.Group()
        self.projectile_group = pygame.sprite.Group()
        self.orb_group = pygame.sprite.Group()
        self.pickup_group = pygame.sprite.Group()
        self.display_surf = pygame.display.get_surface()
        self.offset = pygame.math.Vector2()
        self.half_w = self.display_surf.get_size()[0] // 2
        self.half_h = self.display_surf.get_size()[1] // 2
        self.ground_surf = pygame.image.load(background).convert_alpha()
        self.ground_rects = []
        ground_width = self.ground_surf.get_width()
        ground_height = self.ground_surf.get_height()
        tile_x = current_map.width // self.ground_surf.get_width()
        tile_y = current_map.height // self.ground_surf.get_height()
        for i in range(0, tile_x):
            for j in range(0, tile_y):
                self.ground_rects.append(pygame.Rect(i * ground_width, j * ground_height, self.ground_surf.get_width(), self.ground_surf.get_height()))
        self.ground_rect = self.ground_surf.get_rect(topleft = (0,0))

    def set_player(self, player):
        self.player = player

    def get_relative(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h
        return self.offset

    def custom_draw(self, target):
        self.offset.x = target.rect.centerx - self.half_w
        self.offset.y = target.rect.centery - self.half_h
        i = 0
        for ground_rect in self.ground_rects:
            surf_rect = self.display_surf.get_rect()
            surf_rect.centerx += self.offset.x
            surf_rect.centery += self.offset.y
            if pygame.Rect.colliderect(surf_rect, ground_rect):
                i += 1
                self.display_surf.blit(self.ground_surf, ground_rect.topleft - self.offset)
        
        for sprite in self.pickup_group.sprites():
            self.display_surf.blit(sprite.image, sprite.rect.center - self.offset) # Pickups

        for sprite in sorted(self.enemy_group.sprites(), key = lambda sprite: sprite.rect.centery):
            self.display_surf.blit(sprite.image, sprite.rect.center - self.offset) # Enemies

        for sprite in self.projectile_group.sprites():
            self.display_surf.blit(sprite.image, sprite.rect.center - self.offset) # Projectiles

        self.display_surf.blit(self.player.image, self.player.rect.topleft - self.offset) # Player

class Pickup(pygame.sprite.Sprite):
    def __init__(self, position, groups, type, item, moving):
        super().__init__(groups)
        self.image = pygame.image.load(item["image"]).convert_alpha()
        self.rect = self.image.get_rect(center = position)
        self.type = type
        self.speed = 1
        self.item = item
        self.magnet = item["magnet"]
        self.moving = moving
        
    def update(self, player, enemy_group):
        if self.moving:
            self.move(player)
        self.check_collision(player)
    
    def move(self, player):
        delta_x = player.rect.centerx - self.rect.centerx
        delta_y = player.rect.centery - self.rect.centery
        distance = math.hypot(delta_x, delta_y)
        if distance > 0:
            self.dir = (delta_x / distance, delta_y / distance)

        self.speed *= 1.02
        new_x = self.rect.x + self.dir[0] * self.speed
        new_y = self.rect.y + self.dir[1] * self.speed
        self.rect.x = new_x
        self.rect.y = new_y
    
    def check_collision(self, player):
        if pygame.sprite.collide_rect(self, player):
            player.collect(self.type, self.item)
            self.kill()
            
class Enemy(pygame.sprite.Sprite):
    def __init__(self, position, groups, template, current_map, target = None):
        super().__init__(groups)
        self.current_map = current_map
        self.acceleration = 0.1
        self.friction = 0.05
        self.target = target
        self.auto_destroy = False if target is None else True
        self.dir = pygame.Vector2(0,0)
        self.velocity = pygame.math.Vector2(0, 0)
        self.max_speed = template["speed"]
        self.image = pygame.image.load(template["image"]).convert_alpha()
        self.rect = self.image.get_rect(center = position)
        self.health = template["health"]
        self.damage = template["damage"]
        self.is_damaged = False
        self.flash_end_time = 0
        self.flash_duration = 100
        self.flash_color = (255, 255, 255)
        self.original_image = self.image.copy()
    
    def update(self, player, enemy_group):
        if pygame.time.get_ticks() < self.flash_end_time:
            flash_surface = pygame.Surface(self.rect.size).convert_alpha()
            flash_surface.fill(self.flash_color)
            self.image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
        else:
            if self.is_damaged == True:
                self.image.blit(self.original_image, (0,0))
                self.is_damaged = False
            self.move(player, enemy_group)
    
    def move(self, player, enemy_group):
        target = self.target if self.target is not None else player.rect.center
        target_dir = pygame.math.Vector2(target[0] - self.rect.centerx,
                                            target[1] - self.rect.centery)
        delta_x = target[0] - self.rect.centerx
        delta_y = target[1] - self.rect.centery
        distance = math.hypot(delta_x, delta_y)
        if distance > 0:
            self.dir = pygame.Vector2(delta_x / distance, delta_y / distance)
            
        if distance < 5 and self.auto_destroy:
            self.kill()
            
        if target_dir != (0,0):
            target_dir = target_dir.normalize()

        angle_between = self.dir.angle_to(target_dir)
        max_rotation = min(3, abs(angle_between))
        self.dir.rotate_ip(max_rotation if angle_between > 0 else -max_rotation)
        new_x = self.rect.x + self.dir[0] * self.max_speed
        new_y = self.rect.y + self.dir[1] * self.max_speed
        if self.dir != (0, 0):
            self.velocity += pygame.math.Vector2(self.dir[0] * self.max_speed, self.dir[1] * self.max_speed) * self.acceleration
        else:
            friction_force = -self.velocity * self.friction
            self.velocity += friction_force

        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)
            
        self.rect.x = new_x
        self.rect.y = new_y
                    
    def move2(self, player, enemy_group):
        target = self.target if self.target is not None else player.rect.center
        delta_x = target[0] - self.rect.centerx
        delta_y = target[1] - self.rect.centery
        distance = math.hypot(delta_x, delta_y)
        if distance > 0:
            self.dir = (delta_x / distance, delta_y / distance)
        if distance < 5 and self.auto_destroy:
            self.kill()

        new_x = self.rect.x + self.dir[0] * self.max_speed
        new_y = self.rect.y + self.dir[1] * self.max_speed
        if self.dir != (0, 0):
            self.velocity += pygame.math.Vector2(self.dir[0] * self.max_speed, self.dir[1] * self.max_speed) * self.acceleration
        else:
            friction_force = -self.velocity * self.friction
            self.velocity += friction_force

        if self.velocity.length() > self.max_speed:
            self.velocity.scale_to_length(self.max_speed)

        """collision_rect = self.rect.inflate(-self.rect.width // 2, -self.rect.height // 2)
        collision_rect.topleft = (new_x + self.rect.width // 4, new_y + self.rect.height // 4)
        for enemy in enemy_group:
            if enemy != self and collision_rect.colliderect(enemy.rect):
                delta_x = self.rect.centerx - enemy.rect.centerx
                delta_y = self.rect.centery - enemy.rect.centery
                distance = math.hypot(delta_x, delta_y)
                if distance > 0:
                    away_dir = (delta_x / distance, delta_y / distance)
                    new_x += away_dir[0] * 2
                    new_y += away_dir[1] * 2"""

        self.rect.x = new_x
        self.rect.y = new_y
        
    def damaged(self, damage):
        self.flash_end_time = pygame.time.get_ticks() + self.flash_duration
        self.is_damaged = True
        self.health -= damage
        if self.health <= 0:
            self.current_map.spawn_pickup(self.rect.center)
            self.kill()

class Boss(Enemy):
    def __init__(self, position, groups, template, current_map, is_boss, target = None):
        super().__init__(position, groups, template, current_map, target)
        self.is_boss = is_boss
        self.image = pygame.transform.scale2x(pygame.image.load(template["image"]).convert_alpha())
        self.rect = self.image.get_rect(center = position)
        
    def damaged(self, damage):
        self.flash_end_time = pygame.time.get_ticks() + self.flash_duration
        self.is_damaged = True
        self.health -= damage
        if self.health <= 0:
            if self.is_boss:
                self.current_map.victory = True
                self.current_map.set_gamestate("mapend")
            else:
                self.current_map.boss_alive = False
                self.current_map.spawn_pickup(self.rect.center, "chest")
            self.kill()
    
class Projectile(pygame.sprite.Sprite):
    def __init__(self, position, groups, direction, weapon, level, modifiers, radius):
        super().__init__(groups)
        self.original_image = pygame.transform.scale_by(pygame.image.load(weapon["sprite"]).convert_alpha(),modifiers["projectile_size_mult"])
        self.image = self.original_image
        self.rect = self.image.get_rect(center=position)
        self.type = weapon["movement"]
        self.dir = pygame.Vector2(direction[0], direction[1])
        self.radius = radius
        self.area = 4
        self.level = level + 1
        self.exploding = False
        self.explosive = modifiers["explosive"]
        self.explosion_radius = modifiers["explosion_radius"] + modifiers["power_radius"]
        self.projectile_speed = (weapon[level]["speed"] + random.choice([-1, 0, 1])) * modifiers["projectile_speed_mult"]  if self.type == "random" else weapon[level]["speed"] * modifiers["projectile_speed_mult"] 
        self.damage = (weapon[level]["damage"] + modifiers["damage"]) * modifiers["damage_mult"]
        self.lifespan = weapon[level]["lifespan"] + modifiers["projectile_lifespan"] if weapon[level]["lifespan"] is not None else None
        self.target = self.rect.center + (self.dir.normalize() * (self.radius * (1 + 0.25 * random.uniform(-1, 1))) * self.area) if self.type == "random" else None
        self.animation_frame = 0
        self.animation = 10

    def update(self, player, enemy_group):
        if self.exploding:
            if self.animation_frame > self.animation:
                self.kill()
            else:
                self.animation_frame += 1
                self.original_image = pygame.transform.scale(pygame.image.load("graphics/explosion.png").convert_alpha(), (self.explosion_radius, self.explosion_radius))
                self.image = self.original_image
                self.rect = self.image.get_rect(center=self.rect.center)
        else:
            self.move(enemy_group)
            if (abs(self.rect.centerx - player.rect.centerx) > SCREEN_WIDTH or abs(self.rect.centery - player.rect.centery) > SCREEN_HEIGHT):
                self.kill()

    def move(self, enemy_group):
        if self.type == "tracking":
            if self.target is None:
                nearest_enemy = None
                min_distance = float('inf')
                for enemy in enemy_group:
                    distance = math.hypot(self.rect.centerx - enemy.rect.centerx, self.rect.centery - enemy.rect.centery)
                    if distance < min_distance:
                        nearest_enemy = enemy
                        min_distance = distance

                if nearest_enemy is not None:
                    target_dir = pygame.math.Vector2(nearest_enemy.rect.centerx - self.rect.centerx,
                                                     nearest_enemy.rect.centery - self.rect.centery)
                    if target_dir != (0,0):
                        target_dir = target_dir.normalize()

                    angle_between = self.dir.angle_to(target_dir)
                    max_rotation = min(3, abs(angle_between))
                    self.dir.rotate_ip(max_rotation if angle_between > 0 else -max_rotation)

                self.rect.x = self.rect.x + self.dir[0] * self.projectile_speed
                self.rect.y = self.rect.y + self.dir[1] * self.projectile_speed
                
        elif self.type == "random":
            if self.target is not None:
                initial_position = self.rect.center
                distance_to_target = math.hypot(self.rect.centerx - self.target[0], self.rect.centery - self.target[1])
                speed_factor = min(1, distance_to_target / (self.radius * self.area))
                self.rect.x += (self.dir[0] * self.projectile_speed * speed_factor)
                self.rect.y += (self.dir[1] * self.projectile_speed * speed_factor)
                if self.rect.center == initial_position:
                    self.dying()
                    
        else:
            self.rect.x = self.rect.x + self.dir[0] * self.projectile_speed
            self.rect.y = self.rect.y + self.dir[1] * self.projectile_speed

        rotation_angle = math.degrees(math.atan2(-self.dir[1], self.dir[0]))
        self.image = pygame.transform.rotate(self.original_image, rotation_angle)
    
    def dying(self):
        if self.explosive:
            self.exploding = True
        else:
            self.kill()
            
    def collide(self):
        if self.lifespan is not None:
            self.lifespan -= 1
            if self.lifespan <= 0:
                self.dying()

class Orb(Projectile):
    def __init__(self, position, groups, direction, weapon, level, modifiers, radius, angle):
        super().__init__(position, groups, direction, weapon, level, modifiers, radius)
        self.angle = angle

    def update(self, player, enemy_group):
        self.move(player)
    
    def move(self, player):
        self.rect.x = player.rect.centerx + (self.radius * (1 + self.level/10)) * math.cos(self.angle)
        self.rect.y = player.rect.centery + (self.radius * (1 + self.level/10)) * math.sin(self.angle)
        self.angle -= self.projectile_speed / 30

    def collide(self):
        pass

class Player(pygame.sprite.Sprite):
    def __init__(self, position, group, character, current_map):
        super().__init__(group)
        self.current_map = current_map
        self.name =                 character["name"]
        self.max_speed =            character["speed"]
        self.armor =                character["armor"]
        self.lives =                character["lives"]
        self.health =               character["health"]
        self.damage =               character["damage"]
        self.health_regen =         character["health_regen"]
        self.weapons =              [[character["weapon"], 0]]
        self.extra_projectiles =    character["extra_projectiles"]
        self.idle_spritesheet =     get_spritesheet(character["idle_sprite"], 57)
        self.moving_spritesheet =   get_spritesheet(character["move_sprite"], 57)
        self.exp = 0
        self.level = 0
        self.money = 0
        self.exp_curve = 1.2
        self.exp_to_level = 15
        self.max_health = self.health
        self.frame = 0
        self.animation_speed = 6
        self.image = self.idle_spritesheet[0]
        self.rect = self.image.get_rect(topleft = position)
        self.invincible = False
        self.state = "idle"
        self.friction = 0.1
        self.acceleration = 0.2
        self.direction = "right"
        self.last_direction = self.direction
        self.velocity = pygame.math.Vector2(0, 0)
        self.animation = len(self.idle_spritesheet)
        self.damage_color = pygame.Color(255,0,0)
        self.passives = []
        self.modifiers = {"damage": 0,
                          "explosive": False,
                          "explosion_radius": 0,
                          "pickup_radius": 50,
                          "power_radius": 50,
                          "projectile_lifespan": 0,
                          "extra_projectiles": 0,
                          "health_regen": 0,
                          "armor": 0,
                          "luck": 0,
                          "exp_mult": 1,
                          "heal_mult": 1,
                          "gold_mult": 1,
                          "speed_mult": 1,
                          "radius_mult": 1,
                          "damage_mult": 1,
                          "cooldown_mult": 1,
                          "duration_mult": 1,
                          "invincibility_mult": 1,
                          "projectile_size_mult": 1,
                          "projectile_speed_mult": 1,
                          }
    
    def move(self):
        max_speed = self.max_speed * self.modifiers["speed_mult"]
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] and not keys[pygame.K_DOWN]:
            self.velocity.y = max(self.velocity.y - self.acceleration, -max_speed)
        elif keys[pygame.K_DOWN] and not keys[pygame.K_UP]:
            self.velocity.y = min(self.velocity.y + self.acceleration, max_speed)
        else:
            self.velocity.y *= (1 - self.friction)

        if keys[pygame.K_LEFT] and not keys[pygame.K_RIGHT]:
            self.direction = "left"
            self.velocity.x = max(self.velocity.x - self.acceleration, -max_speed)
        elif keys[pygame.K_RIGHT] and not keys[pygame.K_LEFT]:
            self.direction = "right"
            self.velocity.x = min(self.velocity.x + self.acceleration, max_speed)
        else:
            self.velocity.x *= (1 - self.friction)
        
        if not self.current_map.width - self.rect.width // 2 >= self.rect.centerx + self.velocity.x >= self.rect.width // 2:
            self.velocity.x = 0
        
        if not self.current_map.height - self.rect.height // 2 >= self.rect.centery + self.velocity.y >= self.rect.height // 2:
            self.velocity.y = 0
            
        self.rect.center += self.velocity
            
    def cast_projectile(self, weapon, level, groups):
        distance = position = (0,0)
        for i in range(0, weapon[level]["amount"] + self.modifiers["extra_projectiles"]):
            if weapon["movement"] == "random":
                distance = (random.uniform(-1, 1), random.uniform(-1, 1))
                position = (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
                
            elif weapon["movement"] == "facing":
                mouse_pos = pygame.mouse.get_pos()
                distance = (mouse_pos[0] - SCREEN_WIDTH // 2, mouse_pos[1] - SCREEN_HEIGHT // 2)
                position = (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
            
            elif weapon["movement"] == "tracking":
                distance = (random.uniform(-1, 1), random.uniform(-1, 1))
                position = (self.rect.x + self.rect.width / 2, self.rect.y + self.rect.height / 2)
            
            normal = math.sqrt(distance[0] ** 2 + distance[1] ** 2)
            direction = [distance[0] / normal, distance[1] / normal]
            Projectile(position, groups, (direction[0], direction[1]), weapon, level, self.modifiers, self.modifiers["power_radius"] * self.modifiers["radius_mult"])

    def cast_orb(self, weapon, level, groups):
        radius = self.modifiers["power_radius"] * 2 * self.modifiers["radius_mult"]
        num_points = weapon[level]["amount"] + self.modifiers["extra_projectiles"]
        for i in range(num_points):
            if weapon["movement"] == "circling":
                angle = i * (2 * math.pi) / num_points
                x = self.rect.centerx + radius * math.cos(angle)
                y = self.rect.centery + radius * math.sin(angle)
                normal = math.sqrt(x ** 2 + y ** 2)
                direction = [x / normal, y / normal]
                Orb((0, 0), groups, (direction[0], direction[1]), weapon, level, self.modifiers, radius, angle)
    
    def level_up(self):
        self.exp = 0
        self.level += 1
        self.exp_to_level = int(self.exp_to_level * self.exp_curve)
        self.current_map.set_gamestate("levelup")
    
    def collect(self, type, item):
        if type == "coin":
            self.money += math.ceil(item["value"] * self.modifiers["gold_mult"])
            
        elif type == "heart":
            self.heal(item["value"])
            
        elif type == "experience":
            self.exp += (item["value"] + self.current_map.exp_wave_offset) * self.modifiers["exp_mult"]
            if self.exp >= self.exp_to_level:
                self.level_up()
                
        elif type == "magnet":
            for pickup in self.current_map.camera_group.pickup_group:
                if pickup.magnet:
                    pickup.moving = True
        
        elif type == "chest": # Don't forget to add a visible pickup of choices when getting the chest
            upgrades = []
            amount = random.choices([1,3,5], weights=[50,30,20])[0]
            print(f'Amount: {amount}')
            for i in range(amount):
                choice = random.choice(self.current_map.available_upgrades)
                upgrades.append(choice)
                self.current_map.level_up(choice)

    def heal(self, amount):
        full_amount = math.ceil(amount * self.modifiers["heal_mult"])
        self.health = self.max_health if self.health + full_amount >= self.max_health else self.health + full_amount

    def damaged(self, damage):
        if not self.invincible:
            self.health -= max(damage - (self.armor + self.modifiers["armor"]), 0)
            invincibility_time = 500 * self.modifiers["invincibility_mult"]
            pygame.time.set_timer(99, invincibility_time)
            self.state = "damaged"
            self.invincible = True

        if self.health <= 0:
            self.lives -= 1

        if self.lives == 0:
            self.current_map.set_gamestate("mapend")

    def update(self, player, enemy_group):
        collisions = pygame.sprite.spritecollide(self, enemy_group, False)
        max_damage = 0
        self.frame += 1
        for collision in collisions:
            if collision.damage > max_damage:
                max_damage = collision.damage
        if max_damage > 0: 
            self.damaged(max_damage)
        
        if self.frame % self.animation_speed == 0:
            if self.frame / self.animation_speed > self.animation - 1:
                self.frame = 0
                    
            if self.state == "moving":
                self.image = self.idle_spritesheet[int(self.frame / self.animation_speed)].copy()
                    
            else:
                self.image = self.idle_spritesheet[int(self.frame / self.animation_speed)].copy()
            
            if self.direction == "left":
                self.image = pygame.transform.flip(self.image, True, False)
                
            if self.state == "damaged":
                fade_factor = 1 - (self.frame / self.animation_speed / self.animation)
                flash_color = pygame.Color(int(self.damage_color.r * fade_factor), int(self.damage_color.g * fade_factor), int(self.damage_color.b * fade_factor))
                flash_surface = pygame.Surface(self.rect.size, pygame.SRCALPHA)
                flash_surface.fill(flash_color)
                self.image.blit(flash_surface, (0, 0), special_flags=pygame.BLEND_RGB_ADD)
   
        self.move()

def get_spritesheet(image_name, sprite_width):
    image = pygame.image.load(image_name).convert_alpha()
    image_height = image.get_height()
    image_width = image.get_width()
    frames = []
    if image_width % sprite_width != 0:
        print(f'Error: {image} is in improper format for spritesheet')
        return frames
    
    length = int(image.get_width() / sprite_width)
    for i in range(length):
        image.set_clip(pygame.Rect(i * sprite_width, 0, sprite_width, image_height))
        sprite = image.subsurface(image.get_clip())
        frames.append(sprite)
    
    return frames