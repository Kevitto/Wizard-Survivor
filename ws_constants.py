#!/usr/bin/python3
SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
EXTRAS = { "200 Coins": {"image": "graphics/coin_large.png",
                "description": "Two hundred smackaroos!"}
            }
WEAPONS = { "Poison Shot": {"type": "projectile",
                "movement": "facing",
                "image": "graphics/poisonshot.png",
                "sprite": "graphics/poisonshot_sprite.png",
                "description": "Shoots where you point, poisons enemies!  Simple as that!",
                    0: {"cooldown": 500, "damage": 2, "lifespan": 1, "speed": 5, "amount": 1},
                    1: {"cooldown": 500, "damage": 2, "lifespan": 1, "speed": 5, "amount": 2},
                    2: {"cooldown": 500, "damage": 3, "lifespan": 1, "speed": 5, "amount": 3},
                    3: {"cooldown": 500, "damage": 3, "lifespan": 1, "speed": 6, "amount": 4},
                    4: {"cooldown": 500, "damage": 4, "lifespan": 1, "speed": 6, "amount": 5},
                    5: {"cooldown": 500, "damage": 4, "lifespan": 1, "speed": 6, "amount": 6}
            },
            "Firespin": {"type": "orb",
                "movement": "circling",
                "image": "graphics/firespin.png",
                "sprite": "graphics/firespin_sprite.png",
                "description": "Does little circly thingies!",
                    0: {"cooldown": 100, "damage": 2, "lifespan": None, "speed": 1, "amount": 3},
                    1: {"cooldown": 100, "damage": 3, "lifespan": None, "speed": 1, "amount": 3},
                    2: {"cooldown": 100, "damage": 3, "lifespan": None, "speed": 1, "amount": 4},
                    3: {"cooldown": 100, "damage": 4, "lifespan": None, "speed": 2, "amount": 4},
                    4: {"cooldown": 100, "damage": 4, "lifespan": None, "speed": 2, "amount": 5},
                    5: {"cooldown": 100, "damage": 5, "lifespan": None, "speed": 2, "amount": 5}
            },
            "Emerett's Eye": {"type": "projectile",
                "movement": "tracking",
                "image": "graphics/emerettseye.png",
                "sprite": "graphics/emerettseye_sprite.png",
                "description": "Follows those fuckers...",
                    0: {"cooldown": 2000, "damage": 2, "lifespan": 1, "speed": 3, "amount": 1},
                    1: {"cooldown": 2000, "damage": 3, "lifespan": 1, "speed": 3, "amount": 1},
                    2: {"cooldown": 2000, "damage": 3, "lifespan": 1, "speed": 3, "amount": 1},
                    3: {"cooldown": 2000, "damage": 4, "lifespan": 1, "speed": 4, "amount": 1},
                    4: {"cooldown": 2000, "damage": 4, "lifespan": 1, "speed": 4, "amount": 1},
                    5: {"cooldown": 2000, "damage": 5, "lifespan": 1, "speed": 5, "amount": 1}
            },
            "Sticky Mess": {"type": "projectile",
                "movement": "random",
                "image": "graphics/stickymess.png",
                "sprite": "graphics/stickymess_sprite.png",
                "description": "Goes all willy-nilly, but there's lots!",
                    0: {"cooldown": 1000, "damage": 2, "lifespan": 1, "speed": 5, "amount": 5},
                    1: {"cooldown": 1000, "damage": 2, "lifespan": 1, "speed": 5, "amount": 5},
                    2: {"cooldown": 1000, "damage": 3, "lifespan": 1, "speed": 5, "amount": 6},
                    3: {"cooldown": 1000, "damage": 3, "lifespan": 1, "speed": 6, "amount": 6},
                    4: {"cooldown": 1000, "damage": 4, "lifespan": 1, "speed": 6, "amount": 7},
                    5: {"cooldown": 1000, "damage": 5, "lifespan": 1, "speed": 6, "amount": 8}
                }
            }
