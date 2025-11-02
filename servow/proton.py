import curses
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv
from playsound import playsound
import pygame

from operationfn import (
    send_dispense_command,
    reset_states,
    get_questions_from_api,
    scroll_through_options,
    scroll_through_numbers,
    playsoundct,
)
from animatefn import (
    display_scrolling_text,
    fall_sugarservo,
    blink_candy,
    rise_sugarservo,
    cascading_wave_effect,
)

# ASCII Art
ascii_candy = r"""
                       ----'-..-'---
              \  "-.  /             \  .-"  /
               > -=.\/               \/.=- <
               > -='/\               /\'=- <
              /__.-'  \             /  '-.__\          
                       ----'-..-'---
"""
ascii_candyDispensing = r"""
                       ----'-..-'---
              \  "-.  /             \  .-"  /
               > -=.\/   DISPENSING!   \/.=- <
               > -='/\   /-/-/-/-/-    /\'=- <
              /__.-'  \             /  '-.__\          
                       ----'-..-'---
"""
ascii_sugarservo = r"""
 ______  __  __  ______  ______  ______       ______  ______  ______  __   ________    
/\  ___\/\ \/\ \/\  ___\/\  __ \/\  == \     /\  ___\/\  ___\/\  == \/\ \ / /\  __ \   
\ \___  \ \ \_\ \ \ \__ \ \  __ \ \  __<     \ \___  \ \  __\\ \  __<\ \ \'/\ \ \/\ \  
 \/\_____\ \_____\ \_____\ \_\ \_\ \_\ \_\    \/\_____\ \_____\ \_\ \_\ \__| \ \_____\ 
  \/_____/\/_____/\/_____/\/_/\/_/\/_/ /_/     \/_____/\/_____/\/_/ /_/\/_/   \/_____/ 
"""
ascii_stemclub = r"""
    _______.___________. _______ .___  ___.      ______  __       __    __  .______    __     _______.
    /       |           ||   ____||   \/   |     /      ||  |     |  |  |  | |   _  \  (_ )   /       |
    |   (----`---|  |----`|  |__   |  \  /  |    |  ,----'|  |     |  |  |  | |  |_)  |  |/   |   (----`
    \   \       |  |     |   __|  |  |\/|  |    |  |     |  |     |  |  |  | |   _  <         \   \    
    .----)   |      |  |     |  |____ |  |  |  |    |  `----.|  `----.|  `--'  | |  |_)  |    .----)   |   
    |_______/       |__|     |_______||__|  |__|     \______||_______| \______/  |______/     |_______/  
    """

# Load environment variables
load_dotenv(dotenv_path='keys.env')
api_key = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
candyJokePrompt = "say a custom dental goodbye for using the xylitol vending machine service and a congrats for getting the question correct. your response will be directly printed in the program"
model = genai.GenerativeModel("gemini-1.5-flash")

pygame.mixer.init()
playsound(r'servoSounds/correct.mp3') #check speaker functionality upon boot

