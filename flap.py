import pygame, random, time
from pygame.locals import *

from game_logger import init_session, start_game, finish_game, save_session

from agent_audio_manager import update_agent_audio
from agent_audio_manager import (
    init_agent_sounds,
    play_intro,
    play_outro,
    play_pipe_loss,
    play_ground_loss,
    play_high_score,
    play_game_win,
)

# --- Game constants ---
SCREEN_WIDHT = 400
SCREEN_HEIGHT = 600
SPEED = 10
GRAVITY = 0.5
GAME_SPEED = 5

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

wing = 'assets/audio/wing.wav'
hit = 'assets/audio/hit.wav'


# --- Sprite Classes ---
class Bird(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.images = [pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),
                       pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha()]
        self.speed = SPEED
        self.current_image = 0
        self.image = pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.animation_time = 120
        self.last_anim_time = pygame.time.get_ticks()
        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT / 6
        self.rect[1] = SCREEN_HEIGHT / 2

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.animation_time:
            self.current_image = (self.current_image + 1) % 3
            self.image = self.images[self.current_image]
            self.last_anim_time = now
        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):
        self.speed = -SPEED

    def begin(self):
        now = pygame.time.get_ticks()
        if now - self.last_anim_time >= self.animation_time:
            self.current_image = (self.current_image + 1) % 3
            self.image = self.images[self.current_image]
            self.last_anim_time = now


class Pipe(pygame.sprite.Sprite):
    def __init__(self, inverted, xpos, ysize):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (PIPE_WIDHT, PIPE_HEIGHT))
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        if inverted:
            self.image = pygame.transform.flip(self.image, False, True)
            self.rect[1] = - (self.rect[3] - ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize
        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED


class Ground(pygame.sprite.Sprite):
    def __init__(self, xpos):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image, (GROUND_WIDHT, GROUND_HEIGHT))
        self.mask = pygame.mask.from_surface(self.image)
        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

    def update(self):
        self.rect[0] -= GAME_SPEED


def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])


def get_random_pipes(xpos):
    size = random.randint(100, 300)
    pipe = Pipe(False, xpos, size)
    pipe_inverted = Pipe(True, xpos, SCREEN_HEIGHT - size - PIPE_GAP)
    return pipe, pipe_inverted


