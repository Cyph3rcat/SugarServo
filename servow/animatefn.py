import curses
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv

def display_scrolling_text(stdscr, text, delay=0.025):
    lines = text.splitlines()
    max_line_width = max(len(line) for line in lines)
    num_lines = len(lines)

    # Calculate center of the screen for starting position
    start_x = (curses.COLS - max_line_width) // 2
    pad_height = num_lines
    pad_width = max_line_width + curses.COLS
    pad = curses.newpad(pad_height, pad_width)

    # Fill the pad with the text
    for i, line in enumerate(lines):
        pad.addstr(i, 0, line)

    scroll_pos = start_x
    for _ in range(curses.COLS + max_line_width):
        pad.refresh(0, scroll_pos, 0, 0, num_lines - 1, curses.COLS - 1)
        scroll_pos = (scroll_pos + 1) % (curses.COLS + max_line_width)
        time.sleep(delay)

def blink_candy(stdscr, candy, blink_times=5, delay=0.1):
    candy_lines = candy.splitlines()
    height, width = len(candy_lines), max(len(line) for line in candy_lines)
    start_y = (curses.LINES - height) // 2
    start_x = (curses.COLS - width) // 2

    # Define color pair for CANDY (Pink)
    curses.start_color()
    curses.init_pair(1, curses.COLOR_MAGENTA, curses.COLOR_BLACK)  # Pink (MAGENTA) text

    for _ in range(blink_times):
        stdscr.clear()
        stdscr.refresh()
        time.sleep(delay)
        for i, line in enumerate(candy_lines):
            stdscr.addstr(start_y + i, start_x, line, curses.color_pair(1))
        stdscr.refresh()
        time.sleep(delay)

def cascading_wave_effect(stdscr, ascii_text, duration):
    # Clear the screen
    stdscr.clear()

    # Split the ASCII art into lines
    lines = ascii_text.splitlines()
    max_width = max(len(line) for line in lines)

    # Compute screen dimensions
    screen_height, screen_width = stdscr.getmaxyx()
    start_y = (screen_height - len(lines)) // 2
    start_x = (screen_width - max_width) // 2

    # Animation loop with time limit
    start_time = time.time()
    try:
        while time.time() - start_time < duration:
            for step in range(max_width):
                if time.time() - start_time >= duration:
                    break

                # Clear the screen before drawing
                stdscr.clear()

                # Draw the ASCII art with offsets
                for line_idx, line in enumerate(lines):
                    for char_idx, char in enumerate(line):
                        if char.strip():  # Skip spaces for the wave effect
                            offset = int(5 * abs((char_idx - step) % max_width - max_width / 2) / max_width)
                            y = start_y + line_idx - offset
                            x = start_x + char_idx
                            if 0 <= y < screen_height and 0 <= x < screen_width:
                                stdscr.addch(y, x, char)

                # Refresh the screen
                stdscr.refresh()
                time.sleep(0.05)

    except KeyboardInterrupt:
        pass

def fall_sugarservo(stdscr, sugarservo, delay=0.1, pause_duration=1.5):
    sugarservo_lines = sugarservo.splitlines()
    height, width = len(sugarservo_lines), max(len(line) for line in sugarservo_lines)
    start_x = max((curses.COLS - width) // 2, 0)  # Ensure start_x is non-negative

    # Define color pair for SUGAR SERVO (Cyan)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Cyan text

    # Calculate the starting position of the screen
    start_y = -height  # Start above the visible area

    for offset in range(start_y, curses.LINES):
        stdscr.clear()

        # Display the sugarservo lines in cyan
        for i, line in enumerate(sugarservo_lines):
            if 0 <= offset + i < curses.LINES:  # Only draw within the screen boundaries
                stdscr.addstr(offset + i, start_x, line[:curses.COLS - start_x], curses.color_pair(2))  # Clip line to fit terminal width

        stdscr.refresh()

        # Pause if at the middle
        if offset == (curses.LINES - height) // 2:
            time.sleep(pause_duration)

        time.sleep(delay)

def rise_sugarservo(stdscr, sugarservo, delay=0.1, pause_duration=1.5):
    sugarservo_lines = sugarservo.splitlines()
    height, width = len(sugarservo_lines), max(len(line) for line in sugarservo_lines)
    start_x = max((curses.COLS - width) // 2, 0)  # Ensure start_x is non-negative

    # Define color pair for SUGAR SERVO (Cyan)
    curses.init_pair(2, curses.COLOR_CYAN, curses.COLOR_BLACK)  # Cyan text

    # Calculate the middle position of the screen
    middle_y = (curses.LINES - height) // 2

    for offset in range(curses.LINES, -height, -1):
        stdscr.clear()

        # Display the sugarservo lines in cyan
        for i, line in enumerate(sugarservo_lines):
            if 0 <= offset + i < curses.LINES:  # Only draw within the screen boundaries
                stdscr.addstr(offset + i, start_x, line[:curses.COLS - start_x], curses.color_pair(2))  # Clip line to fit terminal width

        stdscr.refresh()

        # Pause if at the middle
        if offset == middle_y:
            time.sleep(pause_duration)

        time.sleep(delay)

