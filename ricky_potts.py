from pygame import *
from random import randint

win_width = 700
win_height = 500
display.set_caption("Ricky Potts: Space Age Ba-Ba-Bachelor Man !!")
window = display.set_mode((win_width, win_height))

img_hero         = "assets/Ricky.png"
img_enemy        = "assets/cat.png"
img_bullet       = "assets/heart.png"
img_super_bullet = "assets/eheart.png"

score, life, combo_count = 0, 3, 0
super_active, finish = False, False
super_timer, death_timer, frame_count = 0, 0, 0

mixer.init()
meow_sound     = mixer.Sound('assets/meow.mp3')
levelup_sound  = mixer.Sound('assets/levelup.mp3')

SPACE_BLACK, STAR_WHITE, NEON_WHITE, INK_BLACK = (10, 10, 30), (255, 255, 255), (220, 220, 240), (5, 5, 15)

font.init()
font1, font2 = font.Font(None, 60), font.Font(None, 36)
stars = [[randint(0, 700), randint(0, 500)] for i in range(50)]

class GameSprite(sprite.Sprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__()
        self.original_image = image.load(player_image)
        self.image = transform.scale(self.original_image, (size_x, size_y))
        self.speed = player_speed
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y = player_x, player_y

    def reset(self):
        if hasattr(self, 'is_player') and death_timer > 0 and (frame_count // 4) % 2 == 0:
            return 
        window.blit(self.image, (self.rect.x, self.rect.y))

class Player(GameSprite):
    def __init__(self, player_image, player_x, player_y, size_x, size_y, player_speed):
        super().__init__(player_image, player_x, player_y, size_x, size_y, player_speed)
        self.is_player = True

    def update(self):
        keys = key.get_pressed()
        if keys[K_UP] and self.rect.y > 5: self.rect.y -= self.speed
        if keys[K_DOWN] and self.rect.y < 500 - self.rect.height: self.rect.y += self.speed
        
        if super_active:
            s = 110 if (super_timer > 250 and (frame_count % 10) < 5) else 110
            self.image = transform.scale(self.original_image, (s, int(s * 1.2)))
        else: 
            self.image = transform.scale(self.original_image, (70, 90))
        
        old_pos = self.rect.topleft
        self.rect = self.image.get_rect()
        self.rect.topleft = old_pos

    def fire(self):
        bullets.add(Bullet(img_bullet, self.rect.right, self.rect.centery, 25, 25, 15, 0))
        
    def super_fire(self):
        bullets.add(Bullet(img_super_bullet, self.rect.right, self.rect.centery, 35, 35, 18, 0))
        bullets.add(Bullet(img_super_bullet, self.rect.right, self.rect.centery, 35, 35, 18, -5))
        bullets.add(Bullet(img_super_bullet, self.rect.right, self.rect.centery, 35, 35, 18, 5))

class Enemy(GameSprite):
    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -60:
            self.rect.x, self.rect.y = win_width + randint(50, 150), randint(50, 450)
            if not super_active: 
                global combo_count
                combo_count = 0

class Asteroid(sprite.Sprite):
    def __init__(self, x, y, speed):
        super().__init__()
        self.w, self.h = randint(45, 70), randint(35, 55)
        self.image = Surface((self.w, self.h), SRCALPHA)
        draw.ellipse(self.image, (100, 100, 110), (0, 0, self.w, self.h)) # batu
        draw.ellipse(self.image, (45, 45, 55), (0, 0, self.w, self.h), 2) # lineart
        draw.ellipse(self.image, (140, 140, 160), (self.w//4, self.h//4, self.w//3, self.h//3)) # jerawat
        self.rect = self.image.get_rect()
        self.rect.x, self.rect.y, self.speed = x, y, speed

    def update(self):
        self.rect.x -= self.speed
        if self.rect.x < -100: 
            self.rect.x, self.rect.y = win_width + randint(100, 300), randint(50, 430)

    def reset(self):
        window.blit(self.image, (self.rect.x, self.rect.y))

class Bullet(GameSprite):
    def __init__(self, img, x, y, sx, sy, spx, spy):
        super().__init__(img, x, y, sx, sy, spx)
        self.speed_y = spy
    def update(self):
        self.rect.x += self.speed
        self.rect.y += self.speed_y
        if self.rect.x > win_width or self.rect.y < 0 or self.rect.y > win_height: self.kill()

ship = Player(img_hero, 50, 250, 70, 90, 10)
monsters, asteroids, bullets = sprite.Group(), sprite.Group(), sprite.Group()
for i in range(4): monsters.add(Enemy(img_enemy, win_width + randint(50, 300), randint(50, 450), 60, 60, randint(3, 5)))
for i in range(2): asteroids.add(Asteroid(win_width + randint(300, 600), randint(50, 450), randint(4, 7)))

run = True
while run:
    for e in event.get():
        if e.type == QUIT: run = False
        elif e.type == KEYDOWN:
            if e.key == K_SPACE and not finish:
                if not super_active: ship.fire()
                else: ship.super_fire()
            if e.key == K_r and finish:
                score, life, combo_count, super_active, finish, death_timer = 0, 3, 0, False, False, 0

    if score >= 2500 and not finish:
        finish = True

    if not finish:
        frame_count += 1
        
        if super_active and (frame_count % 40) < 20:
            window.fill(NEON_WHITE); star_color = INK_BLACK
        else:
            window.fill(SPACE_BLACK); star_color = STAR_WHITE

        for star in stars:
            star[0] -= 5
            if star[0] < 0: star[0] = win_width
            draw.circle(window, star_color, (star[0], star[1]), 2)

        if combo_count >= 5 and not super_active:
            levelup_sound.play()
            super_active = True
            super_timer = 300 
            combo_count = 0

        if super_active:
            super_timer -= 1
            txt_col = (255, 20, 147) if (frame_count % 20) < 10 else (100, 100, 255)
            window.blit(font1.render('MONKEY LOVE DROP!', True, txt_col), (150, 200))
            if frame_count % 12 == 0: 
                bullets.add(Bullet(img_super_bullet, randint(0, 700), -20, 30, 30, 0, 8))
            if super_timer <= 0: super_active = False

        ship.update()
        monsters.update()
        asteroids.update()
        bullets.update()

        if sprite.groupcollide(monsters, bullets, True, True):
            meow_sound.play()
            score += 100
            if not super_active: combo_count += 1
            monsters.add(Enemy(img_enemy, win_width, randint(50, 450), 60, 60, randint(3, 6)))

        if death_timer == 0:
            hit_m = sprite.spritecollide(ship, monsters, True)
            hit_a = sprite.spritecollide(ship, asteroids, True)
            if hit_m or hit_a:
                life -= 1
                death_timer = 90
                combo_count = 0
                if hit_m: monsters.add(Enemy(img_enemy, win_width, randint(50, 450), 60, 60, randint(3, 5)))
                if hit_a: asteroids.add(Asteroid(win_width + 100, randint(50, 450), randint(4, 7)))
        else: death_timer -= 1

        ship.reset()
        monsters.draw(window)
        for a in asteroids: a.reset()
        bullets.draw(window)
        
        window.blit(font2.render("Love: " + str(score), True, star_color), (10, 10))
        window.blit(font2.render("Life: " + str(life), True, (255, 50, 50)), (10, 40))
        if not super_active: 
            window.blit(font2.render("Combo: " + str(combo_count), True, (255, 20, 147)), (10, 70))

    else:
        if life <= 0:
            window.fill(INK_BLACK)
            window.blit(font1.render('YOU LOSE!', True, (180, 0, 0)), (230, 200))
            window.blit(font2.render('Press [R] to Restart', True, STAR_WHITE), (245, 280))
        elif score >= 2500:
            window.fill((0, 150, 0))
            window.blit(font1.render('YOU WIN!', True, STAR_WHITE), (230, 180))
            window.blit(font2.render('Ricky Berhasil Menyebarkan Kasih Sayang!', True, STAR_WHITE), (100, 260))
            window.blit(font2.render('Tekan [R] untuk Main Lagi', True, STAR_WHITE), (220, 310))

    display.update()
    time.delay(30)