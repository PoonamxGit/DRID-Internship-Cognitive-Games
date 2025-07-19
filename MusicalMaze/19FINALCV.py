import pygame
import sys
import time
import random
import cv2
import mediapipe as mp
import numpy as np
import math

pygame.init()


mp_hands = mp.solutions.hands
hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.5
)


cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)


width, height = 1100, 600
TILE_SIZE = 64
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Knight Platformer Gate Game - Gesture Control")
font = pygame.font.SysFont("arial", 36)
small_font = pygame.font.SysFont("arial", 20)
clock = pygame.time.Clock()


pointer_x = width // 2
pointer_y = height // 2
is_clicking = False
click_cooldown = 0
finger_detected = False


try:
    start_bg = pygame.transform.scale(pygame.image.load("./kenney_tiny-town/Sample2-haze.png"), (width, height))
except:
    start_bg = pygame.Surface((width, height))
    start_bg.fill((50, 50, 100))

try:
    main_bg = pygame.transform.scale(pygame.image.load("./kenney_tiny-town/Sample2.png"), (width, height))
except:
    main_bg = pygame.Surface((width, height))
    main_bg.fill((100, 150, 100))

try:
    level_backgrounds = [pygame.transform.scale(pygame.image.load("./kenney_tiny-town/gamebg-2.png"), (width, height)) for _ in range(5)]
except:
    level_backgrounds = [pygame.Surface((width, height)) for _ in range(5)]
    for i, bg in enumerate(level_backgrounds):
        bg.fill((80 + i*20, 120 + i*10, 150 + i*15))

try:
    man_img = pygame.transform.scale(pygame.image.load("./kenney_tiny-town/man.png").convert_alpha(), (120, 90))
except:
    man_img = pygame.Surface((120, 90))
    man_img.fill((200, 100, 50))

try:
    platform_img = pygame.transform.scale(pygame.image.load("kenney_tiny-town/Tiles/platform1.png"), (TILE_SIZE, TILE_SIZE))
except:
    platform_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    platform_img.fill((139, 69, 19))

try:
    spike_img = pygame.transform.scale(pygame.image.load("kenney_tiny-town/Tiles/bomb1.png"), (TILE_SIZE, TILE_SIZE))
except:
    spike_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    spike_img.fill((255, 0, 0))

try:
    barrier_img = pygame.transform.scale(pygame.image.load("images/barrier.png"), (TILE_SIZE, TILE_SIZE))
except:
    barrier_img = pygame.Surface((TILE_SIZE, TILE_SIZE))
    barrier_img.fill((128, 128, 128))


state = 'menu'
score = -1
man_pos = [100, 400]
man_speed = 4
end_timer_start = None
cleared_barriers = set()
level_scores = [0, 5, 10, 15, 20]
level_gates = {
    0: (270, 400),
    5: (270, 100),
    10: (530, 150),
    15: (750, 200),
    20: (800, 500)
}
gate_timer = None
gate_trigger_time = 1
current_level_index = -1
in_level_scene = False
saved_main_pos = None
active_level_score = None


level_maps = [
    [   # Level 1 map
        "                    ",
        "          B     PPPP",
        "         PPP   B    ",
        "       B      PP    ",
        "      PP   B        ",
        "PPPSP      P  P     ",
        "PPPPP              P",
        "SSSSSSSSSSSSSSSSSSSS",
    ], 
    [   # Level 2 map
        "                    ",
        "          B     PPPP",
        "         PPP   B    ",
        "       B      PP    ",
        "      PP   B        ",
        "PPPSP      P  P     ",
        "PPPPP              P",
        "SSSSSSSSSSSSSSSSSSSS",
    ],  
    [   # Level 2 map
        "                    ",
        "          B     PPPP",
        "         PPP   B    ",
        "       B      PP    ",
        "      PP   B        ",
        "PPPSP      P  P     ",
        "PPPPP              P",
        "SSSSSSSSSSSSSSSSSSSS",
    ], 
    [   # Level 4 map
        "                    ",
        "          B     PPPP",
        "         PPP   B    ",
        "       B      PP    ",
        "      PP   B        ",
        "PPPSP      P  P     ",
        "PPPPP              P",
        "SSSSSSSSSSSSSSSSSSSS",
    ], 
]

def calculate_distance(point1, point2):
    return math.sqrt((point1[0] - point2[0])**2 + (point1[1] - point2[1])**2)

