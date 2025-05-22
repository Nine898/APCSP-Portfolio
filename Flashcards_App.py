from tkinter import filedialog, messagebox
import pygame
import random
import sys
import time
import os
import colorsys
import json

pygame.init()
pygame.mixer.init()

WIDTH, HEIGHT = 800, 600
FPS = 180

WHITE  = (255, 255, 255)
BLACK  = (0, 0, 0)
GREEN  = (0, 200, 0)
RED    = (200, 0, 0)
BLUE   = (50, 50, 255)
GRAY   = (200, 200, 200)

FONT = pygame.font.Font(None, 36)
BIG_FONT = pygame.font.Font(None, 48)

def show_feedback(message, duration=1500, color=RED, y_offset=0):
    screen.fill(WHITE)
    text = FONT.render(message, True, color)
    text_rect = text.get_rect(center=(WIDTH//2, HEIGHT//2 + y_offset))
    screen.blit(text, text_rect)
    pygame.display.flip()
    pygame.time.wait(duration)

def create_button(text, x, y, width, height, color=GRAY):
    button = pygame.Rect(x, y, width, height)
    return {"rect": button, "text": text, "color": color}

def draw_button_list(buttons):
    for button in buttons:
        draw_button(button["text"], button["rect"], button["color"])

def handle_button_click(button_rect, flashcards, action_fn, empty_message="Please enter flashcards first!"):
    if flashcards or action_fn == enter_flashcards:
        return action_fn(flashcards) if flashcards else action_fn()
    else:
        show_feedback(empty_message)
    return flashcards

def create_text_surface(text, font=FONT, color=BLACK, centered=True):
    text_surface = font.render(text, True, color)
    if centered:
        return text_surface, text_surface.get_rect(center=(WIDTH//2, HEIGHT//2))
    return text_surface

def get_wrapped_text_height(text, font, max_width):
    lines = wrap_text(text, font, max_width)
    return len(lines) * font.get_height()

def render_wrapped_text(text, font, max_width, start_x, start_y, color=BLACK, centered=False):
    lines = wrap_text(text, font, max_width)
    total_height = 0
    for line in lines:
        text_surface = font.render(line, True, color)
        if centered:
            x = start_x + (max_width - text_surface.get_width()) // 2
        else:
            x = start_x
        screen.blit(text_surface, (x, start_y + total_height))
        total_height += font.get_height()
    return total_height

def handle_scroll(current_offset, max_scroll, event):
    if event.type == pygame.MOUSEWHEEL:
        return max(0, min(current_offset - event.y * 10, max_scroll))
    elif event.type == pygame.KEYDOWN:
        if event.key == pygame.K_UP:
            return max(0, current_offset - 10)
        elif event.key == pygame.K_DOWN:
            return min(current_offset + 10, max_scroll)
    return current_offset

def check_quit_event(event):
    if event.type == pygame.QUIT:
        pygame.quit()
        sys.exit()

def center_rect(width, height, y_offset=0):
    return pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2 + y_offset, width, height)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Flashcard App")
clock = pygame.time.Clock()


class Flashcard:
   def __init__(self, front, back):
       self.front = front
       self.back = back
       self.showing_front = True
   def flip(self):
       self.showing_front = not self.showing_front


# Text rendering utilities
def get_wrapped_lines(text, font, max_width):
    words = text.split()
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + (" " if current_line else "") + word
        if font.size(test_line)[0] <= max_width - 20:  # 20px margin
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word
    if current_line:
        lines.append(current_line)
    return lines

def calculate_text_dimensions(lines, font):
    line_height = font.get_height()
    total_height = len(lines) * line_height
    return line_height, total_height

def draw_text_in_box(text, rect, font, color, scroll_offset=0, target_surface=screen):
    x, y, width, height = rect
    lines = get_wrapped_lines(text, font, width)
    line_height, total_text_height = calculate_text_dimensions(lines, font)

    start_y = y + (height - total_text_height) // 2 - scroll_offset if total_text_height < height else y - scroll_offset

    for line in lines:
        rendered_line = font.render(line, True, color)
        line_width = rendered_line.get_width()
        line_x = x + (width - line_width) // 2
        target_surface.blit(rendered_line, (line_x, start_y))
        start_y += line_height

def draw_flashcard(card, pos=(100, 200), size=(600, 200), scroll_offset=0):
    x, y = pos
    w, h = size
    bg_color = getattr(card, "color", (0, 0, 0))
    pygame.draw.rect(screen, bg_color, (x, y, w, h))
    text = card.front if card.showing_front else card.back
    draw_text_in_box(text, (x, y, w, h), FONT, WHITE, scroll_offset)

def create_centered_rect(width, height, y_offset=0):
    return pygame.Rect((WIDTH - width) // 2, (HEIGHT - height) // 2 + y_offset, width, height)

def create_button_pair(y_pos, width=200, height=50, spacing=200):
    left_rect = pygame.Rect((WIDTH - width * 2 - spacing) // 2, y_pos, width, height)
    right_rect = pygame.Rect(left_rect.right + spacing, y_pos, width, height)
    return left_rect, right_rect

def draw_button(text, rect, color=GRAY):
    pygame.draw.rect(screen, color, rect)
    pygame.draw.rect(screen, WHITE, rect, 3)
    text_rendered = FONT.render(text, True, BLACK)
    text_rect = text_rendered.get_rect(center=rect.center)
    screen.blit(text_rendered, text_rect)

def render_flashcard_surface(card, size=(600, 200)):
    surface = pygame.Surface(size, pygame.SRCALPHA)
    bg_color = getattr(card, "color", (0, 0, 0))
    surface.fill(bg_color)
    text = card.front if card.showing_front else card.back
    draw_text_in_box(text, (0, 0, size[0], size[1]), FONT, WHITE, 0, target_surface=surface)
    return surface

def wrap_text(text, font, max_width):
    words = text.split(' ')
    lines = []
    current_line = ""
    for word in words:
        test_line = current_line + word + " "
        width, _ = font.size(test_line)
        if width > max_width and current_line != "":
            lines.append(current_line)
            current_line = word + " "
        else:
            current_line = test_line
    lines.append(current_line)
    return lines


# Input handling utilities
def handle_text_input(event, current_text, cursor_pos):
    if event.key == pygame.K_BACKSPACE and cursor_pos > 0:
        return current_text[:cursor_pos-1] + current_text[cursor_pos:], cursor_pos - 1
    elif event.key == pygame.K_DELETE and cursor_pos < len(current_text):
        return current_text[:cursor_pos] + current_text[cursor_pos+1:], cursor_pos
    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
        return None, None
    elif event.key == pygame.K_LEFT:
        return current_text, max(0, cursor_pos - 1)
    elif event.key == pygame.K_RIGHT:
        return current_text, min(len(current_text), cursor_pos + 1)
    elif event.key == pygame.K_HOME:
        return current_text, 0
    elif event.key == pygame.K_END:
        return current_text, len(current_text)
    else:
        return current_text[:cursor_pos] + event.unicode + current_text[cursor_pos:], cursor_pos + len(event.unicode)

def get_text_input(prompt):
    input_text = ""
    cursor_pos = 0
    active = True
    blink_timer = 0
    show_cursor = True

    while active:
        screen.fill(WHITE)
        prompt_surface = FONT.render(prompt, True, BLACK)
        prompt_x = (WIDTH - prompt_surface.get_width()) // 2
        prompt_y = (HEIGHT - prompt_surface.get_height()) // 2 - 50
        screen.blit(prompt_surface, (prompt_x, prompt_y))
        input_rect = pygame.Rect((WIDTH - 700) // 2, prompt_y + prompt_surface.get_height() + 20, 700, 150)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)

        # Split text at cursor position
        text_before_cursor = input_text[:cursor_pos]
        text_after_cursor = input_text[cursor_pos:]

        # Calculate cursor position in wrapped text
        wrapped_before = wrap_text(text_before_cursor, FONT, input_rect.width - 20)
        full_text_wrapped = wrap_text(input_text, FONT, input_rect.width - 20)

        # Draw text and cursor
        y_offset = input_rect.top + 5
        current_pos = 0
        cursor_x, cursor_y = input_rect.left + 10, y_offset

        for i, line in enumerate(full_text_wrapped):
            line_surf = FONT.render(line, True, BLACK)
            screen.blit(line_surf, (input_rect.left + 10, y_offset))

            # Find cursor position
            if current_pos + len(line) >= cursor_pos and current_pos <= cursor_pos:
                cursor_x = input_rect.left + 10 + FONT.size(line[:cursor_pos - current_pos])[0]
                cursor_y = y_offset

            current_pos += len(line)
            y_offset += FONT.get_height()

        # Draw blinking cursor
        blink_timer += 1
        if blink_timer >= FPS // 2:
            show_cursor = not show_cursor
            blink_timer = 0

        if show_cursor:
            pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), 
                           (cursor_x, cursor_y + FONT.get_height()), 2)

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN:
                    active = False
                    break
                elif event.key == pygame.K_BACKSPACE:
                    if cursor_pos > 0:
                        input_text = input_text[:cursor_pos-1] + input_text[cursor_pos:]
                        cursor_pos -= 1
                elif event.key == pygame.K_DELETE:
                    if cursor_pos < len(input_text):
                        input_text = input_text[:cursor_pos] + input_text[cursor_pos+1:]
                elif event.key == pygame.K_LEFT:
                    cursor_pos = max(0, cursor_pos - 1)
                elif event.key == pygame.K_RIGHT:
                    cursor_pos = min(len(input_text), cursor_pos + 1)
                elif event.key == pygame.K_HOME:
                    cursor_pos = 0
                elif event.key == pygame.K_END:
                    cursor_pos = len(input_text)
                else:
                    input_text = input_text[:cursor_pos] + event.unicode + input_text[cursor_pos:]
                    cursor_pos += len(event.unicode)
                show_cursor = True
                blink_timer = 0

        clock.tick(FPS)

    return input_text

def get_answer_input(question):
   input_text = ""
   active = True
   while active:
       screen.fill(WHITE)
       question_surface = BIG_FONT.render(question, True, BLACK)
       qs_rect = question_surface.get_rect(center=(WIDTH // 2, 150))
       screen.blit(question_surface, qs_rect.topleft)
       answer_label = FONT.render("Answer:", True, BLACK)
       screen.blit(answer_label, (50, 300))
       input_rect = pygame.Rect(150, 290, 500, 50)
       pygame.draw.rect(screen, GRAY, input_rect)
       pygame.draw.rect(screen, BLACK, input_rect, 2)
       input_surface = FONT.render(input_text, True, BLACK)
       screen.blit(input_surface, (input_rect.x + 10, input_rect.y + 10))
       pygame.display.flip()
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               pygame.quit(); sys.exit()
           elif event.type == pygame.KEYDOWN:
               if event.key == pygame.K_RETURN:
                   active = False
                   break
               elif event.key == pygame.K_BACKSPACE:
                   input_text = input_text[:-1]
               else:
                   input_text += event.unicode
       clock.tick(FPS)
   return input_text


FLASHCARD_FILE = "flashcards.json"


def save_flashcards(flashcards):
    data = [{"front": card.front, "back": card.back} for card in flashcards]
    with open(FLASHCARD_FILE, "w") as f:
        json.dump(data, f)

def load_flashcards():
    try:
        with open(FLASHCARD_FILE, "r") as f:
            data = json.load(f)
        return [Flashcard(item["front"], item["back"]) for item in data]
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def enter_flashcards():
    flashcards = load_flashcards()
    scroll_offset = 0
    max_scroll = 0
    scroll_speed = 30

    running = True
    while running:
        screen.fill(WHITE)

        initial_button_y = 120  
        button_spacing = 40  
        dynamic_button_y = initial_button_y + (len(flashcards) * button_spacing)

        max_scroll = max(0, (len(flashcards) * 30) - (HEIGHT - 250))

        header = FONT.render("Flashcards Entered:", True, BLACK)
        screen.blit(header, (50, 30 - scroll_offset))

        for i, card in enumerate(flashcards):
            card_text = f"{i+1}. {card.front} → {card.back}"
            wrapped_text = wrap_text(card_text, FONT, WIDTH - 100)
            y_pos = 60 + i * 30 - scroll_offset

            for line in wrapped_text:
                card_surface = FONT.render(line, True, BLACK)
                screen.blit(card_surface, (50, y_pos))
                y_pos += FONT.get_height()

        button_width, button_height = 250, 80
        add_button = pygame.Rect((WIDTH // 2) - (button_width + 20), dynamic_button_y, button_width, button_height)
        remove_button = pygame.Rect((WIDTH // 2) + 10, dynamic_button_y, button_width, button_height)
        exit_button = pygame.Rect((WIDTH // 2) - (button_width // 2), dynamic_button_y + 100, button_width, button_height) 

        pygame.draw.rect(screen, GREEN, add_button)
        pygame.draw.rect(screen, RED, remove_button)
        pygame.draw.rect(screen, GRAY, exit_button)

        add_text = FONT.render("Add Flashcard", True, WHITE)
        remove_text = FONT.render("Remove Flashcard", True, WHITE)
        exit_text = FONT.render("Return", True, WHITE)

        screen.blit(add_text, (add_button.x + (button_width - add_text.get_width()) // 2,
                               add_button.y + (button_height - add_text.get_height()) // 2))
        screen.blit(remove_text, (remove_button.x + (button_width - remove_text.get_width()) // 2,
                                  remove_button.y + (button_height - remove_text.get_height()) // 2))
        screen.blit(exit_text, (exit_button.x + (button_width - exit_text.get_width()) // 2,
                                exit_button.y + (button_height - exit_text.get_height()) // 2))

        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if add_button.collidepoint(x, y):
                    front = get_text_input("Enter flashcard FRONT:")
                    back = get_text_input("Enter flashcard BACK:")
                    flashcards.append(Flashcard(front, back)) 
                    save_flashcards(flashcards)
                elif remove_button.collidepoint(x, y) and flashcards:
                    remove_screen = True
                    while remove_screen:
                        screen.fill(WHITE)
                        index_str = get_text_input("Enter comma-separated flashcard numbers to remove:")
                        try:
                            indices = [int(i.strip()) - 1 for i in index_str.split(',')]
                            if all(0 <= i < len(flashcards) for i in indices):
                                for i in sorted(indices, reverse=True):
                                    del flashcards[i]
                                    save_flashcards(flashcards)
                                    show_feedback("Selected flashcards removed!", color=GREEN)
                                    return flashcards
                            else:
                                show_feedback("Invalid numbers! Please enter valid flashcard numbers.", color=RED)
                        except ValueError:
                            show_feedback("Please enter valid numbers separated by commas.", color=RED)
                    clock.tick(FPS)
                elif exit_button.collidepoint(x, y):
                    running = False  
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 10)
                elif event.key == pygame.K_DOWN:
                    scroll_offset = min(scroll_offset + 10, max_scroll)
                    while event.type == pygame.KEYDOWN and event.key == pygame.K_DOWN:
                        scroll_offset = min(scroll_offset + 10, max_scroll)
                        event = pygame.event.wait()
    return flashcards



def animate_shuffle(flashcards):
    import random
    if not flashcards:
        return flashcards
    existing_colors = set()
    for card in flashcards:
        while True:
            r = random.randint(50, 255)
            g = random.randint(50, 255)
            b = random.randint(50, 255)
            if g > 130 and r > 130 and b < 100:
                continue
            new_color = (r, g, b)
            if new_color not in existing_colors:
                existing_colors.add(new_color)
                card.color = new_color
                break
    scatter_duration = 1.2
    converge_duration = 1.2
    base_x, base_y = 100, 200
    num_cards = len(flashcards)
    initial_positions = [(base_x + i * 3, base_y + i * 3) for i in range(num_cards)]
    scatter_positions = []
    scatter_rotations = []
    for i in range(num_cards):
        dx = random.randint(-200, 200)
        dy = random.randint(-150, 150)
        scatter_positions.append((initial_positions[i][0] + dx, initial_positions[i][1] + dy))
        scatter_rotations.append(random.randint(-90, 90))
    front_card = flashcards[0]

    def lerp(a, b, t):
        return a + (b - a) * t

    def lerp_tuple(a, b, t):
        return (lerp(a[0], b[0], t), lerp(a[1], b[1], t))

    scatter_start = time.time()
    while True:
        t_elapsed = time.time() - scatter_start
        if t_elapsed >= scatter_duration:
            break
        t_frac = t_elapsed / scatter_duration  
        screen.fill(WHITE)
        for i, card in enumerate(flashcards):
            cur_pos = lerp_tuple(initial_positions[i], scatter_positions[i], t_frac)
            cur_rot = lerp(0, scatter_rotations[i], t_frac)
            if card == front_card:
                extra_rot = 90 * t_frac
                cur_rot += extra_rot
            card_surface = render_flashcard_surface(card, size=(600, 200))
            rotated_surface = pygame.transform.rotate(card_surface, cur_rot)
            rect = rotated_surface.get_rect(center=(cur_pos[0] + 300, cur_pos[1] + 100))
            screen.blit(rotated_surface, rect.topleft)
        pygame.display.flip()
        clock.tick(FPS)

    new_order = flashcards[:]
    random.shuffle(new_order)
    final_positions = {}
    for j, card in enumerate(new_order):
        final_positions[card] = (base_x + j * 3, base_y + j * 3)

    converge_start = time.time()
    while True:
        t_elapsed = time.time() - converge_start
        if t_elapsed >= converge_duration:
            break
        t_frac = t_elapsed / converge_duration  
        screen.fill(WHITE)
        for i, card in enumerate(flashcards):
            start_pos = scatter_positions[i]
            final_pos = final_positions[card]
            cur_pos = lerp_tuple(start_pos, final_pos, t_frac)
            cur_rot = lerp(scatter_rotations[i], 0, t_frac)
            if card == front_card:
                extra_rot = 90 * (1 - t_frac)
                cur_rot += extra_rot
            card_surface = render_flashcard_surface(card, size=(600, 200))
            rotated_surface = pygame.transform.rotate(card_surface, cur_rot)
            rect = rotated_surface.get_rect(center=(cur_pos[0] + 300, cur_pos[1] + 100))
            screen.blit(rotated_surface, rect.topleft)
        pygame.display.flip()
        clock.tick(FPS)
    flashcards[:] = new_order
    return flashcards


def animate_reverse(flashcards):
    def rotate_color(color, factor):
        r, g, b = color
        r_norm, g_norm, b_norm = r / 255.0, g / 255.0, b / 255.0
        h, s, v = colorsys.rgb_to_hsv(r_norm, g_norm, b_norm)
        h_new = (h + 0.5 * factor) % 1.0
        r_new, g_new, b_new = colorsys.hsv_to_rgb(h_new, s, v)
        return (int(r_new * 255), int(g_new * 255), int(b_new * 255))

    num_steps = 15
    for card in flashcards:
        original_color = getattr(card, "color", (0, 0, 0))
        for i in range(num_steps):
            screen.fill(WHITE)
            squeeze_factor = abs((i - num_steps/2) / (num_steps/2))
            new_width = max(1, int(600 * squeeze_factor))
            x = 100 + (600 - new_width) // 2
            t = i / (num_steps - 1)
            rotated_bg = rotate_color(original_color, t)
            temp_surface = pygame.Surface((new_width, 200))
            temp_surface.fill(rotated_bg)
            if i < num_steps/2:
                text = card.front if card.showing_front else card.back
            else:
                text = card.back if card.showing_front else card.front

            draw_text_in_box(text, (0, 0, new_width, 200), FONT, WHITE, 0, target_surface=temp_surface)
            screen.blit(temp_surface, (x, 200))
            pygame.display.flip()
            clock.tick(30)
        card.flip()
        card.color = rotate_color(original_color, 1)
    return flashcards


def animate_flip(card):
    num_steps = 15
    card_pos = (100, 200)
    card_size = (600, 200)

    for i in range(num_steps):
        screen.fill(WHITE)
        instruction = "Track Progress: SPACE to flip"
        instr_surface = FONT.render(instruction, True, BLACK)
        screen.blit(instr_surface, (WIDTH // 2 - instr_surface.get_width() // 2, 30))
        factor = abs((i - num_steps/2) / (num_steps/2))
        new_width = max(1, int(card_size[0] * factor))
        x = card_pos[0] + (card_size[0] - new_width) // 2 
        temp_surface = pygame.Surface((new_width, card_size[1]))
        temp_surface.fill(getattr(card, "color", (0, 0, 0))) # Use card color here
        pygame.draw.rect(temp_surface, WHITE, (0, 0, new_width, card_size[1]), 3)

        if i < num_steps/2:
            text = card.front if card.showing_front else card.back
        else:
            text = card.back if card.showing_front else card.front
        draw_text_in_box(text, (0, 0, new_width, card_size[1]), FONT, WHITE, 0, target_surface=temp_surface)

        screen.blit(temp_surface, (x, card_pos[1]))
        pygame.display.flip()
        pygame.time.wait(30)
    card.flip()

def track_progress_mode(flashcards):
    known_cards = []
    unknown_cards = []
    index = 0
    scroll_offset = 0
    total_cards = len(flashcards)

    for card in flashcards:
        if not hasattr(card, "color") or card.color == (0, 0, 0):
            card.color = (random.randint(50, 255), random.randint(50, 255), random.randint(50, 255))

    while index < total_cards:
        screen.fill(WHITE)
        instruction = "Track Progress: SPACE to flip"
        instr_surface = FONT.render(instruction, True, BLACK)
        screen.blit(instr_surface, (WIDTH // 2 - instr_surface.get_width() // 2, 30))

        draw_flashcard(flashcards[index], scroll_offset=scroll_offset)

        known_rect = pygame.Rect(100, 450, 200, 50)
        unknown_rect = pygame.Rect(500, 450, 200, 50)
        draw_button("Known", known_rect, GREEN)
        draw_button("Unknown", unknown_rect, RED)
        pygame.display.flip()

        decision_made = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset = max(0, scroll_offset - event.y * 10)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    scroll_offset = max(0, scroll_offset - 10)
                elif event.key == pygame.K_DOWN:
                    scroll_offset += 10
                elif event.key == pygame.K_SPACE:
                    animate_flip(flashcards[index])
                elif event.key == pygame.K_LEFT:
                    flashcards[index].color = (0, 200, 0) 
                    known_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True
                elif event.key == pygame.K_RIGHT:
                    flashcards[index].color = (200, 0, 0)  
                    unknown_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                if known_rect.collidepoint(x, y):
                    flashcards[index].color = (0, 200, 0)
                    known_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True
                elif unknown_rect.collidepoint(x, y):
                    flashcards[index].color = (200, 0, 0)
                    unknown_cards.append(flashcards[index])
                    index += 1
                    scroll_offset = 0
                    decision_made = True

        if decision_made:
            pygame.time.wait(200)
        clock.tick(FPS)

    screen.fill(WHITE)
    summary_text = f"Review complete! Known: {len(known_cards)} | Unknown: {len(unknown_cards)}"
    summary_surface = BIG_FONT.render(summary_text, True, BLACK)
    screen.blit(summary_surface, (WIDTH // 2 - summary_surface.get_width() // 2, HEIGHT // 2 - 50))
    pygame.display.flip()
    pygame.time.wait(2000)

    if unknown_cards:
        retry = None
        while retry is None:
            screen.fill(WHITE)
            prompt = "Retry unknown flashcards? (Y/N)"
            prompt_surface = FONT.render(prompt, True, BLACK)
            screen.blit(prompt_surface, (WIDTH // 2 - prompt_surface.get_width() // 2, HEIGHT // 2))
            pygame.display.flip()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_y:
                        retry = True
                    elif event.key == pygame.K_n:
                        retry = False
        if retry:
            track_progress_mode(unknown_cards)
    return known_cards, unknown_cards


def test_yourself_mode(flashcards):
    if not flashcards:
        return

    num_cards = None
    while num_cards is None or num_cards > len(flashcards) or num_cards <= 0:  
        screen.fill(WHITE)

        if num_cards is not None:
            if num_cards > len(flashcards):
                show_feedback(f"Please choose a number between 1 and {len(flashcards)}")
            elif num_cards <= 0:
                show_feedback("Please enter a positive number")

        num_str = get_text_input("Enter the number of flashcards to test:")
        try:
            num_cards = int(num_str)
            if num_cards > len(flashcards):
                num_cards = None  # Reset so it prompts the user again
        except ValueError:
            show_feedback("Please input a valid number.", color=RED)

    test_cards = random.sample(flashcards, num_cards)
    score = 0

    for card in test_cards:
        card.showing_front = True

        screen.fill(WHITE)

        question = f"What is the back of this flashcard: {card.front}?"
        wrapped_question = wrap_text(question, FONT, WIDTH - 100)
        y_start = 100  
        for i, line in enumerate(wrapped_question):
            line_surf = FONT.render(line, True, BLACK)
            x = (WIDTH - line_surf.get_width()) // 2
            screen.blit(line_surf, (x, y_start + i * FONT.get_height()))

        answer_prompt = "Your Answer:"
        prompt_surf = FONT.render(answer_prompt, True, BLACK)
        screen.blit(prompt_surf, (50, HEIGHT - 275))

        input_rect = pygame.Rect(50, HEIGHT - 245, WIDTH - 100, 100)
        pygame.draw.rect(screen, GRAY, input_rect)
        pygame.draw.rect(screen, BLACK, input_rect, 2)
        pygame.display.flip()

        answer = ""
        cursor_pos = 0
        active = True
        blink_timer = 0
        show_cursor = True
        while active:
            pygame.draw.rect(screen, GRAY, input_rect)
            pygame.draw.rect(screen, BLACK, input_rect, 2)

            # Split text at cursor position
            text_before_cursor = answer[:cursor_pos]
            text_after_cursor = answer[cursor_pos:]

            # Calculate cursor position in wrapped text
            wrapped_before = wrap_text(text_before_cursor, FONT, input_rect.width - 20)
            full_text_wrapped = wrap_text(answer, FONT, input_rect.width - 20)

            # Draw text and cursor
            y_offset = input_rect.top + 5
            current_pos = 0
            cursor_x, cursor_y = input_rect.left + 10, y_offset

            for i, line in enumerate(full_text_wrapped):
                line_surf = FONT.render(line, True, BLACK)
                screen.blit(line_surf, (input_rect.left + 10, y_offset))

                # Find cursor position
                if current_pos + len(line) >= cursor_pos and current_pos <= cursor_pos:
                    cursor_x = input_rect.left + 10 + FONT.size(line[:cursor_pos - current_pos])[0] if cursor_pos - current_pos >= 0 else input_rect.left + 10
                    cursor_y = y_offset

                current_pos += len(line)
                y_offset += FONT.get_height()

            # Draw blinking cursor
            blink_timer += 1
            if blink_timer >= FPS // 2:
                show_cursor = not show_cursor
                blink_timer = 0

            if show_cursor:
                pygame.draw.line(screen, BLACK, (cursor_x, cursor_y), 
                               (cursor_x, cursor_y + FONT.get_height()), 2)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        active = False
                        break
                    else:
                        answer, cursor_pos = handle_text_input(event, answer, cursor_pos)
                        show_cursor = True
                        blink_timer = 0
            clock.tick(FPS)

        if answer.strip().lower() == card.back.strip().lower():
            score += 1
        else:
            screen.fill(WHITE)
            correct_text = f"Correct Answer: {card.back}"
            wrapped_correct = wrap_text(correct_text, BIG_FONT, WIDTH - 100)
            total_height = len(wrapped_correct) * BIG_FONT.get_height()
            start_y = (HEIGHT - total_height) // 2
            for i, line in enumerate(wrapped_correct):
                line_surf = BIG_FONT.render(line, True, BLACK)
                x = (WIDTH - line_surf.get_width()) // 2
                screen.blit(line_surf, (x, start_y + i * BIG_FONT.get_height()))
            pygame.display.flip()
            pygame.time.wait(1500)

    screen.fill(WHITE)
    result_text = f"You scored {score} out of {num_cards}"
    result_surface = BIG_FONT.render(result_text, True, BLACK)
    screen.blit(result_surface, ((WIDTH - result_surface.get_width()) // 2,
                                  (HEIGHT - result_surface.get_height()) // 2))
    pygame.display.flip()
    pygame.time.wait(3000)


def display_flashcards_text(flashcards):
    items = []
    for card in flashcards:
        items.append(f"Front: {card.front}\nBack:  {card.back}")
    for item in items:
        print(f"{item}\n")

    scroll_offset = 0
    active = True
    selected_text = ""
    selection_start = 0
    selection_end = 0

    while active:
        screen.fill(WHITE)
        title = BIG_FONT.render("Flashcards Text - Press any key to return", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 30))

        text_surface = FONT.render(content, True, BLACK)
        text_rect = text_surface.get_rect(topleft=(50, 100))

        # Draw selection highlight
        if selection_start != selection_end:
            selection_rect = pygame.Rect(text_rect.left + FONT.size(content[:selection_start])[0],
            text_rect.top + FONT.get_height() * (selection_start // 70),
            FONT.size(content[selection_start:selection_end])[0],
            FONT.get_height() * ((selection_end - selection_start) // 70 + 1))
            pygame.draw.rect(screen, (100, 100, 255), selection_rect, 2)

        draw_text_in_box(content, (50, 100, 700, 450), FONT, BLACK, scroll_offset)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                active = False
            elif event.type == pygame.MOUSEWHEEL:
                scroll_offset += -event.y * 10
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos
                char_index = (y - text_rect.top) // FONT.get_height() * 70 + (x - text_rect.left) // FONT.size(" ")[0]
                if char_index < len(content):
                    if event.button == 1:  
                        selection_start = char_index
                        selection_end = char_index
                    elif event.button == 3: 
                        selected_text = content[selection_start:selection_end]
                        selected_text_surface = FONT.render(selected_text, True, BLACK)
                        screen.blit(selected_text_surface, (100, 500))
                        pygame.display.flip()
                        pygame.time.wait(500)
                        selection_start = 0
                        selection_end = 0
            elif event.type == pygame.MOUSEMOTION:
                if event.buttons[0]:  
                    x, y = event.pos
                    char_index = (y - text_rect.top) // FONT.get_height() * 70 + (x - text_rect.left) // FONT.size(" ")[0]
                    if char_index < len(content):
                        selection_end = char_index
        clock.tick(FPS)


def save_flashcards_to_file(flashcards):
    pygame.event.clear()

    screen.fill(WHITE)
    title_surface = BIG_FONT.render("Save Flashcards as Text File", True, BLACK)
    screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 50))

    # Get existing .txt files
    txt_files = [f for f in os.listdir() if f.endswith(".txt")]

    if txt_files:
        # Show existing files
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            initialfile=txt_files,
            title="Save Flashcards as Text File"
        )
    else:
        # Only offer to create a new file
        file_path = filedialog.asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Text Files", "*.txt"), ("All Files", "*.*")],
            title="Create New Flashcard Text File"
        )

    if file_path:
        confirm = messagebox.askokcancel(
            "Confirm Save",
            f"This will save your flashcards to '{os.path.basename(file_path)}'.\nAre you sure you want to continue?"
        )
        if confirm:
            try:
                with open(file_path, "w", encoding="utf-8") as f:
                    for card in flashcards:
                        f.write(f"Front: {card.front}\nBack:  {card.back}\n\n")
                messagebox.showinfo("Success", "Flashcards saved successfully!")
            except Exception as e:
                messagebox.showerror("Error", f"An error occurred while saving:\n{e}")

    pygame.display.flip()
    clock.tick(FPS)


def save_flashcards_mode(flashcards):
    active = True
    while active:
        screen.fill(WHITE)
        title = BIG_FONT.render("Save Flashcards", True, BLACK)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 50))

        button_display = pygame.Rect(WIDTH // 2 - 150, 150, 300, 50)
        button_file = pygame.Rect(WIDTH // 2 - 150, 250, 300, 50)

        draw_button("Display for Copy/Paste", button_display, GRAY)
        draw_button("Save to File", button_file, GRAY)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONDOWN:
                pos = event.pos
                if button_display.collidepoint(pos):
                    display_flashcards_text(flashcards)
                    active = False  
                elif button_file.collidepoint(pos):
                    save_flashcards_to_file(flashcards)
                    active = False   
        clock.tick(FPS)

def main_menu():
   flashcards = []
   feedback_message = ""
   feedback_timer = 0
   while True:
       screen.fill(WHITE)
       title_surface = BIG_FONT.render("Flashcard App", True, BLACK)
       screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 30))
       title_surface = BIG_FONT.render("(Press Return When Entering Text or Numbers)", True, BLACK)
       screen.blit(title_surface, (WIDTH//2 - title_surface.get_width()//2, 75))

       # Display feedback message if exists
       if feedback_message:
           feedback_timer -= 1
           if feedback_timer <= 0:
               feedback_message = ""
           else:
               feedback_text = FONT.render(feedback_message, True, RED)
               screen.blit(feedback_text, (WIDTH//2 - feedback_text.get_width()//2, 80))

       button_list = [
           create_button("Enter/Delete Flashcards", 50, 150, 300, 50),
           create_button("Shuffle Flashcards", 450, 150, 300, 50),
           create_button("Reverse Flashcards", 50, 250, 300, 50),
           create_button("Track Progress", 450, 250, 300, 50),
           create_button("Test Yourself", 50, 350, 300, 50),
           create_button("Save Flashcards", 450, 350, 300, 50),
           create_button("Exit", 250, 450, 300, 50)
       ]
       draw_button_list(button_list)
       pygame.display.flip()
       for event in pygame.event.get():
           if event.type == pygame.QUIT:
               pygame.quit(); sys.exit()
           elif event.type == pygame.MOUSEBUTTONDOWN:
               pos = event.pos
               for button in button_list:
                   if button["rect"].collidepoint(pos):
                       if button["text"] == "Enter/Delete Flashcards":
                           flashcards = handle_button_click(button["rect"], None, enter_flashcards)
                       elif button["text"] == "Shuffle Flashcards":
                           flashcards = handle_button_click(button["rect"], flashcards, animate_shuffle)
                       elif button["text"] == "Reverse Flashcards":
                           flashcards = handle_button_click(button["rect"], flashcards, animate_reverse)
                       elif button["text"] == "Track Progress":
                           handle_button_click(button["rect"], flashcards, track_progress_mode)
                       elif button["text"] == "Test Yourself":
                           handle_button_click(button["rect"], flashcards, test_yourself_mode)
                       elif button["text"] == "Save Flashcards":
                           handle_button_click(button["rect"], flashcards, save_flashcards_mode)
                       elif button["text"] == "Exit":
                           pygame.quit(); sys.exit()
                       break
       clock.tick(FPS)

if __name__ == "__main__":
   main_menu()
