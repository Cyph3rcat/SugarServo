import curses
import time
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json
import re
from playsound import playsound
import pygame

def playsoundct(file):

    full_path = f"servoSounds/{file}"  # Directory where sound files are located
    
    # Load and play the sound
    sound = pygame.mixer.Sound(full_path)
    sound.play()

def send_dispense_command(stdscr):
    stdscr.addstr(0, 0, "DISPENSING")
    print("dispense called, pseudo serial communicated")

# Reset hardware states or UI
def reset_states():
    """
    Reinitialize hardware states and UI:
    - Hardware states are reset to ensure no unintended operations.
    - UI elements are reloaded for a clean user experience.
    """
    curses.endwin()  # Close curses UI

# Send AI prompt to Gemini API
def get_questions_from_api(subject, difficulty, scale):
    """
    Fetch questions from the Gemini API based on the selected subject.
    """
    load_dotenv(dotenv_path='keys.env')
    api_key = os.getenv("GEMINI_API_KEY")
    genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

    payload = f"""Generate one completely random multiple-choice question based on the subject {subject} with difficulty {difficulty} on a scale of 1-[{scale}]. 

                - Difficulty levels should follow this structure:
                1. The first few levels (1 to 3) should be IGCSE level questions.
                2. Middle levels should correspond to A Level material.
                3. The highest two levels should be at a Univer sity level, suitable for teachers and advanced learners.
                if it's not an academic subject, then ignore this

                - Randomly select a subtopic or area within {subject} for each question to increase diversity.
                - Use a variety of question types: 
                1. Theoretical understanding of core concepts.
                2. Problem-solving involving calculations.
                3. Real-world applications with contextual examples or historical/scientific relevance.
                - The type should be chosen randomly to ensure diverse styles.

                - Ensure the options:
                1. Are meaningfully different from one another.
                2. Include at least one incorrect option based on a common misconception or error in the field.
                3. Do not repeat similar phrasings across multiple options.

                - Add a brief explanation for the correct answer, covering both why it is correct and why the other options are wrong.

                Format the output in JSON as follows:
                {{
                    "question": "Insert question here",
                    "options": {{
                        "A": "Option A text",
                        "B": "Option B text",
                        "C": "Option C text",
                        "D": "Option D text"
                    }},
                    "correct_answer": "Insert correct option (A/B/C/D)",
                    "explanation": "Explanation on why it's the correct answer and why others are incorrect."
                }}

                **Reply only with the JSON object**. 
                - Do not include any additional text, comments, or formatting like `'''json`.
                - Start the output with open curly braces and end with close curly braces.
                """

    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(payload)

        # Extract the JSON string and remove leading/trailing whitespace
        json_string = response.text.strip() # Access text directly

        cleaned_response = re.search(r"\{.*\}", json_string, re.DOTALL)

        if cleaned_response:
            json_content = cleaned_response.group()  # Extract the matched JSON
            try:
                questions = parsed_json = json.loads(json_content)  # Parse JSON to check validity
                print(json.dumps(parsed_json, indent=4))  # Pretty print the JSON
                print("JSON successfully parsed")
                return questions
            except json.JSONDecodeError as e:
                print(f"JSON Decode Error: {e}")
                print(f"Raw Response: {json_string}") # Print raw response for debugging
            return None # Return None to indicate failure
        else:
            print("No valid JSON found.")
        
    except Exception as e:
        print(f"Error fetching questions: {e}")
        return None

# Scroll through options and get user choice
def scroll_through_options(stdscr, options):
    """
    Allows the user to scroll through multiple-choice options using arrow keys and select one with ENTER.
    """
    current_index = 0
    time.sleep(1)
    while True:
        # Display options
        stdscr.addstr(0, 0, "Use UP/DOWN keys to scroll and ENTER to select:")
        for i, option in enumerate(options):
            if i == current_index:
                stdscr.addstr(i + 2, 0, f"> {option}", curses.A_REVERSE)  # Highlight selected option
            else:
                stdscr.addstr(i + 2, 0, f"  {option}")
        stdscr.refresh()

        key = stdscr.getch() # record keypress

        # Handle key presses
        if key == curses.KEY_UP:
            playsoundct("scroll.mp3")
            current_index = (current_index - 1) % len(options)
        elif key == curses.KEY_DOWN:
            playsoundct("scroll.mp3")
            current_index = (current_index + 1) % len(options)
        elif key == 10:  # ENTER key
            playsoundct("enter.mp3")
            return current_index  # Return the selected 

def scroll_through_numbers(stdscr, scale):
    choice = 1  # Start at 1
    min_choice, max_choice = 1, scale  # Define the range of choices

    while True:
        # Clear the screen and display instructions
        stdscr.clear()
        stdscr.addstr(0, 0, "Use UP/DOWN keys to scroll and ENTER to select:")
        
        # Display the currently selected number
        stdscr.addstr(2, 2, f"Difficulty: {choice}")
        stdscr.refresh()

        # Get user input
        key = stdscr.getch()

        # Handle key presses
        if key == curses.KEY_UP:
            playsoundct("scroll.mp3")
            choice = min(max_choice, choice + 1)  # Increment but stay within bounds
        elif key == curses.KEY_DOWN:
            playsoundct("scroll.mp3")
            choice = max(min_choice, choice - 1)  # Decrement but stay within bounds
        elif key == 10:  # ENTER key
            playsoundct("enter.mp3")
            return choice  # Return the selected number 
