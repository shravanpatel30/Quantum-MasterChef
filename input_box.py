# import pygame
# import sys
#
# # pygame.init() will initialize all
# # imported module
# pygame.init()
#
# clock = pygame.time.Clock()
#
# # it will display on screen
# screen = pygame.display.set_mode([600, 500])
#
# width_textrect = 200
# height_textrect = 32
#
# def input_textbox(surface, pos):
#     base_font = pygame.font.Font(None, 32)
#     user_text = ''
#
#     # create rectangle
#     input_rect = pygame.Rect(pos[0], pos[1], width_textrect, height_textrect)
#
#     # color_active stores color(lightskyblue3) which gets active when input box is clicked by user
#     color_active = pygame.Color('white')
#
#     # color_passive store color(chartreuse4) which is color of input box.
#     color_passive = pygame.Color('grey60')
#     color = color_passive
#
#     active = False
#
#     while True:
#         for event in pygame.event.get():
#
#             # if user types QUIT then the screen will close
#             if event.type == pygame.QUIT:
#                 pygame.quit()
#                 sys.exit()
#
#             if event.type == pygame.MOUSEBUTTONDOWN:
#                 if input_rect.collidepoint(event.pos):
#                     active = True
#                 else:
#                     active = False
#
#             if event.type == pygame.KEYDOWN:
#                 if active:
#                     if event.key == pygame.K_RETURN:  # If Enter key is pressed
#                         user_text += '\n'  # Add a newline character
#                     elif event.key == pygame.K_BACKSPACE:  # If Backspace is pressed
#                         user_text = user_text[:-1]
#                     else:
#                         user_text += event.unicode
#
#
#         if active:
#             color = color_active
#         else:
#             color = color_passive
#
#         # draw rectangle and argument passed which should be on screen
#         pygame.draw.rect(surface, color, input_rect)
#
#         text_surface = base_font.render(user_text, True, 'black')
#
#         # render at position stated in arguments
#         surface.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))
#
#         # set width of textfield so that text cannot get outside of user's text input
#         input_rect.w = max(width_textrect, text_surface.get_width() + 10)
#         # draw a rectangle as a border
#         pygame.draw.rect(surface, color, input_rect, 2)
#
#         # display.flip() will update only a portion of the
#         # screen to updated, not full area
#         pygame.display.flip()
#
#         # clock.tick(60) means that for every second at most
#         # 60 frames should be passed.
#         clock.tick(60)


import pygame as pg
from sys import exit

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREY60 = (153, 153, 153)


def render_textbox(screen, x, y, width, height, font, textbox_color):
    clock = pg.time.Clock()
    fps = 60
    lines = ['']
    current = 0
    timer = 0
    cursor = False  # Initially, cursor is inactive
    cursor_index = 0
    character_limit = (width - 2 * 20) // font.size(' ')[0]  # Calculate character limit based on width and font
    border_color = GREY60
    active = False  # Initially, textbox is inactive

    textbox_surface = pg.Surface((width, height))
    textbox_surface.fill(textbox_color)
    textbox_rect = textbox_surface.get_rect(topleft=(x, y))

    def input_to_text(event):
        nonlocal lines, current, cursor_index
        if active:  # Only input characters when textbox is active
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_BACKSPACE:
                    # backspace erases the last char in the current line
                    if len(lines[current]) > 0:
                        lines[current] = lines[current][:-1]
                        cursor_index -= 1
                elif event.key == pg.K_RETURN:
                    # 'Enter' key jumps to the next line
                    lines.insert(current + 1, '')
                    current += 1
                elif event.key == pg.K_LEFT:
                    # Move cursor left
                    move_cursor_left()
                elif event.key == pg.K_RIGHT:
                    # Move cursor right
                    move_cursor_right()
                else:
                    # any other key
                    # get the letter as a unicode string char from the event
                    letter = event.unicode
                    if letter:  # Check if the event produced a Unicode character
                        if pg.key.get_pressed()[pg.K_LSHIFT]:
                            # if shift is pressed simultaneously, change the string to upper case
                            letter = letter.upper()
                        # add the char to the current line
                        new_line = lines[current][:cursor_index] + letter + lines[current][cursor_index:]
                        # Check if adding this character would exceed the textbox width
                        text_width, _ = font.size(new_line)
                        if text_width <= width - 2 * 20:  # Check if width of text fits in the textbox width
                            lines[current] = new_line
                            cursor_index += 1
                        # Check if text exceeds line width, then wrap text
                        else:
                            wrap_text()

    def move_cursor_left():
        nonlocal current, cursor_index
        if cursor_index > 0:
            cursor_index -= 1
        else:
            if current > 0:
                current -= 1
                cursor_index = len(lines[current])

    def move_cursor_right():
        nonlocal current, cursor_index
        if cursor_index < len(lines[current]):
            cursor_index += 1
        else:
            if current < len(lines) - 1:
                current += 1
                cursor_index = 0

    def wrap_text():
        nonlocal lines, current, cursor_index
        # Check if the current line exceeds the character limit
        if len(lines[current]) > character_limit:
            # Find the last space before the character limit
            last_space_index = lines[current][:character_limit].rfind(' ')
            if last_space_index != -1:  # If a space is found
                # Split the line at the last space
                first_part = lines[current][:last_space_index]
                second_part = lines[current][last_space_index + 1:]
            else:  # If no space is found, move the entire line to the new line
                first_part = lines[current][:character_limit]
                second_part = lines[current][character_limit:]
            # Assign the first part back to the current line
            lines[current] = first_part
            # Insert the second part into the next line
            lines.insert(current + 1, second_part)
            # Move to the next line
            current += 1
            cursor_index -= last_space_index + 1

    def events():
        nonlocal border_color, active
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                exit()
            elif event.type == pg.MOUSEBUTTONDOWN:
                if textbox_rect.collidepoint(event.pos):
                    active = True  # Activate textbox on click
                    border_color = BLACK
                else:
                    active = False  # Deactivate textbox if clicked outside
                    border_color = GREY60
            else:
                input_to_text(event)
        return True

    def update(dt):
        nonlocal timer, cursor
        timer += dt
        if timer >= 0.5:
            # toggle the cursor
            cursor = not cursor
            timer = 0

    def draw():
        nonlocal lines, current, cursor, border_color, active
        screen.blit(textbox_surface, textbox_rect.topleft)  # Blit the textbox surface onto the screen
        pg.draw.rect(screen, border_color, textbox_rect, 2)  # Draw textbox border
        if active:  # Draw cursor only when textbox is active
            spacing = 0
            indent_x = x + 20  # left margin
            indent_y = y + 20  # top margin
            line_space = 30  # pixels between the y position of each line
            for i, line in enumerate(lines):
                # loop through each line and display it
                txt_surf = font.render(line, True, BLACK)
                screen.blit(txt_surf, (indent_x, indent_y + spacing))
                if i == current and cursor:
                    cursor_x = indent_x + font.size(line[:cursor_index])[0]
                    cursor_y = indent_y + spacing
                    pg.draw.line(screen, BLACK, (cursor_x, cursor_y), (cursor_x, cursor_y + font.get_height()))
                spacing += line_space

        pg.display.update()

    running = True
    while running:
        delta_time = clock.tick(fps) / 1000.0
        running = events()
        update(delta_time)
        draw()
    return lines




# if __name__ == '__main__':
#     pg.init()
#     screen = pg.display.set_mode((800, 600))
#     font = pg.font.SysFont('Arial', 24)
#     textbox_lines = render_textbox(screen, 100, 100, 400, 200, font)
#     print(textbox_lines)
#     pg.quit()


