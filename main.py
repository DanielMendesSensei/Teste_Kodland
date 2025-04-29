import pgzrun
import random
from pygame import Rect

# Constants
WIDTH = 800
HEIGHT = 600
TITLE = "Just Jump"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
BLUE = (0, 100, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)

# Game states
MENU = 0
PLAYING = 1
GAME_OVER = 2

# Initialize variables
game_state = MENU
sound_enabled = True
platforms = []
enemies = []
score = 0
level = 1
end_portal = None


# Create player
class Player:
    def __init__(self):
        self.width = 27
        self.height = 39
        self.x = 100
        self.y = HEIGHT - self.height - 10
        self.x_speed = 0
        self.y_speed = 0
        self.jump_power = -15
        self.gravity = 0.8
        self.is_jumping = False
        self.is_on_ground = False
        self.direction = 1  # 1 for right, -1 for left
        self.animation_index = 0
        self.animation_timer = 0

        # Sprites for right direction (original)
        self.idle_sprites_right = [
            "hero_idle1",
            "hero_idle2",
            "hero_idle3",
            "hero_idle4",
            "hero_idle5",
        ]
        self.run_sprites_right = [
            "hero_run1",
            "hero_run2",
            "hero_run3",
            "hero_run4",
            "hero_run5",
            "hero_run6",
            "hero_run7",
            "hero_run8",
        ]

        # Sprites for left direction (mirrored)
        self.idle_sprites_left = [
            "hero_idle1_left",
            "hero_idle2_left",
            "hero_idle3_left",
            "hero_idle4_left",
            "hero_idle5_left",
        ]
        self.run_sprites_left = [
            "hero_run1_left",
            "hero_run2_left",
            "hero_run3_left",
            "hero_run4_left",
            "hero_run5_left",
            "hero_run6_left",
            "hero_run7_left",
            "hero_run8_left",
        ]

        # Transition sprites
        self.turn_right_sprite = "hero_turn_right"  # Sprite for turning right
        self.turn_left_sprite = "hero_turn_left"  # Sprite for turning left

        # Transition state
        self.is_turning = False
        self.turn_timer = 0
        self.turn_duration = 8  # Duration of turning animation in frames
        self.turn_target = 1  # Target direction after turning

        # Current sprites
        self.idle_sprites = self.idle_sprites_right
        self.run_sprites = self.run_sprites_right
        self.current_sprite = self.idle_sprites[0]

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def update(self):
        # Apply gravity
        self.y_speed += self.gravity

        # Update position
        self.x += self.x_speed
        self.y += self.y_speed

        # Boundary checking
        if self.x < 0:
            self.x = 0
        if self.x > WIDTH - self.width:
            self.x = WIDTH - self.width

        # Check if on ground or platform
        self.is_on_ground = False
        if self.y >= HEIGHT - self.height:
            self.y = HEIGHT - self.height
            self.y_speed = 0
            self.is_jumping = False
            self.is_on_ground = True

        # Check platform collisions
        for platform in platforms:
            if (
                self.get_rect().colliderect(platform.get_rect())
                and self.y_speed > 0
                and self.y + self.height < platform.y + 20
            ):
                self.y = platform.y - self.height
                self.y_speed = 0
                self.is_jumping = False
                self.is_on_ground = True

        # Manage turning animation
        if self.is_turning:
            self.turn_timer += 1
            if self.turn_timer >= self.turn_duration:
                # Completed turning
                self.is_turning = False
                self.direction = self.turn_target

                # Update sprite set based on direction
                if self.direction > 0:  # Turned right
                    self.idle_sprites = self.idle_sprites_right
                    self.run_sprites = self.run_sprites_right
                else:  # Turned left
                    self.idle_sprites = self.idle_sprites_left
                    self.run_sprites = self.run_sprites_left
        else:
            # Normal animation (only if not turning)
            self.animation_timer += 1
            if self.animation_timer >= 8:  # Change sprite every 8 frames
                self.animation_timer = 0
                if abs(self.x_speed) > 0.5:  # If moving
                    self.animation_index = (self.animation_index + 1) % len(self.run_sprites)
                    self.current_sprite = self.run_sprites[self.animation_index]
                else:  # If idle
                    self.animation_index = (self.animation_index + 1) % len(self.idle_sprites)
                    self.current_sprite = self.idle_sprites[self.animation_index]

    def jump(self):
        if not self.is_jumping and self.is_on_ground:
            self.y_speed = self.jump_power
            self.is_jumping = True
            if sound_enabled:
                sounds.jump.play()

    def move(self, direction):
        # If not moving
        if direction == 0:
            self.x_speed = 0
            return

        # If changing direction and not in transition
        if direction != self.direction and not self.is_turning and self.direction != 0:
            self.is_turning = True
            self.turn_timer = 0
            self.turn_target = direction
            self.x_speed = 0  # Stop during turning
        else:
            # If not in transition, move normally
            if not self.is_turning:
                self.x_speed = direction * 5
                self.direction = direction

    def draw(self):
        if self.is_turning:
            # Choose appropriate transition sprite
            if self.turn_target == 1:  # Turning right
                screen.blit(self.turn_right_sprite, (self.x, self.y))
            else:  # Turning left
                screen.blit(self.turn_left_sprite, (self.x, self.y))
        else:
            # Normal drawing of current sprite
            screen.blit(self.current_sprite, (self.x, self.y))