PASSIVES = {"Elixir of Chaos": {"type": "passive",
                "image": "graphics/explosive.png",
                "description": "Kaboom!",
                    0: {"explosive": True, "explosion_radius": 2, "description": "Grants explosive to all projectiles."},
                    1: {"explosive": True, "explosion_radius": 3, "description": "Increases explosion radius."},
                    2: {"explosive": True, "explosion_radius": 4, "description": "Increases explosion radius."},
                    3: {"explosive": True, "explosion_radius": 5, "description": "Increases explosion radius."},
                    4: {"explosive": True, "explosion_radius": 7, "description": "Increases explosion radius."},
                    5: {"explosive": True, "explosion_radius": 10, "description": "Increases explosion radius."},
                },
            "Elixir of Speed": {"type": "passive",
                "image": "graphics/speedup.png",
                "description": "Run faster, jump higher!",
                    0: {"speed": 1.1, "description": "Increase player speed by 10%."},
                    1: {"speed": 1.2, "description": "Increase player speed by 20%."},
                    2: {"speed": 1.3, "description": "Increase player speed by 30%."},
                    3: {"speed": 1.4, "description": "Increase player speed by 40%."},
                    4: {"speed": 1.5, "description": "Increase player speed by 50%."},
                    5: {"speed": 1.6, "description": "Increase player speed by 60%."},
                },
            "Elixir of Stone": {"type": "passive",
                "image": "graphics/penetrate.png",
                "description": "Many more hits.",
                    0: {"projectile_lifespan": 1, "description": "All projectiles penetrate."},
                    1: {"projectile_lifespan": 1, "description": "All projectiles penetrate."},
                    2: {"projectile_lifespan": 2, "description": "All projectiles penetrate more."},
                    3: {"projectile_lifespan": 2, "description": "All projectiles penetrate more."},
                    4: {"projectile_lifespan": 3, "description": "All projectiles penetrate even more."},
                    5: {"projectile_lifespan": 99, "description": "All projectiles are indestructible."},
                },
            "Amethyst Ring": {"type": "passive",
                "image": "graphics/speedup.png",
                "description": "More firepower.",
                    0: {"extra_projectiles": 1, "description": "Adds an extra projectile."},
                    1: {"extra_projectiles": 2, "description": "Adds two extra projectiles."},
                    2: {"extra_projectiles": 3, "description": "Adds three extra projectiles."},
                    3: {"extra_projectiles": 4, "description": "Adds four extra projectiles."},
                    4: {"extra_projectiles": 5, "description": "Adds five extra projectiles."},
                    5: {"extra_projectiles": 6, "description": "Adds six extra projectiles."},
                },
            "Ring of Power": {"type": "passive",
                "image": "graphics/speedup.png",
                "description": "Make them hurt.",
                    0: {"damage": 1, "description": "Increase base damage by 1."},
                    1: {"damage": 2, "description": "Increase base damage by 2."},
                    2: {"damage": 3, "description": "Increase base damage by 3."},
                    3: {"damage": 4, "description": "Increase base damage by 4."},
                    4: {"damage": 5, "description": "Increase base damage by 5."},
                    5: {"damage": 6, "description": "Increase base damage by 6."},
                },
            "Ring of Growth": {"type": "passive",
                "image": "graphics/speedup.png",
                "description": "Get bigger, faster!",
                    0: {"exp_mult": 1.25, "gold_mult": 1.25, "description": "Increase all experience and gold gains by 25%."},
                    1: {"exp_mult": 1.5, "gold_mult": 1.5, "description": "Increase all experience and gold gains by 50%."},
                    2: {"exp_mult": 1.75, "gold_mult": 1.75, "description": "Increase all experience and gold gains by 75%."},
                    3: {"exp_mult": 2.0, "gold_mult": 2.0, "description": "Increase all experience and gold gains by 100%."},
                    4: {"exp_mult": 2.5, "gold_mult": 2.5, "description": "Increase all experience and gold gains by 150%."},
                    5: {"exp_mult": 3.0, "gold_mult": 3.0, "description": "Increase all experience and gold gains by 200%."},
                },
            "Spell Tome Vol.II": {"type": "passive",
                "image": "graphics/speedup.png",
                "description": "Better spells.",
                    0: {"projectile_size_mult": 1.2, "description": "Increases projectile size by 20%."},
                    1: {"projectile_speed_mult": 1.2, "description": "Projectiles are 20% faster."},
                    2: {"projectile_size_mult": 1.5, "description": "Increases projectile size by 50%."},
                    3: {"projectile_speed_mult": 1.5, "description": "Projectiles are 50% faster."},
                    4: {"projectile_size_mult": 2.0, "description": "Doubles projectile size."},
                    5: {"projectile_speed_mult": 2.0, "description": "Doubles projectile speed."},
                },
            }