def detect_click_gesture(landmarks):
    #to detect clicking gesture (thumb and index finger close together)
    if not landmarks or len(landmarks) < 21:
        return False
    
    thumb_tip = landmarks[4]
    index_tip = landmarks[8]
    
   
    distance = calculate_distance(thumb_tip, index_tip)
    
    
    return distance < 0.05

def process_camera_frame():
    #to process camera frame and track finger position
    global pointer_x, pointer_y, is_clicking, click_cooldown, finger_detected
    
    ret, frame = cap.read()
    if not ret:
        return
    
    
    frame = cv2.flip(frame, 1)
    rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    
    
    results = hands.process(rgb_frame)
    
    finger_detected = False
    
    if results.multi_hand_landmarks:
        for hand_landmarks in results.multi_hand_landmarks:
            
            landmarks = []
            for lm in hand_landmarks.landmark:
                landmarks.append([lm.x, lm.y])
            
            if len(landmarks) > 8:
                finger_tip = landmarks[8]
                
                pointer_x = int(finger_tip[0] * width)
                pointer_y = int(finger_tip[1] * height)
                finger_detected = True
                
                
                if detect_click_gesture(landmarks) and click_cooldown == 0:
                    is_clicking = True
                    click_cooldown = 15  
                else:
                    is_clicking = False
   
    if click_cooldown > 0:
        click_cooldown -= 1

def draw_pointer():
    if finger_detected:
        
        pointer_color = (255, 0, 0) if is_clicking else (0, 255, 0)
        pygame.draw.circle(screen, pointer_color, (pointer_x, pointer_y), 15)
        pygame.draw.circle(screen, (255, 255, 255), (pointer_x, pointer_y), 15, 3)
        
        
        if is_clicking:
            pygame.draw.circle(screen, (255, 255, 0), (pointer_x, pointer_y), 25, 5)
    else:
        
        no_finger_text = small_font.render("Point your index finger at the camera", True, (255, 255, 255))
        screen.blit(no_finger_text, (width//2 - no_finger_text.get_width()//2, 50))

def draw_level():
    current_map = level_maps[current_level_index]
    for row_index, row in enumerate(current_map):
        for col_index, cell in enumerate(row):
            x = col_index * TILE_SIZE
            y = row_index * TILE_SIZE
            if cell == "P":
                screen.blit(platform_img, (x, y))
            elif cell == "S":
                screen.blit(spike_img, (x, y))
            elif cell == "B":
                
                barrier_id = f"{current_level_index}{row_index}{col_index}"
                if barrier_id not in cleared_barriers:
                    screen.blit(barrier_img, (x, y))
    pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(width - 100, 0, 100, 100), 3)

def get_tiles():
    current_map = level_maps[current_level_index]
    return [pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for r, row in enumerate(current_map)
            for c, cell in enumerate(row) if cell == "P"]

def get_spikes():
    current_map = level_maps[current_level_index]
    return [pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE)
            for r, row in enumerate(current_map)
            for c, cell in enumerate(row) if cell == "S"]

def get_barriers():
    current_map = level_maps[current_level_index]
    barriers = []
    for r, row in enumerate(current_map):
        for c, cell in enumerate(row):
            if cell == "B":
                barrier_id = f"{current_level_index}{r}{c}"
                barriers.append({
                    'rect': pygame.Rect(c * TILE_SIZE, r * TILE_SIZE, TILE_SIZE, TILE_SIZE),
                    'id': barrier_id,
                    'cleared': barrier_id in cleared_barriers
                })
    return barriers


player = pygame.Rect(100, 400, 40, 50)
velocity_y = 0
jump = False
gravity = 1


class PointerButton:
    def __init__(self, text, x, y, width, height, callback):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = font.render(text, True, (0, 0, 0))
        self.callback = callback
        self.color = (255, 255, 255)
        self.hover_color = (200, 255, 200)
        self.bg_color = self.color
        self.clicked = False
    
    def draw(self, screen):
        pygame.draw.rect(screen, self.bg_color, self.rect, border_radius=20)
        pygame.draw.rect(screen, (0, 0, 0), self.rect, 3, border_radius=20)
        screen.blit(self.text, self.text.get_rect(center=self.rect.center))
    
    def update_pointer(self):
        
        if self.rect.collidepoint(pointer_x, pointer_y) and finger_detected:
            self.bg_color = self.hover_color
            if is_clicking and not self.clicked:
                self.callback()
                self.clicked = True
        else:
            self.bg_color = self.color
            self.clicked = False