# Create enemy class
class Enemy:
    def __init__(self, x, y, patrol_start, patrol_end):
        self.x = x
        self.y = y
        self.width = 50
        self.height = 40
        self.speed = random.uniform(1, 3)
        self.patrol_start = patrol_start
        self.patrol_end = patrol_end
        self.direction = 1  # 1 for right, -1 for left
        self.animation_index = 0
        self.animation_timer = 0

        # Sprites for right and left
        self.sprites_right = ["enemy_move1"]
        self.sprites_left = ["enemy_move1_left"]
        self.sprites = self.sprites_right
        self.current_sprite = self.sprites[0]

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def update(self):
        # Move enemy
        self.x += self.speed * self.direction

        # Check patrol boundaries
        if self.x <= self.patrol_start:
            self.x = self.patrol_start
            self.direction = 1
            self.sprites = self.sprites_right
        elif self.x >= self.patrol_end - self.width:
            self.x = self.patrol_end - self.width
            self.direction = -1
            self.sprites = self.sprites_left

        # Animation logic
        self.animation_timer += 1
        if self.animation_timer >= 8:  # Change sprite every 8 frames
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.sprites)
            self.current_sprite = self.sprites[self.animation_index]

    def draw(self):
        screen.blit(self.current_sprite, (self.x, self.y))


# Create platform class
class Platform:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def draw(self):
        screen.draw.filled_rect(self.get_rect(), GREEN)


# Create portal class for level completion
class Portal:
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.width = 40
        self.height = 60
        self.animation_index = 0
        self.animation_timer = 0
        self.sprites = ["portal1", "portal2", "portal3", "portal4"]
        self.current_sprite = self.sprites[0]

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def update(self):
        self.animation_timer += 1
        if self.animation_timer >= 10:
            self.animation_timer = 0
            self.animation_index = (self.animation_index + 1) % len(self.sprites)
            self.current_sprite = self.sprites[self.animation_index]

    def draw(self):
        screen.blit(self.current_sprite, (self.x, self.y))


