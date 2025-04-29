import pygame
import os
import re
import time
import tkinter as tk
from tkinter import filedialog
import random

pygame.init()

# Set up display
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Flashcards App")

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (200, 200, 200)

# Load student photos and names
# Modify the fetch_student_photos_and_names function to handle cases where the form_data folder is missing
def fetch_student_photos_and_names(photo_path, map_path):
    # fetch_student_photos_and_names(photos_folder_path, form_file_path)

    # Read the mapping of UIN to Name from the HTML file
    uin_to_name = {}
    with open(map_path, 'r', encoding='utf-8') as file:
        content = file.read()
        matches = re.findall(r"Name: (.*?)<br>UIN: (\d+)", content)
        for name, uin in matches:
            # Reformat "LastName, FirstName" to "FirstName LastName" with support for multi-word names
            if "," in name:
                parts = name.split(", ")
                last_name = parts[0]
                first_name = " ".join(parts[1:])  # Join all remaining parts as the first name
                name = f"{first_name} {last_name}"
            uin_to_name[uin] = name


    # Fetch student photos and map them to names
    students = []
    for file_name in os.listdir(photo_path):
        if file_name.endswith(('.png', '.jpg', '.jpeg')):  # Check for image files
            uin = os.path.splitext(file_name)[0]  # Use the file name (without extension) as the UIN
            name = uin_to_name.get(uin, "Unknown")  # Get the name from the mapping, default to "Unknown"
            # Ensure the correct photo path is used without overwriting the variable
            photo_full_path = os.path.join(photo_path, file_name)
            students.append({'name': name, 'photo_path': photo_full_path})
    return students

# Add a button for submitting the guess
button_font = pygame.font.Font(None, 36)
button_rect = pygame.Rect(350, 460, 100, 40)
button_text = button_font.render("Enter", True, BLACK)

# Adjust button positions for equal distribution
prev_button_rect = pygame.Rect(150, 520, 150, 40)  # Left-aligned
show_name_button_rect = pygame.Rect(325, 520, 150, 40)  # Centered
next_button_rect = pygame.Rect(500, 520, 150, 40)  # Right-aligned

# Add a button for choosing a different class
choose_class_button_rect = pygame.Rect(50, 20, 200, 40)
choose_class_button_text = button_font.render("Choose Class", True, BLACK)

# Variables for the form.htm file and photos folder
form_file_path = ""
photos_folder_path = ""

# Modify the display_error_message function to hide the correct name
show_correct_name = False  # Hide the correct name when showing an error