def main(stdscr):
    curses.curs_set(0)  # Hide the cursor
    #colours
    curses.start_color()
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)   # white text on black
    cinstructional = curses.color_pair(1)
    while True:
        try:
            # Set timeout for key press detection (in milliseconds)
            key = 0
            stdscr.nodelay(True)  # Set non-blocking mode

            try:
                while key not in [curses.KEY_ENTER, 10, 13]:  # Wait for Enter key
                    # Display animations
                    cascading_wave_effect(stdscr, ascii_stemclub, 3)
                    if stdscr.getch() in [curses.KEY_ENTER, 10, 13]:  # Check for Enter during animation
                        break
                    blink_candy(stdscr, ascii_candy)
                    if stdscr.getch() in [curses.KEY_ENTER, 10, 13]:
                        break
                    rise_sugarservo(stdscr, ascii_sugarservo)
                    if stdscr.getch() in [curses.KEY_ENTER, 10, 13]:
                        break
            finally:
                stdscr.nodelay(False)  # Restore blocking mode

            # Display welcome message
            stdscr.clear()
            stdscr.addstr(0, 0, "Welcome to the Sugar Servo!")
            stdscr.refresh()
            time.sleep(1)

            # Subject menu
            playsoundct("menu.mp3")
            subjects = ["bio", "chem", "phys", "pure math", "mechanics", "statistics", "business", "econ", "acct", "compsci", "history trivia", "pop culture", "mechanics uestion "]
            stdscr.addstr(1, 0, "Select a subject:",cinstructional)
            stdscr.refresh()
            time.sleep(1)
            selected_subject_index = scroll_through_options(stdscr, subjects)
            selected_subject = subjects[selected_subject_index]

            # Select difficulty
            scale = 8
            stdscr.clear()
            stdscr.addstr(1, 0, f"Select difficulty from 1-{scale}:", cinstructional)
            difficulty = scroll_through_numbers(stdscr, scale)
            stdscr.addstr(4, 0, f"Difficulty selected {difficulty}")

            # Fetch questions from API
            questions = get_questions_from_api(selected_subject, difficulty, scale)
            if not questions:
                stdscr.addstr(4, 0, "Failed to fetch questions. Exiting.")
                stdscr.refresh()
                time.sleep(2)
                continue

            # Question loop
            question = questions["question"]
            options = questions["options"]
            correct_answer = questions["correct_answer"]

            # Prepare a list for dynamic navigation
            slides = [question] + [f"{key}: {value}" for key, value in options.items()]
            current_slide = 0

            while True:
                # Clear and refresh the screen
                stdscr.clear()
                
                # Display the current slide
                stdscr.addstr(0, 0, slides[current_slide], curses.A_BOLD if current_slide == 0 else curses.A_NORMAL)

                # Add a prompt for navigation or selection
                if current_slide == 0:
                    stdscr.addstr(8, 0, "Use arrow keys to navigate options. Press ENTER to select.")
                
                # Refresh the screen
                stdscr.refresh()

                # Get user input
                key = stdscr.getch()

                # Navigate slides
                if key == curses.KEY_DOWN:
                    playsoundct("scroll.mp3")
                    current_slide = (current_slide + 1) % len(slides)
                elif key == curses.KEY_UP:
                    playsoundct("scroll.mp3")
                    current_slide = (current_slide - 1) % len(slides)
                elif key == curses.KEY_ENTER or key in [10, 13]:
                    # Handle selection
                    if current_slide > 0:  # Only evaluate if an option is selected
                        selected_option = list(options.keys())[current_slide - 1]  # Map slide index to option key
                        if selected_option == correct_answer:
                            # Correct answer logic
                            playsoundct("correct.mp3")
                            stdscr.clear()
                            stdscr.addstr(4, 0, "Correct!", curses.A_BOLD | curses.A_UNDERLINE)
                            stdscr.addstr(5, 0, f"Explanation: {questions['explanation']}")
                            stdscr.addstr(12, 0, "[Press [ENTER] to continue]", cinstructional)
                            stdscr.refresh()
                            time.sleep(2)
                            key = stdscr.getch()
                            playsoundct("enter.mp3")
                            stdscr.clear()
                            stdscr.refresh()
                            dispenseStates = ["no","yes"]
                            stdscr.addstr(1, 0, "Dispense Candy?", curses.A_BOLD | curses.A_UNDERLINE)
                            stdscr.refresh()
                            dispenseindex = scroll_through_options(stdscr, dispenseStates)
                            dispense = dispenseStates[dispenseindex]
                            if dispense == "yes":
                                playsoundct("dispensing2.mp3")
                                playsoundct("dispensing.mp3")
                                send_dispense_command(stdscr)

                                stdscr.clear()
                                stdscr.refresh()
                                blink_candy(stdscr, ascii_candyDispensing, 10, 0.25)
                                #print dispensing status here for debug (serial comms)
                                joke = model.generate_content(candyJokePrompt)
                                print(joke.text)
                                stdscr.clear()
                                stdscr.addstr(3, 0, joke.text)
                                stdscr.refresh()
                                playsoundct("thankyou.mp3")
                                time.sleep(2)
                                stdscr.addstr(9, 0, "Thank you for using the SUGAR SERVO!",cinstructional)
                                stdscr.addstr(10, 0, "[press any key to continue]")
                                stdscr.refresh()
                                stdscr.getch()
                                playsoundct("enter.mp3")
                            else:
                                playsoundct("thankyou.mp3")
                                joke = model.generate_content(candyJokePrompt)
                                print(joke.text)
                                stdscr.clear()
                                stdscr.addstr(3, 0, joke.text)
                                stdscr.refresh()
                                time.sleep(2)
                                stdscr.addstr(9, 0, "Thank you for using the SUGAR SERVO!",cinstructional)
                                stdscr.addstr(10, 0, "[press any key to continue]")
                                stdscr.refresh()
                                stdscr.getch()
                                playsoundct("enter.mp3")
                            break
                        else:
                            # Incorrect answer logic
                            playsoundct("incorrect.mp3")
                            stdscr.clear()
                            stdscr.addstr(4, 0, "Incorrect!", curses.A_BOLD | curses.A_UNDERLINE)
                            stdscr.addstr(5, 0, f"Explanation: {questions['explanation']}")
                            stdscr.addstr(12, 0, "[press any key to continue]")
                            stdscr.refresh()
                            stdscr.getch()
                            playsoundct("enter.mp3")
                            break

            # After question loop, return to animations
            stdscr.clear()
            stdscr.refresh()

        except KeyboardInterrupt:
            break  # Graceful exit on Ctrl+C
        finally:
            reset_states()  # Cleanup on exit

if __name__ == "__main__":
    curses.wrapper(main)