# Create Button class for menu
class Button:
    def __init__(self, x, y, width, height, text, action):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.action = action
        self.is_hovered = False

    def get_rect(self):
        return Rect(self.x, self.y, self.width, self.height)

    def check_hover(self, pos):
        self.is_hovered = self.get_rect().collidepoint(pos)
        return self.is_hovered

    def draw(self):
        color = BLUE if self.is_hovered else BLACK
        screen.draw.filled_rect(self.get_rect(), color)
        screen.draw.rect(self.get_rect(), WHITE)
        screen.draw.text(
            self.text,
            center=(self.x + self.width // 2, self.y + self.height // 2),
            color=WHITE,
            fontsize=30,
        )


# Initialize player
player = Player()


# Helper functions
def toggle_sound():
    global sound_enabled
    sound_enabled = not sound_enabled
    sound_button.text = "Sound: ON" if sound_enabled else "Sound: OFF"

    if sound_enabled:
        music.play("game_music" if game_state == PLAYING else "menu_music")
    else:
        music.stop()


# Create menu buttons
start_button = Button(
    WIDTH // 2 - 100, HEIGHT // 2 - 60, 200, 50, "Start Game", lambda: set_game_state(PLAYING)
)
sound_button = Button(WIDTH // 2 - 100, HEIGHT // 2, 200, 50, "Sound: ON", toggle_sound)
exit_button = Button(WIDTH // 2 - 100, HEIGHT // 2 + 60, 200, 50, "Exit", exit)
menu_buttons = [start_button, sound_button, exit_button]


# Initialize level
def init_level():
    global platforms, enemies, player, end_portal, score, level

    # Reset player position
    player.x = 100
    player.y = HEIGHT - player.height - 10
    player.x_speed = 0
    player.y_speed = 0

    # Clear previous level
    platforms.clear()
    enemies.clear()

    # Create ground platform
    platforms.append(Platform(0, HEIGHT - 10, WIDTH, 10))

    # Create platforms with better distribution
    platform_count = 5 + level

    # Calculate maximum jump height
    # The player can jump ~(jump_power^2)/(2*gravity) pixels high
    max_jump_height = int((player.jump_power**3) / (2 * player.gravity))

    # Start with a platform within jumping distance from the ground
    last_y = HEIGHT - 10  # Ground level

    for i in range(platform_count):
        x = random.randint(50, WIDTH - 150)

        # For the first few platforms, ensure they're reachable
        if i < 3:  # First few platforms are guaranteed to be accessible
            # Calculate a y position that is reachable from the last platform
            min_height = max(150, last_y - max_jump_height)
            max_height = min(last_y - 40, HEIGHT - 100)

            # Check if we have a valid range
            if min_height >= max_height:
                min_height = max_height - 30  # Ensure at least a 30 pixel difference

            y = random.randint(min_height, max_height)
        else:
            # Later platforms can be more challenging but still within reason
            min_height = max(150, last_y - max_jump_height - 50)
            max_height = min(HEIGHT - 100, last_y - 30)

            # Check if we have a valid range
            if min_height >= max_height:
                min_height = max_height - 30  # Ensure at least a 30 pixel difference

            # If we still don't have a valid range, adjust further
            if min_height >= max_height:
                y = min_height  # Just use the minimum height as a fallback
            else:
                y = random.randint(min_height, max_height)

        width = random.randint(100, 200)
        platforms.append(Platform(x, y, width, 20))

        # Update last platform y position (used for the next platform)
        last_y = y

    # Create enemies
    enemy_count = 2 + level // 2
    for i in range(enemy_count):
        # Place enemies on platforms or ground
        platform = random.choice(platforms)
        x = random.randint(int(platform.x), int(platform.x + platform.width - 50))
        y = platform.y - 40  # Place enemy on top of platform
        patrol_start = max(platform.x, x - 100)
        patrol_end = min(platform.x + platform.width, x + 100)
        enemies.append(Enemy(x, y, patrol_start, patrol_end))

    # Create end portal on a random platform (preferably not the first ones)
    # This encourages players to explore higher platforms
    available_platforms = platforms[3:] if len(platforms) > 3 else platforms[1:]
    portal_platform = random.choice(available_platforms)  # Skip ground and first platforms
    portal_x = portal_platform.x + portal_platform.width // 2 - 20
    portal_y = portal_platform.y - 60
    end_portal = Portal(portal_x, portal_y)


# Helper functions
def set_game_state(state):
    global game_state, score, level
    game_state = state

    if state == PLAYING:
        # Only reset score and level when starting a new game, not when game over
        if game_state != GAME_OVER:
            score = 0
            level = 1
        init_level()
        if sound_enabled:
            music.play("game_music")
    elif state == MENU:
        if sound_enabled:
            music.play("menu_music")


def next_level():
    global level, score
    level += 1
    score += 100 * level
    if sound_enabled:
        sounds.levelup.play()
    init_level()


# Pygame Zero Functions
def draw():
    screen.fill((50, 50, 100))

    if game_state == MENU:
        # Draw menu
        screen.draw.text(TITLE, center=(WIDTH // 2, HEIGHT // 4), color=WHITE, fontsize=60)
        for button in menu_buttons:
            button.draw()

    elif game_state == PLAYING:
        # Draw platforms
        for platform in platforms:
            platform.draw()

        # Draw portal
        end_portal.draw()

        # Draw enemies
        for enemy in enemies:
            enemy.draw()

        # Draw player
        player.draw()

        # Draw score and level
        screen.draw.text(f"Score: {score}", topleft=(10, 10), color=WHITE, fontsize=24)
        screen.draw.text(f"Level: {level}", topright=(WIDTH - 10, 10), color=WHITE, fontsize=24)

    elif game_state == GAME_OVER:
        screen.draw.text("GAME OVER", center=(WIDTH // 2, HEIGHT // 3), color=WHITE, fontsize=60)
        screen.draw.text(
            f"Final Score: {score}", center=(WIDTH // 2, HEIGHT // 2), color=WHITE, fontsize=30
        )
        screen.draw.text(
            "Click to return to menu",
            center=(WIDTH // 2, HEIGHT * 2 // 3),
            color=WHITE,
            fontsize=24,
        )


def update():
    # Handle continuous key presses
    if game_state == PLAYING:
        # Horizontal movement - checks each key independently
        if keyboard.left and not keyboard.right:
            player.move(-1)
        elif keyboard.right and not keyboard.left:
            player.move(1)
        else:
            player.move(0)

        # Check jump continuously
        if (keyboard.space or keyboard.up) and not player.is_jumping and player.is_on_ground:
            player.jump()

        # Update player
        player.update()

        # Update portal
        end_portal.update()

        # Check if player reached portal
        if player.get_rect().colliderect(end_portal.get_rect()):
            next_level()

        # Update enemies
        for enemy in enemies:
            enemy.update()

            # Check collision with player
            if player.get_rect().colliderect(enemy.get_rect()):
                if sound_enabled:
                    sounds.hit.play()
                set_game_state(GAME_OVER)
                # We don't reset score and level here, only when starting a new game


def on_mouse_move(pos):
    if game_state == MENU:
        for button in menu_buttons:
            button.check_hover(pos)


def on_mouse_down(pos, button):
    if game_state == MENU:
        for btn in menu_buttons:
            if btn.check_hover(pos):
                btn.action()

    elif game_state == GAME_OVER:
        set_game_state(MENU)


def on_key_down(key):
    if game_state == PLAYING:
        if key == keys.SPACE or key == keys.UP:
            player.jump()


# Start the game with menu music
if sound_enabled:
    music.play("menu_music")

pgzrun.go()
