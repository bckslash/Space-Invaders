import pygame 
import os, time, random

pygame.font.init()

WIDTH, HEIGHT = 750, 700
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Space Invaders")
FPS = 60
VELOCITY = 6
# fonts
FONT_DEFAULT_SIZE = 60
FONT_DEFAULT = pygame.font.SysFont('comicsans', FONT_DEFAULT_SIZE)
FONT_GAMEOVER = pygame.font.SysFont('comicsans', 120)

# colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
YELLOW = (255, 255, 0)
PURPLE = (153, 50, 204)
GRAY = (92, 92, 92)
ORANGE = (255, 127, 0)
MILK = (194, 194, 197)
GREEN = (0, 255, 0)

# load assets
IMAGE_SHIP_MAIN = pygame.image.load(os.path.join('Assets', 'ship.png'))
SHIP_MAIN = pygame.transform.scale(pygame.transform.rotate(IMAGE_SHIP_MAIN, 0), (100, 90))

IMAGE_SHIP_RED = pygame.image.load(os.path.join('Assets', 'pixel_ship_red_small.png'))
SHIP_RED = pygame.transform.rotate(IMAGE_SHIP_RED, 180)

IMAGE_SHIP_GREEN = pygame.image.load(os.path.join('Assets', 'pixel_ship_green_small.png'))
SHIP_GREEN = pygame.transform.rotate(IMAGE_SHIP_GREEN, 180)

IMAGE_SHIP_BLUE = pygame.image.load(os.path.join('Assets', 'pixel_ship_blue_small.png'))
SHIP_BLUE = pygame.transform.rotate(IMAGE_SHIP_BLUE, 180)

IMAGE_BACKGROUND = pygame.transform.scale(pygame.image.load(
os.path.join('Assets', 'background-black.png')), (WIDTH, HEIGHT))

IMAGE_LASER_YELLOW = pygame.image.load(os.path.join('Assets', 'pixel_laser_yellow.png'))
IMAGE_LASER_RED = pygame.image.load(os.path.join('Assets', 'pixel_laser_red.png'))
IMAGE_LASER_GREEN = pygame.image.load(os.path.join('Assets', 'pixel_laser_green.png'))
IMAGE_LASER_BLUE = pygame.image.load(os.path.join('Assets', 'pixel_laser_red.png'))

class Laser:
    def __init__(self, x, y, img):
        self.x = x
        self.y = y
        self.img = img
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        window.blit(self.img, (self.x, self.y))

    def move(self, vel):
        self.y += vel
    
    def off_screen(self, height):
        return not (self.y <= height+200 and self.y >= -200)

    def collision(self, obj):
        return collide(obj, self)

class Ship:
    COOLDOWN = 10

    def __init__(self, x, y, health=100):
        self.x = x
        self.y = y
        self.health = health
        self.ship_img = None
        self.laser_img = None
        self.lasers = []
        self.cool_down_counter = 0
    
    def draw(self, window):
        window.blit(self.ship_img, (self.x, self.y))
        for laser in self.lasers:
            laser.draw(window)

    def move_lasers(self, vel, obj):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            elif laser.collision(obj):
                obj.health -= 10
                self.lasers.remove(laser)

    def cooldown(self):
        if self.cool_down_counter >= self.COOLDOWN:
            self.cool_down_counter = 0
        elif self.cool_down_counter > 0:
            self.cool_down_counter += 1

    def shoot(self):
        if self.cool_down_counter == 0:
            laser = Laser(self.x, self.y, self.laser_img)
            self.lasers.append(laser)
            self.cool_down_counter = 1

    def get_width(self):
        return self.ship_img.get_width()
    
    def get_height(self):
        return self.ship_img.get_height()

class Player(Ship):
    def __init__(self, x, y, health=100):
        super().__init__(x, y, health)
        self.ship_img = SHIP_MAIN
        self.laser_img = IMAGE_LASER_YELLOW
        self.mask = pygame.mask.from_surface(self.ship_img)
        self.max_health = health

    def move_lasers(self, vel, objs):
        self.cooldown()
        for laser in self.lasers:
            laser.move(vel)
            if laser.off_screen(HEIGHT):
                self.lasers.remove(laser)
            else:
                for obj in objs:
                    if laser.collision(obj):
                        if obj in objs: objs.remove(obj)
                        if laser in self.lasers: self.lasers.remove(laser)

    def draw(self, window):
        super().draw(window)
        self.healthbar(window)

    def healthbar(self, window):
        pygame.draw.rect(window, RED, (self.x, self.y+self.ship_img.get_height()+10, self.ship_img.get_width(), 10))
        pygame.draw.rect(window, GREEN, (self.x, self.y+self.ship_img.get_height()+10, self.ship_img.get_width() * (self.health/self.max_health), 10))


class Enemy(Ship):
    COLOR_MAP = {
            "red" : (SHIP_RED, IMAGE_LASER_RED),
            "green" : (SHIP_GREEN, IMAGE_LASER_GREEN),
            "blue" : (SHIP_BLUE, IMAGE_LASER_BLUE) 
    }

    def __init__(self, x, y, color, health=100):
        super().__init__(x, y, health)
        self.ship_img, self.laser_img = self.COLOR_MAP[color]
        self.mask = pygame.mask.from_surface(self.ship_img)

    def move(self, vel):
        self.y += vel