ENEMIES = {"Drone":    {"type": "standard",
                        "image": "graphics/enemy.png",
                        "movement": "follow",
                        "damage": 15,
                        "health": 3,
                        "speed": 1},
           "Worker":   {"type": "fast",
                        "image": "graphics/enemy2.png",
                        "movement": "dash",
                        "damage": 20,
                        "health": 2,
                        "speed": 3},
           "Tank":     {"type": "tank",
                        "image": "graphics/enemy3.png",
                        "movement": "follow",
                        "damage": 25,
                        "health": 10,
                        "speed": 1},
           }
BOSSES =  {"Drone":    {"type": "standard",
                        "image": "graphics/enemy.png",
                        "movement": "follow",
                        "damage": 20,
                        "health": 3,
                        "speed": 1},
           "Worker":   {"type": "fast",
                        "image": "graphics/enemy2.png",
                        "movement": "dash",
                        "damage": 30,
                        "health": 2,
                        "speed": 3},
           "Tank":     {"type": "tank",
                        "image": "graphics/enemy3.png",
                        "movement": "follow",
                        "damage": 50,
                        "health": 10,
                        "speed": 1},
           }
PICKUPS = {"nothing": {"image": None,
                       "weight": 5,
                       "magnet": False,
                       "value": "0"},
           "heart": {"image": "graphics/heart.png",
                     "weight": 1,
                     "magnet": False,
                     "value": 10},
           "coin": {"image": "graphics/coin.png",
                    "weight": 34,
                    "magnet": True,
                    "value": 2},
           "experience": {"image": "graphics/exp.png",
                          "weight": 59,
                          "magnet": True,
                          "value": 3},
           "magnet": {"image": "graphics/magnet.png",
                      "weight": 1,
                      "magnet": False,
                      "value": None},
            "chest": {"image": "graphics/chest.png",
                      "weight": 0,
                      "magnet": False,
                      "value": None}
           }
MAPS = {"1": {"timeout": 5,
                "background": 'graphics/ground.png',
                "bgcolor": '#000000',
                "width": 4000,
                "height": 4000,
                "enemies": [ENEMIES["Drone"], 
                            ENEMIES["Worker"], 
                            ENEMIES["Tank"]],
                "minibosses": [BOSSES["Drone"]],
                "boss": BOSSES["Drone"],
                "waves": {1: [(0,2), (0,0), (0,0)],
                          2: [(2,4), (0,0), (0,1)],
                          3: [(2,4), (0,0), (1,3)],
                          4: [(2,5), (0,0), (2,4)],
                          5: [(0,0), (5,6), (0,0)]},},
        "2": {"timeout": 5,
                "background": 'graphics/ground.png',
                "bgcolor": '#ffffff',
                "width": 2000,
                "height": 2000,
                "enemies": [ENEMIES["Drone"], 
                            ENEMIES["Worker"], 
                            ENEMIES["Tank"]],
                "minibosses": [],
                "bosses": [],
                "waves": {1: [(0,2), (0,0), (0,0)],
                          2: [(2,4), (0,0), (0,1)],
                          3: [(2,4), (0,0), (1,3)],
                          4: [(2,5), (0,0), (2,4)],
                          5: [(0,0), (5,6), (0,0)]},}
           }
CHARACTERS = {"Wizard Bob": 
                {"name": "Wizard Bob",
                 "idle_sprite": "graphics/player_spritesheet.png",
                 "move_sprite": "graphics/player_spritesheet.png",
                 "health": 100,
                 "health_regen": 0,
                 "armor": 1,
                 "speed": 2.0,
                 "damage": 1,
                 "extra_projectiles": 0,
                 "weapon": "Firespin",
                 "lives": 1,
                 }
           }