# --- The Game Engine Class ---
class FlappyGame:
    def __init__(self):
        # Pygame initialization
        pygame.init()
        pygame.font.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
        pygame.display.set_caption('Flappy Bird')

        # Audio init
        pygame.mixer.init()
        init_agent_sounds()

        # Assets
        self.score_font = pygame.font.SysFont('Impact', 30)
        self.score_bg_font = pygame.font.SysFont('Impact', 32)
        self.info_font = pygame.font.SysFont('Impact', 25)
        self.info_1 = self.info_font.render("Press 'R' to try again", True, (250, 121, 88))
        self.info_1_bg = self.info_font.render("Press 'R' to try again", True, (240, 234, 161))

        self.BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
        self.BACKGROUND = pygame.transform.scale(self.BACKGROUND, (SCREEN_WIDHT, SCREEN_HEIGHT))
        self.BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()
        self.GAME_OVER_TEXT = pygame.image.load('assets/sprites/gameover.png').convert_alpha()
        self.SCORE_PANEL = pygame.image.load('assets/sprites/score.png').convert_alpha()
        self.AGENT_WINDOW = pygame.image.load('assets/sprites/agent.png').convert_alpha()

        # load the agent with the mouth open
        self.AGENT_SPEAK = pygame.image.load('assets/sprites/agent_speaking.png').convert_alpha()

        self.clock = pygame.time.Clock()

        # Persistent Game Variables
        self.high_score = 0
        self.loss_count = 0
        self.ticks_played = 0
        self.agent_enabled = False
        self.agent_speaking = False

        # Logging
        self.session_log, self.LOG_PATH = init_session("session_log.txt")
        self.current_game_key = None
        self.game_ticks_start = 0

        # Initialize First Round
        self.init_round()

    def init_round(self):
        """Initializes sprites for a new game round."""
        self.bird_group = pygame.sprite.Group()
        self.bird = Bird()
        self.bird_group.add(self.bird)

        self.ground_group = pygame.sprite.Group()
        for i in range(2):
            ground = Ground(GROUND_WIDHT * i)
            self.ground_group.add(ground)

        self.pipe_group = pygame.sprite.Group()
        for i in range(2):
            pipes = get_random_pipes(SCREEN_WIDHT * i + 800)
            self.pipe_group.add(pipes[0])
            self.pipe_group.add(pipes[1])

        self.begin = True
        self.alive = True
        self.passed = False
        self.score = 0

    def get_state(self):
        """Returns the game state for the support agent."""
        # Find next pipe distance
        dist_to_pipe = 9999
        pipe_y = 0
        for pipe in self.pipe_group:
            if pipe.rect[1] > 0:  # Bottom pipe
                if pipe.rect.x + pipe.rect.width > self.bird.rect.x:
                    if pipe.rect.x < dist_to_pipe:
                        dist_to_pipe = pipe.rect.x
                        pipe_y = pipe.rect.y

        return {
            "player_y": self.bird.rect.y,
            "next_pipe_dist_x": dist_to_pipe - self.bird.rect.x,
            "next_pipe_y": pipe_y,
            "is_alive": self.alive,
            "game_active": not self.begin,
            "score": self.score,
            "loss_count": self.loss_count
        }

    def frame_step(self, input_action=None):
        """
        Runs exactly ONE frame.
        If input_action is None, it listens to the keyboard.
        """
        update_agent_audio()
        self.clock.tick(60)

        # 1. Event Handling (Manual Input)
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                return False
            if event.type == KEYDOWN:
                if (event.key == K_SPACE or event.key == K_UP) and self.alive:
                    input_action = "jump"
                if event.key == K_r and not self.alive:
                    input_action = "restart"

        # 2. Start Screen Logic
        if self.begin:
            if input_action == "jump":
                self.bird.bump()
                pygame.mixer.music.load(wing)
                pygame.mixer.music.play()

                self.current_game_key = start_game(self.session_log, self.high_score, self.loss_count)
                self.game_ticks_start = self.ticks_played

                self.begin = False
                self.passed = False
                self.score = 0

            self.screen.blit(self.BACKGROUND, (0, 0))
            self.screen.blit(self.BEGIN_IMAGE, (120, 150))

            if is_off_screen(self.ground_group.sprites()[0]):
                self.ground_group.remove(self.ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                self.ground_group.add(new_ground)

            self.bird.begin()
            self.ground_group.update()

            self.bird_group.draw(self.screen)
            self.ground_group.draw(self.screen)
            if self.agent_enabled: self.screen.blit(self.AGENT_WINDOW, (10, 510))
            pygame.display.update()
            return True

        # 3. Main Logic
        self.screen.blit(self.BACKGROUND, (0, 0))

        # --- UPDATE PHASE (Physics) ---
        if self.alive:
            self.ticks_played += 1
            if input_action == "jump":
                self.bird.bump()
                pygame.mixer.music.load(wing)
                pygame.mixer.music.play()

            if is_off_screen(self.ground_group.sprites()[0]):
                self.ground_group.remove(self.ground_group.sprites()[0])
                new_ground = Ground(GROUND_WIDHT - 20)
                self.ground_group.add(new_ground)

            bird_pos = SCREEN_WIDHT / 6
            current_pipe = self.pipe_group.sprites()[0]
            if (self.passed is False) and (current_pipe.rect[0] <= bird_pos):
                self.passed = True
                self.score += 1
                print(" Score: " + str(self.score))

            if is_off_screen(self.pipe_group.sprites()[0]):
                self.pipe_group.remove(self.pipe_group.sprites()[0])
                self.pipe_group.remove(self.pipe_group.sprites()[0])
                pipes = get_random_pipes(SCREEN_WIDHT * 2)
                self.pipe_group.add(pipes[0])
                self.pipe_group.add(pipes[1])
                self.passed = False

            # Update sprite positions
            self.bird_group.update()
            self.ground_group.update()
            self.pipe_group.update()

            # Collision Check
            hit_ground = pygame.sprite.groupcollide(self.bird_group, self.ground_group, False, False,
                                                    pygame.sprite.collide_mask)
            hit_pipe = pygame.sprite.groupcollide(self.bird_group, self.pipe_group, False, False,
                                                  pygame.sprite.collide_mask)

            if hit_ground or hit_pipe:
                self.high_score = max(self.high_score, self.score)
                if self.high_score == self.score and self.agent_enabled: play_high_score()
                if hit_pipe and self.agent_enabled: play_pipe_loss()
                if hit_ground and self.agent_enabled: play_ground_loss()
                pygame.mixer.music.load(hit)
                pygame.mixer.music.play()
                self.alive = False
                self.loss_count += 1

                if self.current_game_key is not None:
                    duration_ticks = self.ticks_played - self.game_ticks_start
                    death_cause = "ground" if hit_ground else "pipe"
                    finish_game(self.session_log, self.current_game_key, duration_ticks, self.score, self.high_score,
                                self.loss_count, death_cause)
                    save_session(self.LOG_PATH, self.session_log)

                # Prepare surfaces for Game Over screen
                self.score_surface = self.score_font.render(str(self.score), True, (250, 121, 88))
                self.score_bg_surface = self.score_bg_font.render(str(self.score), True, (240, 234, 161))
                self.hs_surface = self.score_font.render(str(self.high_score), True, (250, 121, 88))
                self.hs_bg_surface = self.score_bg_font.render(str(self.high_score), True, (240, 234, 161))

        # --- DRAW PHASE ---
        self.bird_group.draw(self.screen)
        self.pipe_group.draw(self.screen)
        self.ground_group.draw(self.screen)

        # make the agent switch between mouth open and closed when speaking
        if self.agent_enabled:
            # 1. Check if talking (default to False if variable missing)
            talking = getattr(self, 'is_talking', False)

            # 2. Toggle frame every ~150ms (Animation Speed)
            # If talking AND (time modulo) is even -> Open Mouth. Else -> Closed.
            if talking and (pygame.time.get_ticks() // 150) % 2 == 0:
                self.screen.blit(self.AGENT_SPEAK, (10, 510))
            else:
                self.screen.blit(self.AGENT_WINDOW, (10, 510))

        # --- GAME OVER UI ---
        if not self.alive:
            if not self.agent_speaking and input_action == "restart":
                self.init_round()

            self.screen.blit(self.GAME_OVER_TEXT, (100, 100))
            self.screen.blit(self.SCORE_PANEL, (35, 200))
            self.screen.blit(self.score_bg_surface, (310, 245))
            self.screen.blit(self.score_surface, (310, 245))
            self.screen.blit(self.hs_bg_surface, (310, 308))
            self.screen.blit(self.hs_surface, (310, 308))
            self.screen.blit(self.info_1_bg, (52, 222))
            self.screen.blit(self.info_1, (50, 220))

            # Enable Agent if conditions met
            if not self.agent_enabled and self.loss_count >= 2 and self.ticks_played >= 100:
                self.agent_enabled = True
                print("This is where the agent should first intervene")
                play_intro()

        pygame.display.update()
        return True


if __name__ == "__main__":
    game = FlappyGame()
    running = True
    while running:
        running = game.frame_step()