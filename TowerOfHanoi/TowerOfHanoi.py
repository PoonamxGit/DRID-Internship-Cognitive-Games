import pygame
import sys
import time
import threading
import random
import math
import json
import os
import cv2
import mediapipe as mp

pygame.init()
WIDTH, HEIGHT = 900, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Advanced Tower of Hanoi")
font = pygame.font.SysFont(None, 36)
big_font = pygame.font.SysFont(None, 72)

# Color Schemes
LIGHT_THEME = {
    "bg": (255, 255, 255),
    "text": (0, 0, 0),
    "rod": (139, 69, 19),
    "btn": (200, 200, 200)
}

DARK_THEME = {
    "bg": (10, 10, 20),
    "text": (255, 255, 255),
    "rod": (200, 200, 200),
    "btn": (50, 50, 50)
}

current_theme = LIGHT_THEME

# Game Constants
DISK_COLORS = [(255, 0, 0), (255, 165, 0), (255, 255, 0),
               (0, 128, 0), (0, 0, 255), (75, 0, 130), (238, 130, 238)]

ROD_X = [200, 450, 700]
ROD_Y_TOP = 150
ROD_HEIGHT = 300
DISK_HEIGHT = 30

# Game State
level = 1
max_level = 6
move_count = 0
timer_start = None
selected_disk = None
selected_disk_pos = None
auto_solving = False
game_state = "start"
countdown_start = 0

# Leaderboard
LEADERBOARD_FILE = "leaderboard.json"
leaderboard = []

# Starfield (for dark theme animation)
stars = [(random.randint(0, WIDTH), random.randint(0, HEIGHT), random.randint(1, 3)) for _ in range(100)]

def reset_level():
    global rods, move_count, timer_start
    rods = [list(range(level, 0, -1)), [], []]
    move_count = 0
    timer_start = time.time()

def draw_starfield():
    for i, (x, y, speed) in enumerate(stars):
        pygame.draw.circle(screen, (100 + speed * 50,) * 3, (x, y), speed)
        y += speed
        if y > HEIGHT:
            y = 0
            x = random.randint(0, WIDTH)
        stars[i] = (x, y, speed)

def draw_gradient_background():
    top_color = (180, 220, 255) if current_theme == LIGHT_THEME else (20, 20, 60)
    bottom_color = (255, 255, 255) if current_theme == LIGHT_THEME else (40, 40, 80)
    for y in range(HEIGHT):
        ratio = y / HEIGHT
        r = int(top_color[0] * (1 - ratio) + bottom_color[0] * ratio)
        g = int(top_color[1] * (1 - ratio) + bottom_color[1] * ratio)
        b = int(top_color[2] * (1 - ratio) + bottom_color[2] * ratio)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

def draw_page_border():
    border_color = (0, 120, 255) if current_theme == LIGHT_THEME else (0, 255, 180)
    for i in range(8, 0, -2):
        alpha = max(30, 255 - i * 30)
        s = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        pygame.draw.rect(s, border_color + (alpha,), (i, i, WIDTH-2*i, HEIGHT-2*i), 4)
        screen.blit(s, (0, 0))
    pygame.draw.rect(screen, border_color, (0, 0, WIDTH, HEIGHT), 6)