def start_game():
    global state, score, man_pos, player, velocity_y, jump, end_timer_start, cleared_barriers
    score = 0
    man_pos = [100, 400]
    player.x, player.y = 100, 400
    velocity_y = 0
    jump = False
    cleared_barriers.clear()
    end_timer_start = None
    state = 'game'

def show_instructions():
    global state
    state = 'instructions'

def go_back_to_menu():
    global state
    state = 'menu'

start_button = PointerButton("Start Game", width//2 - 100, height//2 - 90, 200, 60, start_game)
instr_button = PointerButton("Instructions", width//2 - 100, height//2, 200, 60, show_instructions)
back_button = PointerButton("Back", 20, 20, 120, 50, go_back_to_menu)

def move_man_towards(target):
    global man_pos
    dx, dy = target[0] - man_pos[0], target[1] - man_pos[1]
    dist = (dx ** 2 + dy ** 2) ** 0.5
    if dist < man_speed:
        man_pos = list(target)
        return True
    else:
        man_pos[0] += man_speed * dx / dist
        man_pos[1] += man_speed * dy / dist
        return False

# Level 1: Pan Flute Challenge 
def run_music_challenge():
    pygame.init()
    music_screen = pygame.display.set_mode((1100, 600))
    pygame.display.set_caption("Pan Flute Challenge - Gesture Control")
    font = pygame.font.SysFont("arial", 28)
    clock = pygame.time.Clock()
    
    
    try:
        panflute_img = pygame.image.load("./images/panflute.png").convert_alpha()
        panflute_img = pygame.transform.scale(panflute_img, (1600, 700))
    except:
        panflute_img = pygame.Surface((1600, 700))
        panflute_img.fill((139, 69, 19))
    
    offset_y = 90
    
    
    note_labels = ['G1', 'A1', 'B1', 'C1', 'D1', 'E1', 'F1',
                   'G2', 'A2', 'B2', 'C2', 'D2', 'E2', 'F2', 'G3']
    note_rect_params = [
        (70, 100, 60, 455), (130, 100, 67, 425), (197, 100, 61, 400),
        (258, 100, 63, 360), (318, 100, 62, 325), (378, 100, 53, 305),
        (430, 100, 55, 270), (486, 100, 51, 246), (536, 100, 52, 215),
        (588, 100, 47, 200), (636, 100, 48, 175), (684, 100, 48, 160),
        (732, 100, 48, 150), (780, 100, 48, 133), (828, 100, 43, 120)
    ]
    note_rects = [pygame.Rect(x, y, w, h) for (x, y, w, h) in note_rect_params]
    
    
    note_sounds = {}
    for note in note_labels:
        try:
            note_sounds[note] = pygame.mixer.Sound(f"sounds/new/{note}.ogg")
        except:
            note_sounds[note] = None
    
    
    available_notes = [n for n in note_labels if note_sounds[n] is not None]
    sequence = random.sample(available_notes, 3)
    
    
    for note in sequence:
        idx = note_labels.index(note)
        rect = note_rects[idx]
        music_screen.fill((255, 255, 255))
        music_screen.blit(panflute_img, (0, offset_y))
        pygame.draw.rect(music_screen, (0, 255, 0), rect, 5)
        pygame.draw.rect(music_screen, (0, 0, 0), rect, 2)
        label = font.render(note, True, (0, 0, 0))
        music_screen.blit(label, (rect.x + rect.width // 2 - label.get_width() // 2, rect.y - 35))
        pygame.display.flip()
        if note_sounds[note]:
            note_sounds[note].play()
        pygame.time.wait(800)
    
    input_sequence = []
    attempts = 0
    max_attempts = 3
    note_clicked = [False] * len(note_labels)
    
    while attempts < max_attempts:
        process_camera_frame()
        
        music_screen.fill((255, 255, 255))
        music_screen.blit(panflute_img, (0, offset_y))
        
        
        for i, rect in enumerate(note_rects):
            color = None
            
            
            if rect.collidepoint(pointer_x, pointer_y - offset_y) and finger_detected:
                color = (255, 255, 180)  
                if is_clicking and not note_clicked[i]:
                    if note_sounds[note_labels[i]]:
                        note_sounds[note_labels[i]].play()
                    input_sequence.append(note_labels[i])
                    note_clicked[i] = True
            
            if not is_clicking:
                note_clicked[i] = False
            
            
            if color:
                pygame.draw.rect(music_screen, color, rect)
            pygame.draw.rect(music_screen, (0, 0, 0), rect, 1)
            
            
            label = font.render(note_labels[i], True, (0, 0, 255))
            music_screen.blit(label, (rect.x + rect.width // 2 - label.get_width() // 2, rect.y - 35))
        
        
        entered_text = font.render(f"Your Input: {' - '.join(input_sequence)}", True, (50, 50, 100))
        music_screen.blit(entered_text, (20, 550))
        
       
        draw_pointer()
        
        pygame.display.flip()
        
        
        if len(input_sequence) == len(sequence):
            pygame.time.wait(300)
            if input_sequence == sequence:
                pygame.display.set_mode((1100, 600))
                return True
            else:
                attempts += 1
                input_sequence = []
                if attempts >= max_attempts:
                    pygame.display.set_mode((1100, 600))
                    return False
        
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        clock.tick(60)
    
    pygame.display.set_mode((1100, 600))
    return False

# Level 2: Piano Challenge 
def run_level2():
    pygame.init()
    screen = pygame.display.set_mode((1100, 600))
    font = pygame.font.SysFont("arial", 20)
    big_font = pygame.font.SysFont("arial", 16)
    clock = pygame.time.Clock()

    piano_x = 50
    piano_y = 100
    white_key_width = 70
    white_key_height = 280
    black_key_width = 45
    black_key_height = 180

    white_notes = ['C1', 'D1', 'E1', 'F1', 'G1', 'A1', 'B1', 'C2', 'D2', 'E2', 'F2', 'G2', 'A2', 'B2']
    base_notes = ['C', 'D', 'E', 'F', 'G', 'A', 'B', 'C', 'D', 'E', 'F', 'G', 'A', 'B']

    white_keys = []
    for i, (note, base_note) in enumerate(zip(white_notes, base_notes)):
        x = piano_x + i * white_key_width
        white_keys.append({
            "x": x, 
            "y": piano_y,
            "width": white_key_width,
            "height": white_key_height,
            "note": note,
            "base_note": base_note,
            "rect": pygame.Rect(x, piano_y, white_key_width, white_key_height)
        })

    black_key_positions = [0, 1, 3, 4, 5, 7, 8, 10, 11, 12]
    black_keys = []
    for pos in black_key_positions:
        if pos < len(white_keys) - 1:
            x = white_keys[pos]["x"] + white_key_width - black_key_width // 2
            black_keys.append({
                "x": x,
                "y": piano_y,
                "width": black_key_width,
                "height": black_key_height,
                "rect": pygame.Rect(x, piano_y, black_key_width, black_key_height)
            })

    key_sounds = {}
    for note in ['C', 'D', 'E', 'F', 'G', 'A', 'B']:
        try:
            key_sounds[note] = pygame.mixer.Sound(f"sounds/{note}.wav")
        except:
            key_sounds[note] = None

    correct_sequence = [random.choice(white_notes) for _ in range(3)]
    user_sequence = []
    user_attempts = 0
    max_attempts = 3
    last_clicked_key = None
    feedback = ""
    key_clicked = [False] * len(white_keys)

    def draw_piano(highlight_key=None, is_system_playing=False):
        piano_frame = pygame.Rect(piano_x - 20, piano_y - 20, 
                                  len(white_keys) * white_key_width + 40, 
                                  white_key_height + 60)
        pygame.draw.rect(screen, (139, 69, 19), piano_frame)
        pygame.draw.rect(screen, (0, 0, 0), piano_frame, 3)

        for key in white_keys:
            if is_system_playing and highlight_key and key['note'] == highlight_key:
                key_color = (0, 255, 0)
            elif highlight_key and key['note'] == highlight_key:
                key_color = (255, 255, 150)
            elif last_clicked_key and key['note'] == last_clicked_key:
                key_color = (150, 255, 150)
            else:
                key_color = (255, 255, 255)

            pygame.draw.rect(screen, key_color, key['rect'])
            pygame.draw.rect(screen, (0, 0, 0), key['rect'], 2)

            if key_color == (255, 255, 255):
                gradient_rect = pygame.Rect(key['rect'].x, key['rect'].y, key['rect'].width, 20)
                pygame.draw.rect(screen, (240, 240, 240), gradient_rect)

        for black_key in black_keys:
            pygame.draw.rect(screen, (0, 0, 0), black_key['rect'])
            pygame.draw.rect(screen, (50, 50, 50), black_key['rect'], 1)
            highlight_rect = pygame.Rect(black_key['rect'].x + 5, black_key['rect'].y + 5,
                                         black_key['rect'].width - 10, 15)
            pygame.draw.rect(screen, (40, 40, 40), highlight_rect)

        for key in white_keys:
            label = big_font.render(key['note'], True, (0, 0, 0))
            label_rect = label.get_rect(center=(key['x'] + key['width']//2, key['y'] + key['height'] + 25))
            screen.blit(label, label_rect)

    def highlight_and_play_key(note):
        screen.fill((30, 30, 50))
        title = font.render("Listen carefully to the melody...", True, (255, 255, 255))
        title_rect = title.get_rect(center=(screen.get_width()//2, 50))
        screen.blit(title, title_rect)
        draw_piano(highlight_key=note, is_system_playing=True)

        listening_text = font.render("♪ ♫ ♪", True, (255, 255, 0))
        listening_rect = listening_text.get_rect(center=(screen.get_width()//2, 120))
        screen.blit(listening_text, listening_rect)

        pygame.display.flip()
        base_note = None
        for key in white_keys:
            if key['note'] == note:
                base_note = key['base_note']
                break
        if base_note and key_sounds[base_note]:
            key_sounds[base_note].play()
        pygame.time.wait(800)

    
    screen.fill((30, 30, 50))
    title = font.render("Remember the tune and play! You have 3 chances!", True, (255, 255, 255))
    screen.blit(title, title.get_rect(center=(screen.get_width()//2, 100)))
    pygame.display.flip()
    pygame.time.wait(2000)

    for note in correct_sequence:
        highlight_and_play_key(note)
        pygame.time.wait(300)

    
    while True:
        process_camera_frame()
        screen.fill((30, 30, 50))
        title = font.render("Piano Challenge", True, (255, 255, 255))
        screen.blit(title, title.get_rect(center=(screen.get_width()//2, 30)))

        hover_key = None
        for key in white_keys:
            if key['rect'].collidepoint(pointer_x, pointer_y) and finger_detected:
                hover_key = key['note']
                break

        draw_piano(highlight_key=hover_key)

        for i, key in enumerate(white_keys):
            if key['rect'].collidepoint(pointer_x, pointer_y) and finger_detected:
                if is_clicking and not key_clicked[i]:
                    note = key['note']
                    base_note = key['base_note']
                    last_clicked_key = note
                    if key_sounds[base_note]:
                        key_sounds[base_note].play()

                    user_sequence.append(note)
                    feedback = f"Played: {note}"
                    key_clicked[i] = True

                    if len(user_sequence) == len(correct_sequence):
                        if user_sequence == correct_sequence:
                            screen.fill((0, 80, 0))
                            success_text = font.render("SUCCESS! Well done!", True, (255, 255, 255))
                            screen.blit(success_text, success_text.get_rect(center=(screen.get_width()//2, 300)))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            return True
                        else:
                            user_attempts += 1
                            if user_attempts >= max_attempts:
                                screen.fill((80, 0, 0))
                                fail_text = font.render("GAME OVER! Too many attempts.", True, (255, 255, 255))
                                screen.blit(fail_text, fail_text.get_rect(center=(screen.get_width()//2, 300)))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                return False
                            else:
                                feedback = f"Wrong melody! Try again. ({user_attempts}/{max_attempts})"
                                user_sequence = []
                                last_clicked_key = None

            if not is_clicking:
                key_clicked[i] = False

        user_display_text = font.render("Your melody: ", True, (255, 255, 255))
        screen.blit(user_display_text, (piano_x, 520))
        for i, note in enumerate(user_sequence):
            color = (0, 255, 0) if i < len(correct_sequence) and note == correct_sequence[i] else (255, 0, 0)
            note_label = font.render(f"♪{note}", True, color)
            screen.blit(note_label, (piano_x + 140 + i * 80, 520))

        if feedback:
            feedback_surface = font.render(feedback, True, (255, 255, 0))
            screen.blit(feedback_surface, feedback_surface.get_rect(center=(screen.get_width()//2, 550)))

        draw_pointer()
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        clock.tick(60)


# Level 3: Drum Challenge 
def run_level3():
    pygame.init()
    screen = pygame.display.set_mode((1000, 600))
    pygame.display.set_caption("Electronic Drum Challenge - Level 3")
    font = pygame.font.SysFont("arial", 20)
    clock = pygame.time.Clock()
    
    try:
        drum_image = pygame.image.load("images/drum.png")
        drum_image = pygame.transform.scale(drum_image, (600, 400))
        drum_image_rect = drum_image.get_rect(center=(500, 280))
    except:
        drum_image = None
    
    drum_areas = [
        {"label": "Kick", "sound": "kick.wav", "rect": pygame.Rect(642,292,80,80)},
        {"label": "Snare", "sound": "snare.wav", "rect": pygame.Rect(280,292,80,80)}, 
        {"label": "Hi-Hat", "sound": "hihat.wav", "rect": pygame.Rect(547,192,80,80)},
        {"label": "Clap", "sound": "clap.wav", "rect": pygame.Rect(382, 195,80,80)}, 
    ]
    
    drum_sounds = {}
    for area in drum_areas:
        try:
            drum_sounds[area['label']] = pygame.mixer.Sound(f"sounds/{area['sound']}")
        except:
            drum_sounds[area['label']] = None
    
    correct_sequence = [random.choice([area['label'] for area in drum_areas]) for _ in range(4)]
    user_sequence = []
    user_attempts = 0
    max_attempts = 3
    feedback = ""
    last_clicked = None
    area_clicked = [False] * len(drum_areas)
    
    
    for note in correct_sequence:
        screen.fill((25, 25, 25))
        if drum_image:
            screen.blit(drum_image, drum_image_rect)
        
        for area in drum_areas:
            if area['label'] == note:
                pygame.draw.ellipse(screen, (0, 255, 0), area['rect'], 5)
            else:
                pygame.draw.ellipse(screen, (255, 255, 100), area['rect'], 6)
        
        pygame.display.flip()
        if drum_sounds[note]:
            drum_sounds[note].play()
        pygame.time.wait(700)
    
    while True:
        process_camera_frame()
        
        screen.fill((25, 25, 25))
        if drum_image:
            screen.blit(drum_image, drum_image_rect)
        
        title = font.render("Electronic Drum Challenge - Level 3", True, (255, 255, 255))
        screen.blit(title, (screen.get_width() // 2 - 180, 20))
        
        
        for i, area in enumerate(drum_areas):
            if area['rect'].collidepoint(pointer_x, pointer_y) and finger_detected:
                pygame.draw.ellipse(screen, (255, 255, 0), area['rect'], 6)
                if is_clicking and not area_clicked[i]:
                    label = area['label']
                    last_clicked = label
                    
                    if drum_sounds[label]:
                        drum_sounds[label].play()
                    user_sequence.append(label)
                    feedback = f"Played: {label}"
                    area_clicked[i] = True
                    
                    if len(user_sequence) == len(correct_sequence):
                        if user_sequence == correct_sequence:
                            screen.fill((0, 80, 0))
                            win = font.render("YOU NAILED IT!", True, (255, 255, 255))
                            screen.blit(win, win.get_rect(center=(screen.get_width() // 2, 300)))
                            pygame.display.flip()
                            pygame.time.wait(2000)
                            return True
                        else:
                            user_attempts += 1
                            if user_attempts >= max_attempts:
                                screen.fill((80, 0, 0))
                                lose = font.render("GAME OVER! Wrong rhythm.", True, (255, 255, 255))
                                screen.blit(lose, lose.get_rect(center=(screen.get_width() // 2, 300)))
                                pygame.display.flip()
                                pygame.time.wait(2000)
                                return False
                            else:
                                feedback = "Oops! Try again."
                                user_sequence = []
                                last_clicked = None
            else:
                pygame.draw.ellipse(screen, (255, 255, 100), area['rect'], 6)
            
            if not is_clicking:
                area_clicked[i] = False
        
        
        display_text = font.render("Your pattern: ", True, (255, 255, 255))
        screen.blit(display_text, (100, 500))
        for i, note in enumerate(user_sequence):
            color = (0, 255, 0) if i < len(correct_sequence) and note == correct_sequence[i] else (255, 0, 0)
            note_text = font.render(f"● {note}", True, color)
            screen.blit(note_text, (220 + i * 100, 500))
        
        if feedback:
            feed_text = font.render(feedback, True, (255, 255, 0))
            screen.blit(feed_text, (100, 540))
        
        
        draw_pointer()
        
        pygame.display.flip()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        clock.tick(60)

# Level 4: Guitar Challenge 
def run_guitar_challenge():
    guitar_screen = pygame.display.set_mode((1100, 600))
    pygame.display.set_caption("Guitar Pattern Challenge - Gesture Control")
    font = pygame.font.SysFont("arial", 28)
    clock = pygame.time.Clock()
    
    try:
        fretboard_img = pygame.image.load("images/guitarKey.png").convert_alpha()
        fretboard_img = pygame.transform.scale(fretboard_img, (900, 180))
    except:
        fretboard_img = pygame.Surface((900, 180))
        fretboard_img.fill((120, 80, 40))
    
    fretboard_x = 100
    fretboard_y = 200
    
    key_width = 180
    key_height = 40
    key_spacing = 20
    key_rects = []
    for i in range(4):
        rect = pygame.Rect(
            fretboard_x + i * (key_width + key_spacing),
            fretboard_y + 70,
            key_width,
            key_height
        )
        key_rects.append(rect)
    
    # Load guitar sounds
    guitar_sounds = []
    for i in range(1, 5):
        try:
            guitar_sounds.append(pygame.mixer.Sound(f"sounds/guitar{i}.wav"))
        except:
            guitar_sounds.append(None)
    
    sequence = [random.randint(0, 3) for _ in range(3)]
    
    # Show sequence
    for idx in sequence:
        guitar_screen.fill((30, 30, 60))
        guitar_screen.blit(fretboard_img, (fretboard_x, fretboard_y))
        for i, rect in enumerate(key_rects):
            color = (255, 255, 0) if i == idx else (0, 0, 0)
            pygame.draw.rect(guitar_screen, color, rect, 4)
        pygame.display.flip()
        if guitar_sounds[idx]:
            guitar_sounds[idx].play()
        pygame.time.wait(600)
    
    input_sequence = []
    attempts = 0
    max_attempts = 3
    key_clicked = [False] * len(key_rects)
    
    while attempts < max_attempts:
        process_camera_frame()
        
        guitar_screen.fill((30, 30, 60))
        guitar_screen.blit(fretboard_img, (fretboard_x, fretboard_y))
        
        
        for i, rect in enumerate(key_rects):
            if rect.collidepoint(pointer_x, pointer_y) and finger_detected:
                pygame.draw.rect(guitar_screen, (100, 255, 100), rect, 0)
                if is_clicking and not key_clicked[i]:
                    if guitar_sounds[i]:
                        guitar_sounds[i].play()
                    input_sequence.append(i)
                    key_clicked[i] = True
            else:
                pygame.draw.rect(guitar_screen, (0, 0, 0), rect, 2)
            
            if not is_clicking:
                key_clicked[i] = False
        
        entered_text = font.render(f"Your Input: {' - '.join(str(i+1) for i in input_sequence)}", True, (255, 255, 255))
        guitar_screen.blit(entered_text, (20, 550))
        
        
        draw_pointer()
        
        pygame.display.flip()
        
        if len(input_sequence) == len(sequence):
            pygame.time.wait(300)
            if input_sequence == sequence:
                pygame.display.set_mode((1100, 600))
                return True
            else:
                attempts += 1
                input_sequence = []
                if attempts >= max_attempts:
                    pygame.display.set_mode((1100, 600))
                    return False
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
        
        clock.tick(60)
    
    pygame.display.set_mode((1100, 600))
    return False


barrier_cooldown = 0
run = True
jump_click_used = False

while run:
    
    process_camera_frame()
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        elif state == 'game' and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP and not in_level_scene:
                score += 1
                gate_timer = None
    
    if barrier_cooldown > 0:
        barrier_cooldown -= 1
    
    if state == 'menu':
        screen.blit(start_bg, (0, 0))
        start_button.update_pointer()
        instr_button.update_pointer()
        start_button.draw(screen)
        instr_button.draw(screen)
        
        
        instr_text = small_font.render("Point your finger and pinch to click buttons", True, (255, 255, 255))
        screen.blit(instr_text, (20, height - 40))
        
    elif state == 'instructions':
        screen.fill((30, 30, 30))
        back_button.update_pointer()
        back_button.draw(screen)
        
        instructions = [
            "POINTER CONTROLS:",
            "• Point your index finger to move the pointer",
            "• Pinch thumb and index finger to click and jump",
            "• Move pointer left/right to control character",
            "• 4 levels in game, go through each level to win",
            "• Avoid bombs, reach red square!",
            "• Musical Barriers in between lead to",
            "  music challenge",
            "• Follow the tune to go ahead",
            "• You have 3 chances",
        ]
        
        for i, instr in enumerate(instructions):
            text = font.render(instr, True, (255, 255, 255))
            screen.blit(text, (50, 150 + i * 40))
    
    elif state == 'win':
        if end_timer_start is None:
            end_timer_start = time.time()
        screen.fill((0, 100, 0))
        win_text = font.render(f"YOU WIN! Final Score: {score}", True, (255, 255, 0))
        screen.blit(win_text, (width//2 - win_text.get_width()//2, height//2 - 20))
        if time.time() - end_timer_start >= 7:
            pygame.quit()
            sys.exit()
    
    elif state == 'gameover':
        if end_timer_start is None:
            end_timer_start = time.time()
        screen.fill((100, 0, 0))
        over_text = font.render(f"GAME OVER! Final Score: {score}", True, (255, 255, 255))
        screen.blit(over_text, (width//2 - over_text.get_width()//2, height//2 - 20))
        if time.time() - end_timer_start >= 7:
            pygame.quit()
            sys.exit()
    
    elif state == 'game':
        if man_pos[0] == 800 and man_pos[1] == 500:
            time.sleep(2)
            state = 'win'
            end_timer_start = None
            continue
        
        if in_level_scene:
            screen.blit(level_backgrounds[current_level_index], (0, 0))
            draw_level()
            
            
            dx = dy = 0
            
            
            if finger_detected:
                if pointer_x < width * 0.4:  
                    dx = -5
                elif pointer_x > width * 0.6:  
                    dx = 5
                
                
                if is_clicking and not jump and not jump_click_used:
                    velocity_y = -20
                    jump = True
                    jump_click_used = True
                elif not is_clicking:
                    jump_click_used = False
            
            velocity_y += gravity
            dy += velocity_y
            
            player.x += dx
            player.y += dy
            
            
            for tile in get_tiles():
                if player.colliderect(tile):
                    if dy > 0:
                        player.bottom = tile.top
                        velocity_y = 0
                        jump = False
                    elif dy < 0:
                        player.top = tile.bottom
                        velocity_y = 0
            
            for spike in get_spikes():
                if player.colliderect(spike):
                    in_level_scene = False
                    state = 'gameover'
                    end_timer_start = None
                    break
            
            barriers = get_barriers()
            for barrier in barriers:
                if (player.colliderect(barrier['rect']) and
                     not barrier['cleared'] and
                     barrier_cooldown == 0):
                    
                    if current_level_index == 0:
                        result = run_music_challenge()  # Level 1 (Pan Flute)
                    elif current_level_index == 1:
                        result = run_level2()  # Level 2 (Piano)
                    elif current_level_index == 2:
                        result = run_level3()  # Level 3 (Drum)
                    elif current_level_index == 3:
                        result = run_guitar_challenge()  # Level 4 (Guitar)
                    else:
                        result = True
                    
                    if result:
                        cleared_barriers.add(barrier['id'])
                        player.x += 10
                    else:
                        in_level_scene = False
                        state = 'gameover'
                        end_timer_start = None
                    barrier_cooldown = 30
                    break
            
            
            goal_zone = pygame.Rect(width - 100, 0, 100, 100)
            if player.colliderect(goal_zone):
                score += 5
                in_level_scene = False
                player.x, player.y = 100, 400
                velocity_y = 0
                jump = False
                current_level_index = -1
                active_level_score = None
                man_pos = list(saved_main_pos)
            
            pygame.draw.rect(screen, (0, 255, 0), player)
        
        else:
            screen.blit(main_bg, (0, 0))
            if score in level_gates and score != active_level_score:
                if move_man_towards(level_gates[score]):
                    if gate_timer is None:
                        gate_timer = time.time()
                    elif time.time() - gate_timer >= gate_trigger_time:
                        saved_main_pos = list(man_pos)
                        in_level_scene = True
                        current_level_index = level_scores.index(score)
                        active_level_score = score
                        gate_timer = None
            
            screen.blit(man_img, man_pos)
        
        score_text = font.render(f"Score: {score}", True, (255, 255, 255))
        screen.blit(score_text, (20, 20))
    
    
    draw_pointer()
    
    pygame.display.update()
    clock.tick(60)


cap.release()
cv2.destroyAllWindows()
pygame.quit()
sys.exit()
