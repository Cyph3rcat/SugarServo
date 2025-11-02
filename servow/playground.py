import pygame
from playsound import playsound
import time

# Initialize Pygame mixer
pygame.mixer.init()

def playsoundct(file):

    full_path = f"servoSounds/{file}"  # Directory where sound files are located
    
    # Load and play the sound
    sound = pygame.mixer.Sound(full_path)
    sound.play()

playsound("servoSounds/enter.mp3")
playsoundct("menu.mp3")
playsoundct("correct.mp3")

for i in range(30):
    print(f"Doing something else... {i}")
    time.sleep(1)