def handle_movement(keys_pressed, ship):
    if keys_pressed[pygame.K_a] and ship.x - VELOCITY > 0:  # LEFT
        ship.x -= VELOCITY
    if keys_pressed[pygame.K_d] and ship.x + VELOCITY + ship.get_width() < WIDTH:  # RIGHT
        ship.x += VELOCITY
    if keys_pressed[pygame.K_w] and ship.y - VELOCITY > 0:  # UP
        ship.y -= VELOCITY
    if keys_pressed[pygame.K_s] and ship.y + VELOCITY + ship.get_height() < HEIGHT:  # DOWN
        ship.y += VELOCITY

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def main():
    clock = pygame.time.Clock()
    run = True
    level = 0
    lives = 10
    enemy_velocity = 1
    laser_velocity = 9
    enemy_spawn_zone = 0
    lost = False
    lost_count = 0

    enemies = []
    wave_lenght = 0

    player = Player(random.randint(0, WIDTH-120),HEIGHT-120)

    def redraw_window():
        WIN.fill(PURPLE)
        WIN.blit(IMAGE_BACKGROUND, (WIDTH//2 - IMAGE_BACKGROUND.get_width()//2 , HEIGHT//2 - IMAGE_BACKGROUND.get_height()//2))
        
        #draw enemy ships
        for enemy in enemies:
            enemy.draw(WIN)

        #draw player ship
        player.draw(WIN)

        # create text and shadow
        text_lives = FONT_DEFAULT.render("Lives: {}".format(lives), 1, ORANGE)
        shadow_text_lives = FONT_DEFAULT.render("Lives: {}".format(lives), 1, GRAY)

        text_level = FONT_DEFAULT.render("Level: {}".format(str(level)), 1, ORANGE)
        shadow_text_level = FONT_DEFAULT.render("Level: {}".format(str(level)), 1, GRAY)

        # place text and shadow
        shadow_offset = FONT_DEFAULT_SIZE // 20
        WIN.blit(shadow_text_lives, (10+shadow_offset, 10+shadow_offset))
        WIN.blit(text_lives, (10,10))

        WIN.blit(shadow_text_level, (WIDTH-text_level.get_width()-10+shadow_offset, 10+shadow_offset))
        WIN.blit(text_level, (WIDTH-text_level.get_width()-10, 10))

        shadow_text_gameover = FONT_GAMEOVER.render("GAMEOVER!", 1, GRAY)
        text_gameover = FONT_GAMEOVER.render("GAMEOVER!", 1, ORANGE)
        if lost == True:
            WIN.blit(shadow_text_gameover, (WIDTH//2-text_gameover.get_width() //2+shadow_offset, HEIGHT//2-text_gameover.get_height()//2+shadow_offset))
            WIN.blit(text_gameover, (WIDTH//2-text_gameover.get_width()//2, HEIGHT//2-text_gameover.get_height()//2))

        pygame.display.update()

    while(run):
        clock.tick(FPS)
        redraw_window()

        if lives <= 0 or player.health <= 0:
            lost = True
            lost_count += 1

        if lost:
            if lost_count > FPS * 3:
                run = False
            else: continue

        if len(enemies) == 0:
            level += 1
            wave_lenght += 5
            if level == 5: enemy_velocity += 1
            enemy_spawn_zone -= 150
            for i in range(wave_lenght):
                enemy = Enemy(random.randrange(10, WIDTH-100), random.randrange(enemy_spawn_zone, 0), random.choice(["red", "green", "blue"]))
                enemies.append(enemy)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
        
        keys_pressed = pygame.key.get_pressed()
        handle_movement(keys_pressed, player)

        # shoot laser
        if keys_pressed[pygame.K_SPACE]:
            player.shoot()

        for enemy in enemies[:]:
            enemy.move(enemy_velocity)
            enemy.move_lasers(laser_velocity, player)

            if random.randrange(0, 8*FPS) == 1:
                enemy.shoot()

            if collide(enemy, player):
                player.health -= 10
                if enemy in enemies: enemies.remove(enemy)

            if enemy.y + enemy.get_height() > HEIGHT:
                lives -= 1
                enemies.remove(enemy)
        
            for player_laser in player.lasers:
                for enemy_laser in enemy.lasers:
                    if collide(player_laser, enemy_laser):
                        enemy.lasers.remove(enemy_laser)
                        player.lasers.remove(player_laser)

        player.move_lasers(-laser_velocity, enemies)

def main_menu():
    run = True
    FONT_TITLE = pygame.font.SysFont('comicsans', 130)

    while run:
        WIN.blit(IMAGE_BACKGROUND, (WIDTH//2 - IMAGE_BACKGROUND.get_width() //2, HEIGHT//2 - IMAGE_BACKGROUND.get_height()//2))
        text_menu = FONT_TITLE.render("Press to START", 1, PURPLE)
        shadow_text_menu = FONT_TITLE.render("Press to START", 1, GRAY)
        WIN.blit(shadow_text_menu, (WIDTH//2-text_menu.get_width()//2 + 5, HEIGHT//2-text_menu.get_height()//2 + 5))
        WIN.blit(text_menu, (WIDTH//2-text_menu.get_width()//2, HEIGHT//2-text_menu.get_height()//2))
        pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
            if event.type == pygame.MOUSEBUTTONDOWN:
                main()

    pygame.quit()

if __name__ == "__main__":
    main_menu()