def draw_button(text, x, y, w, h):
    pygame.draw.rect(screen, current_theme["btn"], (x, y, w, h))
    pygame.draw.rect(screen, current_theme["text"], (x, y, w, h), 2)
    txt = font.render(text, True, current_theme["text"])
    screen.blit(txt, (x + (w - txt.get_width()) // 2, y + (h - txt.get_height()) // 2))

def button_clicked(x, y, bx, by, bw, bh):
    return bx <= x <= bx + bw and by <= y <= by + bh

def get_disk_rect(rod_index, disk_index, disk_size):
    width = 30 + disk_size * 30
    x = ROD_X[rod_index] - width // 2
    y = ROD_Y_TOP + ROD_HEIGHT - (disk_index + 1) * DISK_HEIGHT
    return pygame.Rect(x, y, width, DISK_HEIGHT)

def get_rod_from_pos(x):
    for i, rod_x in enumerate(ROD_X):
        if abs(x - rod_x) < 100:
            return i
    return None

def can_place_disk(rod_index, disk_size):
    rod = rods[rod_index]
    return not rod or rod[-1] > disk_size

def auto_solve_hanoi(n, source, target, aux):
    global rods, move_count
    if n == 0:
        return
    auto_solve_hanoi(n - 1, source, aux, target)
    rods[target].append(rods[source].pop())
    move_count += 1
    draw_game_screen()
    pygame.display.flip()
    time.sleep(0.2)
    auto_solve_hanoi(n - 1, aux, target, source)

def start_auto_solver():
    global auto_solving
    if auto_solving:
        return
    auto_solving = True
    threading.Thread(target=solve_thread, daemon=True).start()

def solve_thread():
    global auto_solving
    auto_solve_hanoi(level, 0, 2, 1)
    auto_solving = False

def draw_leaderboard_screen():
    draw_gradient_background()
    draw_page_border()
    title = big_font.render("Leaderboard (Best Times)", True, (0, 180, 0))
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))
    sorted_lb = sorted(leaderboard, key=lambda x: x["time"])[:10]
    for i, entry in enumerate(sorted_lb):
        txt = font.render(f"{i+1}. {entry['name']} - {entry['time']}s", True, current_theme["text"])
        screen.blit(txt, (WIDTH // 2 - 200, 150 + i * 40))
    draw_button("Back", WIDTH // 2 - 100, HEIGHT - 80, 200, 50)
    pygame.display.flip()

def get_player_name():
    name = ""
    input_active = True
    while input_active:
        draw_gradient_background()
        draw_page_border()
        prompt = font.render("Enter your name for the leaderboard:", True, current_theme["text"])
        screen.blit(prompt, (WIDTH // 2 - prompt.get_width() // 2, HEIGHT // 2 - 60))
        name_txt = big_font.render(name + "|", True, (0, 180, 0))
        screen.blit(name_txt, (WIDTH // 2 - name_txt.get_width() // 2, HEIGHT // 2))
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    input_active = False
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 12 and event.unicode.isprintable():
                    name += event.unicode
    return name.strip()

def draw_start_screen():
    draw_gradient_background()
    draw_page_border()
    if current_theme == DARK_THEME:
        draw_starfield()
    title = big_font.render("Tower of Hanoi", True, current_theme["text"])
    screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
    draw_button("Start Game", WIDTH // 2 - 100, 250, 200, 50)
    draw_button("Instructions", WIDTH // 2 - 100, 320, 200, 50)
    draw_button("Change Theme", WIDTH // 2 - 100, 390, 200, 50)
    draw_button("Leaderboard", WIDTH // 2 - 100, 460, 200, 50)
    pygame.display.flip()

def draw_instruction_screen():
    draw_gradient_background()
    draw_page_border()
    lines = [
        "Goal: Move all disks from the first rod to the third.",
        "Rules:",
        "1. Only one disk can be moved at a time.",
        "2. A larger disk cannot be placed on a smaller one.",
        "3. Use as few moves as possible.",
        "",
        "Level 2 Gesture Controls:",
        "- To PICK a disk: Make a pointing gesture (index finger extended, thumb apart) above a rod.",
        "- To MOVE the disk: Move your hand left/right above the rods.",
        "- To DROP the disk: Pinch your thumb and index finger together above the target rod.",
        "- Only valid moves are allowed (no larger disk on smaller).",
        "",
        "Buttons:",
        "- Restart: Reset current level.",
        "- Next Level: Go to next disk level.",
        "- Auto Solve: Watch the puzzle being solved!"
    ]
    for i, line in enumerate(lines):
        txt = font.render(line, True, current_theme["text"])
        screen.blit(txt, (50, 50 + i * 35))
    draw_button("Back", 20, HEIGHT - 60, 150, 40)
    pygame.display.flip()

def draw_countdown_screen():
    draw_gradient_background()
    draw_page_border()
    elapsed = time.time() - countdown_start
    if elapsed >= 4:
        reset_level()
        return "game"
    countdown = 3 - int(elapsed)
    text = big_font.render(str(countdown if countdown > 0 else "Go!"), True, (255, 0, 0))
    screen.blit(text, (WIDTH // 2 - text.get_width() // 2, HEIGHT // 2 - text.get_height() // 2))
    pygame.display.flip()
    return "countdown"

def draw_game_screen(gesture_disk=None, gesture_rod=None):
    draw_gradient_background()
    draw_page_border()
    if current_theme == DARK_THEME:
        draw_starfield()
    for x in ROD_X:
        pygame.draw.rect(screen, current_theme["rod"], (x - 10, ROD_Y_TOP, 20, ROD_HEIGHT))
    for rod_index, rod in enumerate(rods):
        for disk_index, disk_size in enumerate(rod):
            rect = get_disk_rect(rod_index, disk_index, disk_size)
            color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, current_theme["text"], rect, 2)
    if selected_disk and selected_disk_pos:
        disk_size = selected_disk[1]
        width = 30 + disk_size * 30
        rect = pygame.Rect(selected_disk_pos[0] - width // 2, selected_disk_pos[1] - DISK_HEIGHT // 2, width, DISK_HEIGHT)
        color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, current_theme["text"], rect, 2)
    # Draw gesture disk (for Level 2)
    if gesture_disk is not None and gesture_rod is not None:
        disk_size = gesture_disk
        width = 30 + disk_size * 30
        rod_x = ROD_X[gesture_rod]
        rect = pygame.Rect(rod_x - width // 2, ROD_Y_TOP - 40, width, DISK_HEIGHT)
        color = DISK_COLORS[(disk_size - 1) % len(DISK_COLORS)]
        pygame.draw.rect(screen, color, rect)
        pygame.draw.rect(screen, current_theme["text"], rect, 2)
    time_elapsed = int(time.time() - timer_start) if timer_start else 0
    screen.blit(font.render(f"Time: {time_elapsed}s", True, current_theme["text"]), (10, 10))
    screen.blit(font.render(f"Moves: {move_count}", True, current_theme["text"]), (10, 50))
    screen.blit(font.render(f"Level: {level}", True, current_theme["text"]), (10, 90))
    draw_button("Restart", WIDTH - 180, 20, 150, 40)
    if len(rods[2]) == level:
        if level == max_level:
            win_text = big_font.render("You reached the last level!", True, (0, 255, 0))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 50))
            draw_button("Next Level", WIDTH - 180, 70, 150, 40)
        else:
            win_text = big_font.render("Level Complete!", True, (0, 255, 0))
            screen.blit(win_text, (WIDTH // 2 - win_text.get_width() // 2, 50))
            draw_button("Next Level", WIDTH - 180, 70, 150, 40)
    draw_button("Auto Solve", WIDTH - 180, 120, 150, 40)
    pygame.display.flip()

def draw_thankyou_screen():
    draw_gradient_background()
    draw_page_border()
    msg = big_font.render("Thank you, you played well!", True, (0, 180, 0))
    screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, HEIGHT // 2 - 100))
    draw_button("Start Again", WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60)
    pygame.display.flip()

def toggle_theme():
    global current_theme
    current_theme = DARK_THEME if current_theme == LIGHT_THEME else LIGHT_THEME

def load_leaderboard():
    global leaderboard
    if os.path.exists(LEADERBOARD_FILE):
        with open(LEADERBOARD_FILE, "r") as f:
            leaderboard = json.load(f)
    else:
        leaderboard = []

def save_leaderboard():
    with open(LEADERBOARD_FILE, "w") as f:
        json.dump(leaderboard, f)

# --- Hand Gesture Controller Class ---
class HandGestureController:
    def __init__(self):
        self.mp_hands = mp.solutions.hands
        self.hands = self.mp_hands.Hands(max_num_hands=1)

    def detect_gesture(self, frame):
        img_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        results = self.hands.process(img_rgb)
        gesture = None
        rod_index = None
        if results.multi_hand_landmarks:
            hand_landmarks = results.multi_hand_landmarks[0]
            index_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.INDEX_FINGER_TIP]
            thumb_tip = hand_landmarks.landmark[self.mp_hands.HandLandmark.THUMB_TIP]
            dist = ((index_tip.x - thumb_tip.x) ** 2 + (index_tip.y - thumb_tip.y) ** 2) ** 0.5
            if dist < 0.05:
                gesture = "pinch"
            else:
                gesture = "point"
            if index_tip.x < 0.33:
                rod_index = 0
            elif index_tip.x < 0.66:
                rod_index = 1
            else:
                rod_index = 2
        return gesture, rod_index
    def release(self):
        self.hands.close()

def main():
    global selected_disk, selected_disk_pos, move_count, level, game_state, countdown_start, rods

    clock = pygame.time.Clock()
    running = True

    # Gesture variables
    gesture_controller = None
    cap = None
    gesture_disk = None
    gesture_disk_rod = None
    gesture_last_rod = None

    game_state = "start"
    while running:
        # --- Hand Gesture Controls for Level 2 ---
        if game_state == "game" and level == 2:
            if gesture_controller is None:
                cap = cv2.VideoCapture(0)
                gesture_controller = HandGestureController()
                gesture_disk = None
                gesture_disk_rod = None
                gesture_last_rod = None

            ret, frame = cap.read()
            if ret:
                gesture, rod_index = gesture_controller.detect_gesture(frame)
                cv2.imshow("Hand Gesture Control", frame)
                cv2.waitKey(1)

                # Pick disk
                if gesture == "point" and gesture_disk is None and rod_index is not None and rods[rod_index]:
                    disk_size = rods[rod_index].pop()
                    gesture_disk = disk_size
                    gesture_disk_rod = rod_index
                    gesture_last_rod = rod_index

                # Drop disk
                elif gesture == "pinch" and gesture_disk is not None and rod_index is not None and can_place_disk(rod_index, gesture_disk):
                    rods[rod_index].append(gesture_disk)
                    move_count += 1
                    gesture_disk = None
                    gesture_disk_rod = None
                    gesture_last_rod = None

                # If trying to drop on invalid rod, return disk to original rod
                elif gesture == "pinch" and gesture_disk is not None:
                    rods[gesture_disk_rod].append(gesture_disk)
                    gesture_disk = None
                    gesture_disk_rod = None
                    gesture_last_rod = None

            draw_game_screen(gesture_disk, rod_index if gesture_disk is not None else None)

            # --- Automatically go to next level when Level 2 is completed ---
            if len(rods[2]) == level:
                # Release resources
                if gesture_controller is not None:
                    gesture_controller.release()
                    gesture_controller = None
                if cap is not None:
                    cap.release()
                    cv2.destroyAllWindows()
                    cap = None
                gesture_disk = None
                gesture_disk_rod = None
                gesture_last_rod = None
                # Go to next level or leaderboard
                if level < max_level:
                    level += 1
                    reset_level()
                    # If you want to show a "Level Complete" message for a second, you can add a delay here
                else:
                    time_elapsed = int(time.time() - timer_start)
                    name = get_player_name()
                    leaderboard.append({"name": name, "time": time_elapsed})
                    leaderboard.sort(key=lambda x: x["time"])
                    save_leaderboard()
                    game_state = "leaderboard"
        else:
            # Release webcam and gesture controller if not in Level 2
            if gesture_controller is not None:
                gesture_controller.release()
                gesture_controller = None
            if cap is not None:
                cap.release()
                cv2.destroyAllWindows()
                cap = None
            if game_state == "game":
                draw_game_screen()

        if game_state == "start":
            draw_start_screen()
        elif game_state == "instructions":
            draw_instruction_screen()
        elif game_state == "countdown":
            game_state = draw_countdown_screen()
        elif game_state == "thankyou":
            draw_thankyou_screen()
        elif game_state == "leaderboard":
            draw_leaderboard_screen()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = event.pos
                if game_state == "start":
                    if button_clicked(mx, my, WIDTH // 2 - 100, 250, 200, 50):
                        countdown_start = time.time()
                        game_state = "countdown"
                    elif button_clicked(mx, my, WIDTH // 2 - 100, 320, 200, 50):
                        game_state = "instructions"
                    elif button_clicked(mx, my, WIDTH // 2 - 100, 390, 200, 50):
                        toggle_theme()
                    elif button_clicked(mx, my, WIDTH // 2 - 100, 460, 200, 50):
                        game_state = "leaderboard"

                elif game_state == "instructions":
                    if button_clicked(mx, my, 20, HEIGHT - 60, 150, 40):
                        game_state = "start"

                elif game_state == "game" and level != 2:
                    if auto_solving:
                        continue
                    if button_clicked(mx, my, WIDTH - 180, 20, 150, 40):
                        reset_level()
                    elif button_clicked(mx, my, WIDTH - 180, 70, 150, 40):
                        if len(rods[2]) == level:
                            if level < max_level:
                                level += 1
                                reset_level()
                            else:
                                time_elapsed = int(time.time() - timer_start)
                                name = get_player_name()
                                leaderboard.append({"name": name, "time": time_elapsed})
                                leaderboard.sort(key=lambda x: x["time"])
                                save_leaderboard()
                                game_state = "leaderboard"
                    elif button_clicked(mx, my, WIDTH - 180, 120, 150, 40):
                        start_auto_solver()
                    elif selected_disk is None:
                        rod_idx = get_rod_from_pos(mx)
                        if rod_idx is not None and rods[rod_idx]:
                            disk_size = rods[rod_idx].pop()
                            selected_disk = (rod_idx, disk_size)
                            selected_disk_pos = event.pos

                elif game_state == "thankyou":
                    if button_clicked(mx, my, WIDTH // 2 - 100, HEIGHT // 2 + 20, 200, 60):
                        level = 1
                        reset_level()
                        game_state = "start"

                elif game_state == "leaderboard":
                    if button_clicked(mx, my, WIDTH // 2 - 100, HEIGHT - 80, 200, 50):
                        level = 1
                        reset_level()
                        game_state = "start"

            elif event.type == pygame.MOUSEMOTION:
                if selected_disk:
                    selected_disk_pos = event.pos

            elif event.type == pygame.MOUSEBUTTONUP:
                if selected_disk:
                    mx, my = event.pos
                    target_rod = get_rod_from_pos(mx)
                    if target_rod is not None and can_place_disk(target_rod, selected_disk[1]):
                        rods[target_rod].append(selected_disk[1])
                        move_count += 1
                    else:
                        rods[selected_disk[0]].append(selected_disk[1])
                    selected_disk = None
                    selected_disk_pos = None

        clock.tick(60)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    reset_level()
    load_leaderboard()
    main()
