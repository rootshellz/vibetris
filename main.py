import pygame
import sys
import random
from pieces import Tetromino, TETROMINOES

# Initialize Pygame
pygame.init()
pygame.mixer.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 30
GRID_WIDTH = 10
GRID_HEIGHT = 20
SIDEBAR_WIDTH = 200

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
CYAN = (0, 255, 255)
YELLOW = (255, 255, 0)
MAGENTA = (255, 0, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
ORANGE = (255, 165, 0)

# Set up the display
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
pygame.display.set_caption("Tetris Game")

# Game variables
grid = [[BLACK for _ in range(GRID_WIDTH)] for _ in range(GRID_HEIGHT)]
current_piece = None
next_piece = None
game_over = False
clock = pygame.time.Clock()
fall_time = 0
fall_speed = 50  # milliseconds
lock_delay = 5  # milliseconds
lock_timer = 0
score = 0
total_lines_cleared = 0
key_repeat_delay = 200  # milliseconds before repeat starts
key_repeat_rate = 50  # milliseconds between repeats
key_states = {"left": False, "right": False, "down": False}
key_timers = {"left": 0, "right": 0, "down": 0}
block_counts = {"I": 0, "O": 0, "T": 0, "S": 0, "Z": 0, "J": 0, "L": 0}
total_blocks = 0


def draw_grid():
    # Draw the grid cells
    for y in range(GRID_HEIGHT):
        for x in range(GRID_WIDTH):
            if grid[y][x] != BLACK:
                pygame.draw.rect(
                    screen,
                    grid[y][x],
                    (
                        x * GRID_SIZE + SIDEBAR_WIDTH,
                        y * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE,
                    ),
                )
                pygame.draw.rect(
                    screen,
                    WHITE,
                    (
                        x * GRID_SIZE + SIDEBAR_WIDTH,
                        y * GRID_SIZE,
                        GRID_SIZE,
                        GRID_SIZE,
                    ),
                    1,
                )
    # Draw border around the gameplay area
    pygame.draw.rect(
        screen,
        WHITE,
        (SIDEBAR_WIDTH, 0, GRID_WIDTH * GRID_SIZE, GRID_HEIGHT * GRID_SIZE),
        2,
    )


def draw_sidebar():
    pygame.draw.rect(screen, BLACK, (0, 0, SIDEBAR_WIDTH, WINDOW_HEIGHT))
    # Display score and lines cleared
    font = pygame.font.Font(None, 36)
    score_text = font.render(f"Score: {score}", True, WHITE)
    screen.blit(score_text, (10, 10))
    lines_text = font.render(f"Lines: {total_lines_cleared}", True, WHITE)
    screen.blit(lines_text, (10, 40))

    # Display block counters and percentages with corresponding colors
    y_position = 80
    block_types = ["I", "O", "T", "S", "Z", "J", "L"]
    for block in block_types:
        count = block_counts[block]
        percentage = (count / total_blocks * 100) if total_blocks > 0 else 0
        block_color = TETROMINOES[block]["color"]
        block_text = font.render(
            f"{block}: {count} ({percentage:.1f}%)", True, block_color
        )
        screen.blit(block_text, (10, y_position))
        y_position += 30


def draw_next_piece(piece):
    font = pygame.font.Font(None, 36)
    next_text = font.render("Next:", True, WHITE)
    screen.blit(next_text, (510, 10))
    if piece:
        shape = piece.shape
        start_x = 600
        start_y = 50
        for r, row in enumerate(shape):
            for c, cell in enumerate(row):
                if cell != 0:
                    pygame.draw.rect(
                        screen,
                        piece.color,
                        (
                            start_x + c * GRID_SIZE,
                            start_y + r * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                    )
                    pygame.draw.rect(
                        screen,
                        WHITE,
                        (
                            start_x + c * GRID_SIZE,
                            start_y + r * GRID_SIZE,
                            GRID_SIZE,
                            GRID_SIZE,
                        ),
                        1,
                    )


def spawn_piece():
    global total_blocks
    # Choose a random tetromino
    piece_name = random.choice(list(TETROMINOES.keys()))
    # Update block counts
    block_counts[piece_name] += 1
    total_blocks += 1
    # Spawn at the top center of the grid
    x = GRID_WIDTH // 2 - len(TETROMINOES[piece_name]["shape"][0]) // 2
    y = 0
    return Tetromino(piece_name, x, y)


def merge_piece_to_grid():
    global current_piece, grid
    for x, y in current_piece.get_positions():
        if y < 0:  # Piece has reached the top
            return False
        grid[y][x] = current_piece.color
    return True


def clear_lines():
    global grid, score, total_lines_cleared
    lines_cleared = 0
    y = GRID_HEIGHT - 1
    while y >= 0:
        if all(cell != BLACK for cell in grid[y]):
            lines_cleared += 1
            del grid[y]
            grid.insert(0, [BLACK for _ in range(GRID_WIDTH)])
        else:
            y -= 1
    total_lines_cleared += lines_cleared
    if lines_cleared == 1:
        score += 100
    elif lines_cleared == 2:
        score += 400
    elif lines_cleared == 3:
        score += 900
    elif lines_cleared == 4:
        score += 2000
    return lines_cleared


def draw_current_piece():
    for x, y in current_piece.get_positions():
        if y >= 0:  # Only draw parts of the piece that are within the grid
            pygame.draw.rect(
                screen,
                current_piece.color,
                (
                    x * GRID_SIZE + SIDEBAR_WIDTH,
                    y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                ),
            )
            pygame.draw.rect(
                screen,
                WHITE,
                (
                    x * GRID_SIZE + SIDEBAR_WIDTH,
                    y * GRID_SIZE,
                    GRID_SIZE,
                    GRID_SIZE,
                ),
                1,
            )


def main():
    global current_piece, next_piece, game_over, fall_time, score, lock_timer

    # Synthesize event-based 8-bit chiptune style sound effects
    import array
    import math

    def generate_square_wave(frequency, duration, sample_rate=44100, amplitude=0.5):
        samples = int(sample_rate * duration)
        data = array.array("h")  # signed short integer samples
        for i in range(samples):
            t = float(i) / sample_rate
            value = int(
                32760
                * amplitude
                * (1 if math.sin(2 * math.pi * frequency * t) >= 0 else -1)
            )
            data.append(value)
        return pygame.mixer.Sound(buffer=data)

    # Define sound effects for different events
    # Neutral sound for block landing
    block_land_sound = generate_square_wave(
        220.00, 0.1, amplitude=0.3
    )  # A3, short beep
    # Positive sounds for scoring
    score_1_point_sound = generate_square_wave(
        523.25, 0.05, amplitude=0.4
    )  # C5, quick high note
    score_100_points_sound = generate_square_wave(
        659.25, 0.1, amplitude=0.5
    )  # E5, slightly longer
    score_600_points_sound = generate_square_wave(
        783.99, 0.2, amplitude=0.6
    )  # G5, triumphant longer note
    # Negative sound for game over
    game_over_sound = generate_square_wave(
        130.81, 0.5, amplitude=0.5
    )  # C3, low and slow

    # Channels for sound effects and background music
    effect_channel = pygame.mixer.Channel(0)
    bg_music_channel = pygame.mixer.Channel(1)

    def generate_melody(key="C", num_notes=64):
        notes = {
            "C": [261.63, 523.25],
            "D": [293.66, 587.33],
            "E": [329.63, 659.25],
            "F": [349.23, 698.46],
            "G": [392.00, 783.99],
            "A": [440.00, 880.00],
            "B": [493.88, 987.77],
        }
        scales = {
            "C_major_penta": ["C", "D", "E", "G", "A"],
            "G_major_penta": ["G", "A", "B", "D", "E"],
            "F_major_penta": ["F", "G", "A", "C", "D"],
        }

        scale = scales.get(f"{key}_major_penta", scales["C_major_penta"])
        melody = []
        for _ in range(num_notes):
            note_name = random.choice(scale)
            octave = random.choice([0, 1])
            frequency = notes[note_name][octave]
            duration = random.choice([0.1, 0.2, 0.2, 0.3, 0.4])
            melody.append((frequency, duration))
        return melody

    bg_melody = generate_melody(random.choice(["C", "F", "G"]))

    # Play the background melody in a loop
    current_bg_note = 0
    bg_note_start_time = 0

    def play_next_bg_note():
        nonlocal current_bg_note, bg_note_start_time
        if current_bg_note < len(bg_melody):
            frequency, duration = bg_melody[current_bg_note]
            note_sound = generate_square_wave(frequency, duration, amplitude=0.2)
            bg_music_channel.play(note_sound)
            bg_note_start_time = pygame.time.get_ticks()
            current_bg_note = (current_bg_note + 1) % len(bg_melody)

    # Start the background music
    play_next_bg_note()

    if current_piece is None:
        current_piece = spawn_piece()
        next_piece = spawn_piece()
        if current_piece.collides(grid):
            game_over = True

    game_over_time = 0
    game_over_display_duration = 3000  # 3 seconds in milliseconds

    while True:
        if not game_over:
            fall_time += clock.get_rawtime()
            clock.tick()

            # Handle key events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_over = True
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        key_states["left"] = True
                        key_timers["left"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dx=-1):
                            current_piece.move(-1, 0)
                            if current_piece.collides(grid, dy=1):
                                lock_timer = pygame.time.get_ticks()
                    if event.key == pygame.K_RIGHT:
                        key_states["right"] = True
                        key_timers["right"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dx=1):
                            current_piece.move(1, 0)
                            if current_piece.collides(grid, dy=1):
                                lock_timer = pygame.time.get_ticks()
                    if event.key == pygame.K_DOWN:
                        key_states["down"] = True
                        key_timers["down"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dy=1):
                            current_piece.move(0, 1)
                        else:
                            lock_timer = 1
                    if event.key == pygame.K_UP:
                        original_shape = current_piece.shape
                        current_piece.rotate()
                        if current_piece.collides(grid):
                            # Try wall kicks
                            for dx in [1, -1, 2, -2]:
                                if not current_piece.collides(grid, dx=dx):
                                    current_piece.move(dx, 0)
                                    if current_piece.collides(grid, dy=1):
                                        lock_timer = pygame.time.get_ticks()
                                    break
                            else:
                                current_piece.shape = original_shape
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        key_states["left"] = False
                    if event.key == pygame.K_RIGHT:
                        key_states["right"] = False
                    if event.key == pygame.K_DOWN:
                        key_states["down"] = False

            # Handle background music timing
            current_time = pygame.time.get_ticks()
            if bg_note_start_time > 0 and current_time - bg_note_start_time >= (
                bg_melody[(current_bg_note - 1) % len(bg_melody)][1] * 1000
            ):
                play_next_bg_note()

            # Handle key repeat
            for direction in ["left", "right", "down"]:
                if key_states[direction]:
                    elapsed = current_time - key_timers[direction]
                    if elapsed >= key_repeat_delay:
                        if (elapsed - key_repeat_delay) >= key_repeat_rate:
                            if direction == "left" and not current_piece.collides(
                                grid, dx=-1
                            ):
                                current_piece.move(-1, 0)
                            elif direction == "right" and not current_piece.collides(
                                grid, dx=1
                            ):
                                current_piece.move(1, 0)
                        elif direction == "down" and not current_piece.collides(
                            grid, dy=1
                        ):
                            current_piece.move(0, 1)
                            score += (
                                2  # Award 2 points per line moved down using down arrow
                            )
                            effect_channel.play(
                                score_1_point_sound
                            )  # Play 1 point score sound
                            key_timers[direction] = current_time - (
                                (elapsed - key_repeat_delay) % key_repeat_rate
                            )

            if fall_time >= fall_speed:
                if not current_piece.collides(grid, dy=1):
                    current_piece.move(0, 1)
                    lock_timer = 0
                else:
                    if lock_timer == 0:
                        lock_timer = pygame.time.get_ticks()
                    if pygame.time.get_ticks() - lock_timer > lock_delay:
                        effect_channel.play(
                            block_land_sound
                        )  # Play block landing sound
                        if not merge_piece_to_grid():
                            game_over = True
                            game_over_time = pygame.time.get_ticks()
                            effect_channel.play(game_over_sound)  # Play game over sound
                        lines_cleared = clear_lines()
                        if lines_cleared > 0:
                            for i in range(lines_cleared):
                                score_100_points_sound.play()
                                pygame.time.wait(100)
                            if lines_cleared == 4:
                                score_600_points_sound.play()
                        current_piece = next_piece
                        next_piece = spawn_piece()
                        if current_piece.collides(grid):
                            game_over = True
                            game_over_time = pygame.time.get_ticks()
                            effect_channel.play(game_over_sound)  # Play game over sound
                        lock_timer = 0
                fall_time = 0

            # Handle custom events for music and input
            for event in pygame.event.get():
                if event.type == pygame.USEREVENT + 2:
                    play_next_bg_note()
                elif event.type == pygame.QUIT:
                    game_over = True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT:
                        key_states["left"] = True
                        key_timers["left"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dx=-1):
                            current_piece.move(-1, 0)
                            if current_piece.collides(grid, dy=1):
                                lock_timer = pygame.time.get_ticks()
                    elif event.key == pygame.K_RIGHT:
                        key_states["right"] = True
                        key_timers["right"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dx=1):
                            current_piece.move(1, 0)
                            if current_piece.collides(grid, dy=1):
                                lock_timer = pygame.time.get_ticks()
                    elif event.key == pygame.K_DOWN:
                        key_states["down"] = True
                        key_timers["down"] = pygame.time.get_ticks()
                        if not current_piece.collides(grid, dy=1):
                            current_piece.move(0, 1)
                            score += (
                                2  # Award 2 points per line moved down using down arrow
                            )
                            effect_channel.play(
                                score_1_point_sound
                            )  # Play 1 point score sound
                        else:
                            lock_timer = 1
                    elif event.key == pygame.K_UP:
                        original_shape = current_piece.shape
                        current_piece.rotate()
                        if current_piece.collides(grid):
                            # Try wall kicks
                            for dx in [1, -1, 2, -2]:
                                if not current_piece.collides(grid, dx=dx):
                                    current_piece.move(dx, 0)
                                    if current_piece.collides(grid, dy=1):
                                        lock_timer = pygame.time.get_ticks()
                                    break
                            else:
                                current_piece.shape = original_shape
                elif event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT:
                        key_states["left"] = False
                    elif event.key == pygame.K_RIGHT:
                        key_states["right"] = False
                    elif event.key == pygame.K_DOWN:
                        key_states["down"] = False

            # Drawing
            screen.fill(BLACK)
            draw_sidebar()
            draw_grid()
            draw_current_piece()
            draw_next_piece(next_piece)
            pygame.display.flip()
            clock.tick(60)
        else:
            # Display Game Over message
            font = pygame.font.Font(None, 74)
            game_over_text = font.render("Game Over", True, WHITE)
            text_rect = game_over_text.get_rect(
                center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
            )
            screen.blit(game_over_text, text_rect)
            pygame.display.flip()

            # Check if it's time to close the game
            current_time = pygame.time.get_ticks()
            if current_time - game_over_time >= game_over_display_duration:
                break

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    break

            clock.tick(60)

    effect_channel.stop()  # Stop sound effects when game ends
    bg_music_channel.stop()  # Stop background music when game ends
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