def display_error_message(message):
    global show_correct_name
    show_correct_name = False  # Ensure the correct name is hidden
    error_font = pygame.font.Font(None, 36)
    error_surface = error_font.render(message, True, (255, 0, 0))  # Red color for error
    error_rect = error_surface.get_rect(center=(screen.get_width() // 2, 100))  # Position where the correct name was
    screen.blit(error_surface, error_rect)

# Ensure update_current_student is called after loading the roster in choose_class
def choose_class():
    global form_file_path, photos_folder_path, students, current_student_index, message, total_students, correct_guesses

    # Open a file dialog to select the Student Photos_files folder
    root = tk.Tk()
    root.withdraw()  # Hide the root window
    folder_selected = filedialog.askdirectory(title="Select Student Photos_files Folder")

    if folder_selected:
        form_file_path = os.path.join(folder_selected, "form.htm")
        photos_folder_path = os.path.join(folder_selected, "form_data")

        if not os.path.exists(photos_folder_path):
            photos_folder_path = folder_selected  # Use the selected class folder if form_data is missing
            form_file_path = os.path.join(folder_selected, "saved_resource(1).html")  # Use saved_resource(1).html instead

        # Modify the choose_class function to allow reselecting the folder instead of exiting
        if not os.path.exists(form_file_path):
            message = "Error: No valid mapping file found. Please select a valid folder."
            return  # Indent the return statement to be part of the function

        # Load students
        students = fetch_student_photos_and_names(photos_folder_path, form_file_path)
        random.shuffle(students)  # Shuffle the students list
        current_student_index = 0

        # Reset scoreboard
        correct_guesses = 0
        total_students = len(students)

        # Update the current student after students are loaded
        if students:
            update_current_student()
        else:
            message = "No students found in the selected class."
    else:
        print("Error: No folder selected. Exiting program.")


# Track the current student index
current_student_index = 0

# Update the current student and photo
def update_current_student():
    global current_student, student_image
    current_student = students[current_student_index]
    student_image = pygame.image.load(current_student['photo_path'])
    student_image = pygame.transform.scale(student_image, (200, 200))

# Initialize the first student
# update_current_student()  # Ensure it is only called after choose_class()

font = pygame.font.Font(None, 36)
input_box = pygame.Rect(300, 400, 200, 40)
user_text = ""

# Update the check_guess function to accept the first name as a correct guess
def check_guess(user_guess, correct_name):
    user_guess = user_guess.strip().lower()
    correct_name = correct_name.strip().lower()

    # Split the correct name into first and last name
    correct_first_name = correct_name.split()[0]  # Get the first name

    # Check if the guess matches the full name or just the first name
    return user_guess == correct_name or user_guess == correct_first_name

# Update the score display
score_font = pygame.font.Font(None, 36)

def draw_score():
    score_text = score_font.render(f"Score: {correct_guesses}/{total_students}", True, BLACK)
    screen.blit(score_text, (600, 20))  # Position at the top right

# Main loop
running = True
message = ""
show_correct_name = False

# Add a blinking cursor to the input box
cursor_visible = True
last_cursor_toggle = time.time()
cursor_blink_interval = 0.5  # Cursor blinks every 0.5 seconds

# Define the text for the "Show Name" button
show_name_button_text = button_font.render("Show Name", True, BLACK)

# Define the text for the "Next Photo" button
next_button_text = button_font.render("Next Photo", True, BLACK)

# Define the text for the "Prev Photo" button
prev_button_text = button_font.render("Prev Photo", True, BLACK)

# Ensure students is initialized before calling update_current_student
students = []  # Initialize as an empty list to avoid NameError

# Move update_current_student() to after the class is selected
# This ensures students is populated before the function is called
root = tk.Tk()
root.withdraw()  # Hide the root window
folder_selected = False

if folder_selected:
    form_file_path = os.path.join(folder_selected, "form.htm")
    photos_folder_path = os.path.join(folder_selected, "form_data")

    if not os.path.exists(photos_folder_path):
        photos_folder_path = folder_selected  # Use the selected class folder if form_data is missing
        form_file_path = os.path.join(folder_selected, "saved_resource(1).html")  # Use saved_resource(1).html instead

    # Modify the choose_class function to allow reselecting the folder instead of exiting
    if not os.path.exists(form_file_path):
        message = "Error: No valid mapping file found. Please select a valid folder."
        display_error_message

    # Load students
    students = fetch_student_photos_and_names(photos_folder_path, form_file_path)
    current_student_index = 0

    # Reset scoreboard
    correct_guesses = 0
    total_students = len(students)

    # Update the current student after students are loaded
    update_current_student()
else:
    print("Error: No folder selected. Exiting program.")
    #exit()

# Initialize a sparse user interface without loading a roster or choosing a class
students = []  # Initialize as an empty list
current_student_index = 0
correct_guesses = 0
total_students = 0

# Remove the initial prompt to select a class
# The user can choose a class later using the "Choose Class" button

# Update the main loop to handle text input for the guess
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if choose_class_button_rect.collidepoint(event.pos):
                choose_class()
            elif students:
                # Hide the Correct or Incorrect messages when navigation or toggle buttons are clicked
                if prev_button_rect.collidepoint(event.pos):
                    current_student_index = (current_student_index - 1) % len(students)  # Loop to the last photo
                    update_current_student()
                    message = ""  # Clear the message
                elif next_button_rect.collidepoint(event.pos):
                    current_student_index = (current_student_index + 1) % len(students)  # Loop to the first photo
                    update_current_student()
                    message = ""  # Clear the message
                # Toggle the Show Name button text and functionality
                elif show_name_button_rect.collidepoint(event.pos):
                    show_correct_name = not show_correct_name  # Toggle the state
                    if show_correct_name:
                        show_name_button_text = button_font.render("Hide Name", True, BLACK)
                    else:
                        show_name_button_text = button_font.render("Show Name", True, BLACK)
                    message = ""  # Clear the message
                elif button_rect.collidepoint(event.pos):
                    # Increment the correct_guesses counter when the guess is correct
                    if check_guess(user_text, current_student['name']):
                        correct_guesses += 1  # Increment the score for a correct guess
                        message = "Correct!"
                    else:
                        message = "Incorrect!"
                    user_text = ""  # Clear the text box
        elif event.type == pygame.KEYDOWN:
            # Increment the correct_guesses counter when the Enter key is pressed
            if event.key == pygame.K_RETURN:
                if check_guess(user_text, current_student['name']):
                    correct_guesses += 1  # Increment the score for a correct guess
                    message = "Correct!"
                else:
                    message = "Incorrect!"
                user_text = ""  # Clear the text box
            elif event.key == pygame.K_BACKSPACE:
                user_text = user_text[:-1]  # Remove the last character
            else:
                user_text += event.unicode  # Add the typed character to the text box

    # Fill the screen with white
    screen.fill(WHITE)

    # Draw the Choose Class button
    pygame.draw.rect(screen, GRAY, choose_class_button_rect)
    screen.blit(choose_class_button_text, (choose_class_button_rect.x + 10, choose_class_button_rect.y + 5))
    pygame.draw.rect(screen, BLACK, choose_class_button_rect, 2)

    # Display additional elements if a class is loaded
    if students:
        # Display the student photo
        screen.blit(student_image, (300, 150))

        # Draw the input box
        pygame.draw.rect(screen, GRAY, input_box)
        text_surface = font.render(user_text, True, BLACK)
        screen.blit(text_surface, (input_box.x + 5, input_box.y + 5))
        pygame.draw.rect(screen, BLACK, input_box, 2)

        # Draw the Prev Photo button
        pygame.draw.rect(screen, GRAY, prev_button_rect)
        screen.blit(prev_button_text, (prev_button_rect.x + 10, prev_button_rect.y + 5))
        pygame.draw.rect(screen, BLACK, prev_button_rect, 2)

        # Draw the Show Name button
        pygame.draw.rect(screen, GRAY, show_name_button_rect)
        screen.blit(show_name_button_text, (show_name_button_rect.x + 10, show_name_button_rect.y + 5))
        pygame.draw.rect(screen, BLACK, show_name_button_rect, 2)

        # Draw the Next Photo button
        pygame.draw.rect(screen, GRAY, next_button_rect)
        screen.blit(next_button_text, (next_button_rect.x + 10, next_button_rect.y + 5))
        pygame.draw.rect(screen, BLACK, next_button_rect, 2)

        # Draw the Enter button
        pygame.draw.rect(screen, GRAY, button_rect)
        screen.blit(button_text, (button_rect.x + 10, button_rect.y + 5))
        pygame.draw.rect(screen, BLACK, button_rect, 2)

        # Display the score
        draw_score()

        # Display the correct name if the Show Name button is clicked
        if show_correct_name:
            correct_name_surface = font.render(f"{current_student['name']}", True, BLACK)
            correct_name_rect = correct_name_surface.get_rect(center=(screen.get_width() // 2, 100))
            screen.blit(correct_name_surface, correct_name_rect)

    # Display a message if no class is loaded
    else:
        # Update the message to break it into two lines
        no_class_message_line1 = font.render("No class loaded.", True, BLACK)
        no_class_message_line2 = font.render("Save Class Roster then choose the Student Photos_files folder.", True, BLACK)
        no_class_rect_line1 = no_class_message_line1.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 - 20))
        no_class_rect_line2 = no_class_message_line2.get_rect(center=(screen.get_width() // 2, screen.get_height() // 2 + 20))
        screen.blit(no_class_message_line1, no_class_rect_line1)
        screen.blit(no_class_message_line2, no_class_rect_line2)

    # Ensure the message is displayed on the screen
    if message:
        message_color = (0, 255, 0) if message == "Correct!" else (255, 0, 0)  # Green for correct, red for incorrect
        message_surface = font.render(message, True, message_color)
        message_rect = message_surface.get_rect(center=(screen.get_width() // 2, 580))
        screen.blit(message_surface, message_rect)

    # Ensure the blinking cursor is only displayed after a class has been loaded
    if students and time.time() - last_cursor_toggle > cursor_blink_interval:
        cursor_visible = not cursor_visible
        last_cursor_toggle = time.time()

    # Draw the blinking cursor only if a class is loaded
    if students and cursor_visible:
        # Ensure cursor_x is calculated only when students are loaded
        cursor_x = input_box.x + 5 + text_surface.get_width()  # Calculate the cursor position based on user text
        pygame.draw.line(screen, BLACK, (cursor_x, input_box.y + 5), (cursor_x, input_box.y + input_box.height - 5), 2)

    # Update the display
    pygame.display.flip()

# C:\Users\HP\AppData\Local\Programs\Python\Python313\Scripts\pyinstaller --onefile "C:\Users\HP\OneDrive - Florida Gulf Coast University\Apps\flashcards-app\main.py"

# Quit Pygame
pygame.quit()

